"""Summarize s1 and s2 runs on emulator-5554 with 80-image UI."""
import glob
import json
import os
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "..", "data", "raw")
if not os.path.isdir(RAW_DIR):
    RAW_DIR = os.path.join(ROOT, "data", "raw")


def summarize(pattern, name, policy_order):
    files = sorted(glob.glob(os.path.join(RAW_DIR, pattern)))
    if not files:
        print(f"No files for {name} ({pattern})")
        return {}

    grouped = {}
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        pol = d["config"]["policy"]
        fs = d.get("frameSummary", {})
        ts = d.get("taskSummary", {})
        grouped.setdefault(pol, []).append({
            "frames": fs.get("frames", 0),
            "dropPct": fs.get("dropPct", 0),
            "missedPct": fs.get("missedPct", 0),
            "p95Ms": fs.get("p95Ms", 0),
            "rasterP95Ms": fs.get("rasterP95Ms", 0),
            "makespanMs": ts.get("makespanMs", 0),
            "critP95Ms": ts.get("criticalLatencyP95Ms", 0),
            "bgMaxWaitMs": ts.get("bgMaxWaitMs", 0),
            "done": ts.get("done", 0),
            "total": ts.get("total", 0),
            "dropped": ts.get("dropped", 0),
        })

    print(f"\n=== SUMMARY: {name} ({len(files)} runs) ===")
    hdr = "| Policy | n | Frames | Missed% | Frame p95 | Raster p95 | Crit p95 | BG Wait | Makespan | Done/Total |"
    sep = "|---|---:|---|---|---|---|---|---|---|---|"
    print(hdr)
    print(sep)

    out = {}
    for pol in policy_order:
        if pol not in grouped:
            continue
        items = grouped[pol]
        n = len(items)

        def med(k):
            v = [float(x[k]) for x in items]
            m = statistics.median(v)
            lo, hi = min(v), max(v)
            if k in ["done", "total", "frames", "makespanMs", "dropped"]:
                return f"{m:.0f} [{lo:.0f}–{hi:.0f}]"
            elif k in ["critP95Ms", "bgMaxWaitMs"]:
                return f"{m:.1f} [{lo:.1f}–{hi:.1f}]"
            else:
                return f"{m:.2f} [{lo:.2f}–{hi:.2f}]"

        row = (
            f"| `{pol}` | {n} | {med('frames')} | {med('missedPct')}% | "
            f"{med('p95Ms')}ms | {med('rasterP95Ms')}ms | {med('critP95Ms')}ms | "
            f"{med('bgMaxWaitMs')}ms | {med('makespanMs')}ms | {med('done')} / {items[0]['total']} |"
        )
        print(row)
        out[pol] = {k: statistics.median([float(x[k]) for x in items]) for k in items[0]}
    return out


if __name__ == "__main__":
    s1_res = summarize("meta_*_s1_emu_L16W4_*.json", "S1 (Tải tĩnh bão hòa)", ["none", "p0", "p1", "p2", "p3"])
    s2_res = summarize("meta_*_s2_emu_L16W4_*.json", "S2 (Tải động bậc thang)", ["p1", "p3", "p4"])
    s_img_res = summarize("meta_*_s_image_emu_L16W4_*.json", "S_Image (80 ảnh JPEG)", ["none", "p0", "p1", "p2", "p3", "p4"])
