"""Summarize s_image experiment runs across policies (none, p0..p4) on emulator-5554."""

import argparse
import glob
import json
import os
import statistics
from typing import Any

POLICY_ORDER = ["none", "p0", "p1", "p2", "p3", "p4"]

METRICS = [
    ("frames", "frameSummary", "frames", ".0f"),
    ("dropPct", "frameSummary", "dropPct", ".2f"),
    ("dropTotalPct", "frameSummary", "dropTotalPct", ".2f"),
    ("missedPct", "frameSummary", "missedPct", ".2f"),
    ("p95Ms", "frameSummary", "p95Ms", ".2f"),
    ("buildP95Ms", "frameSummary", "buildP95Ms", ".2f"),
    ("rasterP95Ms", "frameSummary", "rasterP95Ms", ".2f"),
    ("gapP95Ms", "frameSummary", "gapP95Ms", ".2f"),
    ("total", "taskSummary", "total", ".0f"),
    ("done", "taskSummary", "done", ".0f"),
    ("dropped", "taskSummary", "dropped", ".0f"),
    ("makespanMs", "taskSummary", "makespanMs", ".0f"),
    ("critP95Ms", "taskSummary", "criticalLatencyP95Ms", ".1f"),
    ("bgMaxWaitMs", "taskSummary", "bgMaxWaitMs", ".1f"),
]


def load_runs(raw_dir: str, pattern: str) -> list[dict[str, Any]]:
    """Load and parse matching metadata JSON files."""
    files = sorted(glob.glob(os.path.join(raw_dir, pattern)))
    rows: list[dict[str, Any]] = []
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = data.get("config", {})
        fs = data.get("frameSummary", {})
        ts = data.get("taskSummary", {})
        row: dict[str, Any] = {
            "file": os.path.basename(path),
            "policy": cfg.get("policy", ""),
            "run": cfg.get("run", 0),
            "tag": cfg.get("tag", ""),
            "load": cfg.get("load", 0),
            "workers": cfg.get("workers", 0),
            "chunkMs": cfg.get("chunkMs", 0),
        }
        for key, section, field, _fmt in METRICS:
            src = fs if section == "frameSummary" else ts
            row[key] = src.get(field)
        rows.append(row)
    return rows


def fmt_med_range(vals: list[float], fmt: str) -> str:
    """Format median [min-max] from a non-empty numeric list."""
    if not vals:
        return "N/A"
    med = statistics.median(vals)
    lo = min(vals)
    hi = max(vals)
    if len(vals) == 1:
        return f"{med:{fmt}}"
    return f"{med:{fmt}} [{lo:{fmt}}-{hi:{fmt}}]"


def compute_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate per-policy median, min, max for all metrics."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        grouped.setdefault(r["policy"], []).append(r)

    ordered = [p for p in POLICY_ORDER if p in grouped]
    for p in sorted(grouped):
        if p not in ordered:
            ordered.append(p)

    summary: list[dict[str, Any]] = []
    for p in ordered:
        p_rows = sorted(grouped[p], key=lambda x: x["run"])
        entry: dict[str, Any] = {"policy": p, "n": len(p_rows), "metrics": {}}
        for key, _sec, _field, _fmt in METRICS:
            vals = [float(r[key]) for r in p_rows if r[key] is not None]
            if vals:
                entry["metrics"][key] = {
                    "median": statistics.median(vals),
                    "min": min(vals),
                    "max": max(vals),
                    "values": vals,
                }
        summary.append(entry)
    return summary


