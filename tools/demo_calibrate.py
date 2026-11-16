#!/usr/bin/env python3
"""Chạy kịch bản demo 60 s tự động cho từng chính sách trên máy thật và in bảng kết quả.
Dùng để hiệu chỉnh các pha trong lib/workload/demo_scenario.dart (không cần chạm máy).

  python3 tools/demo_calibrate.py --serial R83WB1145QD --policies p0,p1,p2,p3,p4 [--build]
"""
import argparse, json, os, subprocess, tempfile, time

PKG = "com.example.optimize"
REMOTE = f"/sdcard/Android/data/{PKG}/files"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serial", default=None)
    ap.add_argument("--policies", default="p0,p1,p2,p3,p4")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--cool-s", type=int, default=45)
    a = ap.parse_args()
    adb = ["adb"] + (["-s", a.serial] if a.serial else [])

    def run(*args, check=True):
        return subprocess.run(adb + list(args), capture_output=True, text=True, check=check).stdout

    if a.build:
        subprocess.run(["flutter", "build", "apk", "--profile"], cwd=ROOT, check=True)
        run("install", "-r", os.path.join(ROOT, "build/app/outputs/flutter-apk/app-profile.apk"))
    run("shell", "mkdir", "-p", REMOTE)
    results = []
    try:
        for pol in a.policies.split(","):
            run("shell", "rm", "-f", f"{REMOTE}/demo_{pol}.json", check=False)
            cfg = dict(policy=pol, scenario="demo", workers=a.workers, chunkMs=80, durationS=60)
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
                json.dump(cfg, f)
            run("push", f.name, f"{REMOTE}/config.json")
            os.unlink(f.name)
            run("shell", "am", "force-stop", PKG)
            run("shell", "input", "keyevent", "KEYCODE_WAKEUP", check=False)
            run("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
            t0 = time.time()
            ok = False
            while time.time() - t0 < 140:
                time.sleep(5)
                if f"demo_{pol}.json" in run("shell", "ls", REMOTE, check=False):
                    ok = True
                    break
            if ok:
                out = run("shell", "cat", f"{REMOTE}/demo_{pol}.json")
                results.append(json.loads(out))
                print(out.strip(), flush=True)
            else:
                print(f"!! TIMEOUT {pol}", flush=True)
            run("shell", "am", "force-stop", PKG)
            time.sleep(a.cool_s)
    finally:
        run("shell", "rm", "-f", f"{REMOTE}/config.json", check=False)
    print(f"{'pol':4}{'missed%':>9}{'crit95ms':>10}{'done%':>8}{'drop':>7}{'peakC':>7}{'thr_s':>7}")
    for r in results:
        print(f"{r['policy']:4}{r['missedPct']:9.1f}{r['critP95Ms']:10d}{r['donePct']:8.1f}{r['dropped']:7d}{r['peakTempC']:7.1f}{r['throttledS']:7.1f}")


if __name__ == "__main__":
    main()
