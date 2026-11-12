#!/usr/bin/env python3
"""Gom meta_*.json trong data/raw, in median [min-max] theo (policy, scenario, tag)."""
import glob, json, os, statistics as st, sys
from collections import defaultdict

root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
rows = defaultdict(list)
for f in sorted(glob.glob(os.path.join(root, "meta_*.json"))):
    m = json.load(open(f))
    c, fs, ts = m["config"], m["frameSummary"], m["taskSummary"]
    key = (c["policy"], c["scenario"], c.get("tag") or f"L{c['load']:g}W{c['workers']}")
    rows[key].append({
        "missed%": fs.get("missedPct", float("nan")), "gap95": fs.get("gapP95Ms", float("nan")),
        "jank%": fs["dropPct"], "critP95": ts["criticalLatencyP95Ms"], "bgWait": ts["bgMaxWaitMs"],
        "makespan": ts["makespanMs"], "done": ts["done"] / max(1, ts["total"]) * 100,
    })

cols = ["missed%", "gap95", "jank%", "critP95", "bgWait", "makespan", "done"]
print(f"{'policy':8}{'scn':5}{'tag':12}{'n':>3}  " + "  ".join(f"{c:>20}" for c in cols))
for k in sorted(rows):
    r = rows[k]
    cells = []
    for c in cols:
        v = [x[c] for x in r]
        cells.append(f"{st.median(v):8.1f} [{min(v):.0f}-{max(v):.0f}]".rjust(20))
    print(f"{k[0]:8}{k[1]:5}{k[2]:12}{len(r):>3}  " + "  ".join(cells))