def maybe_mann_whitney(rows: list[dict[str, Any]], ref_policy: str = "p1", target_policy: str = "p4") -> dict[str, Any]:
    """Compute Mann-Whitney U if scipy is available and samples >= 2."""
    try:
        from scipy.stats import mannwhitneyu
    except ImportError:
        return {"available": False}

    a_rows = [r for r in rows if r["policy"] == ref_policy]
    b_rows = [r for r in rows if r["policy"] == target_policy]
    if len(a_rows) < 2 or len(b_rows) < 2:
        return {"available": False, "reason": "insufficient_samples"}

    tests: dict[str, Any] = {}
    for key in ["dropPct", "missedPct", "rasterP95Ms", "p95Ms", "makespanMs", "critP95Ms", "bgMaxWaitMs"]:
        va = [float(r[key]) for r in a_rows if r[key] is not None]
        vb = [float(r[key]) for r in b_rows if r[key] is not None]
        if len(va) >= 2 and len(vb) >= 2:
            stat = mannwhitneyu(va, vb, alternative="two-sided")
            tests[key] = {"u": float(stat.statistic), "p": float(stat.pvalue)}
    return {"available": True, "ref": ref_policy, "target": target_policy, "tests": tests}


def print_report(rows: list[dict[str, Any]], summary: list[dict[str, Any]], mw: dict[str, Any]) -> None:
    """Print per-run raw table and aggregated Median [Min-Max] markdown table."""
    print(f"Loaded {len(rows)} run(s).")
    if not rows:
        return

    print("\n=== RAW RUNS ===")
    raw_hdr = (
        f"{'tag':<26} {'policy':<6} {'frames':>6} {'drop%':>7} {'dropTot%':>8} "
        f"{'miss%':>7} {'p95ms':>7} {'bld95':>7} {'rst95':>7} "
        f"{'done/tot':>10} {'mkspn':>7} {'crit95':>8} {'bgMax':>8}"
    )
    print(raw_hdr)
    print("-" * len(raw_hdr))
    for r in sorted(rows, key=lambda x: (POLICY_ORDER.index(x["policy"]) if x["policy"] in POLICY_ORDER else 99, x["run"])):
        tot = int(r["total"] or 0)
        done = int(r["done"] or 0)
        print(
            f"{r['tag']:<26} {r['policy']:<6} "
            f"{(r['frames'] or 0):>6.0f} {(r['dropPct'] or 0):>7.2f} {(r['dropTotalPct'] or 0):>8.2f} "
            f"{(r['missedPct'] or 0):>7.2f} {(r['p95Ms'] or 0):>7.2f} {(r['buildP95Ms'] or 0):>7.2f} "
            f"{(r['rasterP95Ms'] or 0):>7.2f} {f'{done}/{tot}':>10} "
            f"{(r['makespanMs'] or 0):>7.0f} {(r['critP95Ms'] or 0):>8.1f} {(r['bgMaxWaitMs'] or 0):>8.1f}"
        )

    print("\n=== AGGREGATED SUMMARY (Median [Min-Max]) ===")
    cols = ["frames", "dropPct", "missedPct", "p95Ms", "buildP95Ms", "rasterP95Ms", "makespanMs", "critP95Ms", "bgMaxWaitMs", "done"]
    fmt_map = {k: fmt for k, _s, _f, fmt in METRICS}
    print("| Policy | n | " + " | ".join(cols) + " |")
    print("|---|---:|" + "|".join(["---"] * len(cols)) + "|")
    for entry in summary:
        cells = []
        for c in cols:
            m = entry["metrics"].get(c)
            cells.append(fmt_med_range(m["values"], fmt_map[c]) if m else "N/A")
        print(f"| `{entry['policy']}` | {entry['n']} | " + " | ".join(cells) + " |")

    if mw.get("available"):
        print(f"\n=== Mann-Whitney U ({mw['ref']} vs {mw['target']}) ===")
        for k, res in mw["tests"].items():
            print(f"- {k}: U={res['u']:.1f}, p={res['p']:.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize s_image benchmark results.")
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--pattern", default="meta_*_s_image_emu_L16W4_*.json")
    parser.add_argument("--out-json", default="data/summary_s_image_emu.json")
    args = parser.parse_args()

    rows = load_runs(args.raw_dir, args.pattern)
    summary = compute_summary(rows)
    mw = maybe_mann_whitney(rows)
    print_report(rows, summary, mw)

    if rows:
        out_dir = os.path.dirname(args.out_json)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump({"runs": rows, "summary": summary, "mann_whitney": mw}, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Saved summary JSON to {args.out_json}")


if __name__ == "__main__":
    main()
