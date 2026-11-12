#!/usr/bin/env python3
"""Chạy ma trận thực nghiệm trên máy Android thật, không cần build lại giữa các lần.

Quy trình mỗi lần: đẩy config.json -> mở app -> chờ meta_*.json -> adb pull -> dừng app -> nghỉ nguội.
Thứ tự các lần chạy được xáo trộn (seed cố định) để nhiễu nhiệt không thiên lệch một chính sách.

Ví dụ:
  python3 tools/run_matrix.py --build --policies p1,p2 --loads 8 --workers 4 --reps 3 --device a04e
"""
import argparse, csv, itertools, json, os, random, re, subprocess, sys, tempfile, time
from datetime import datetime

PKG = "com.example.optimize"
REMOTE = f"/sdcard/Android/data/{PKG}/files"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sh(cmd, check=True, **kw):
    return subprocess.run(cmd, check=check, capture_output=True, text=True, **kw).stdout


class Adb:
    def __init__(self, serial):
        self.base = ["adb"] + (["-s", serial] if serial else [])

    def __call__(self, *a, check=True):
        return sh(self.base + list(a), check=check)

    def shell(self, *a, check=True):
        return self("shell", *a, check=check)

    def temp_c(self):
        m = re.search(r"temperature:\s*(\d+)", self.shell("dumpsys", "battery"))
        return int(m.group(1)) / 10 if m else float("nan")

    def battery_level(self):
        m = re.search(r"level:\s*(\d+)", self.shell("dumpsys", "battery"))
        return int(m.group(1)) if m else -1


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serial", default=None)
    ap.add_argument("--device", default="dev", help="nhãn thiết bị trong tên file")
    ap.add_argument("--scenario", default="s1")
    ap.add_argument("--policies", default="p1,p2")
    ap.add_argument("--loads", default="4")
    ap.add_argument("--workers", default="4")
    ap.add_argument("--chunks", default="80")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--first-run", type=int, default=1)
    ap.add_argument("--duration", type=int, default=60)
    ap.add_argument("--seed", type=int, default=42, help="seed của kịch bản tác vụ")
    ap.add_argument("--shuffle-seed", type=int, default=1)
    ap.add_argument("--cool-s", type=int, default=60, help="nghỉ tối thiểu giữa các lần")
    ap.add_argument("--max-temp", type=float, default=0, help="chờ pin <= nhiệt này (°C); 0 = bỏ qua")
    ap.add_argument("--extra", default="{}", help='JSON gộp vào config, vd {"yieldMs":16}')
    ap.add_argument("--tag-suffix", default="", help="thêm vào tag, vd Y16")
    ap.add_argument("--build", action="store_true", help="build + cài APK profile trước khi chạy")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "raw"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    grid = list(itertools.product(a.policies.split(","), a.loads.split(","), a.workers.split(","), a.chunks.split(",")))
    jobs = [(p, float(l), int(w), int(c), rep) for (p, l, w, c) in grid for rep in range(a.first_run, a.first_run + a.reps)]
    random.Random(a.shuffle_seed).shuffle(jobs)
    log(f"{len(jobs)} lần chạy (đã xáo trộn): " + ", ".join(f"{p}/L{l:g}/W{w}/r{r}" for p, l, w, c, r in jobs))
    if a.dry_run:
        return

    os.makedirs(a.out, exist_ok=True)
    adb = Adb(a.serial)
    if a.build:
        log("flutter build apk --profile ...")
        subprocess.run(["flutter", "build", "apk", "--profile"], cwd=ROOT, check=True)
        adb("install", "-r", os.path.join(ROOT, "build/app/outputs/flutter-apk/app-profile.apk"))
    adb.shell("mkdir", "-p", REMOTE)

    manifest = os.path.join(os.path.dirname(a.out), "manifest.csv")
    new = not os.path.exists(manifest)
    mf = open(manifest, "a", newline="")
    w = csv.writer(mf)
    if new:
        w.writerow(["name", "policy", "scenario", "load", "workers", "chunkMs", "run", "order", "temp_start_c", "battery_start", "started_at"])

    try:
        for i, (pol, load, wk, ck, rep) in enumerate(jobs, 1):
            tag = f"L{load:g}W{wk}" + (f"C{ck}" if len(a.chunks.split(",")) > 1 or ck != 80 else "")
            cfg = dict(policy=pol, scenario=a.scenario, device=a.device, run=rep, seed=a.seed, workers=wk,
                       chunkMs=ck, load=load, durationS=a.duration, tag=tag + a.tag_suffix)
            cfg.update(json.loads(a.extra))
            tag = cfg["tag"]
            name = f"{pol}_{a.scenario}_{a.device}_{tag}_{rep}"
            t0 = adb.temp_c()
            log(f"({i}/{len(jobs)}) {name}  temp={t0}C battery={adb.battery_level()}%")
            w.writerow([name, pol, a.scenario, load, wk, ck, rep, i, t0, adb.battery_level(), datetime.now().isoformat()])
            mf.flush()

            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
                json.dump(cfg, f)
            adb("push", f.name, f"{REMOTE}/config.json")
            os.unlink(f.name)

            adb.shell("am", "force-stop", PKG)
            adb.shell("input", "keyevent", "KEYCODE_WAKEUP", check=False)
            adb.shell("am", "start", "-n", f"{PKG}/.MainActivity")

            meta = f"{REMOTE}/meta_{name}.json"
            timeout = 10 + 10 + a.duration + 30 + 60
            t_start = time.time()
            while time.time() - t_start < timeout:
                time.sleep(5)
                if "No such file" not in adb.shell("ls", meta, check=False) and meta.split("/")[-1] in adb.shell("ls", REMOTE, check=False):
                    break
            else:
                log(f"!! TIMEOUT {name} (app có thể bị kill hoặc màn hình khóa)")
                adb.shell("am", "force-stop", PKG)
                continue
            for pre in ("frames", "tasks", "meta"):
                ext = "json" if pre == "meta" else "csv"
                adb("pull", f"{REMOTE}/{pre}_{name}.{ext}", a.out)
            adb.shell("am", "force-stop", PKG)
            log(f"   xong {name} ({time.time() - t_start:.0f}s)")

            if i < len(jobs):
                time.sleep(a.cool_s)
                while a.max_temp and adb.temp_c() > a.max_temp:
                    log(f"   chờ nguội: {adb.temp_c()}C > {a.max_temp}C")
                    time.sleep(20)
    finally:
        adb.shell("rm", "-f", f"{REMOTE}/config.json", check=False)  # tránh ghi đè lần flutter run sau
        mf.close()
        log("đã xóa config.json trên máy")
    log("HOÀN TẤT. Tóm tắt: python3 tools/summarize.py")


if __name__ == "__main__":
    main()
