import json, glob, os, statistics as st

root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "raw")
print("=== KẾT QUẢ THỰC NGHIỆM S1 TRÊN REDMI NOTE 13 (L256, W8, C80, 120Hz, n=2) ===")

def get_stats(policy, runs):
    data = []
    for r in runs:
        path = os.path.join(root, f"meta_{policy}_s1_note13_L256W8_{r}.json")
        if os.path.exists(path):
            with open(path) as f:
                m = json.load(f)
                fs, ts = m["frameSummary"], m["taskSummary"]
                data.append({
                    "missed": fs.get("missedPct", 0),
                    "jank": fs.get("dropPct", 0),
                    "gap95": fs.get("gapP95Ms", 0),
                    "critP95": ts.get("criticalLatencyP95Ms", 0),
                    "bgWait": ts.get("bgMaxWaitMs", 0),
                    "makespan": ts.get("makespanMs", 0),
                    "dropped": ts.get("dropped", 0),
                    "done": ts.get("done", 0) / max(1, ts.get("total", 1)) * 100,
                })
    return data

none_data = get_stats("none", [1, 2])
p0_data = get_stats("p0", [1, 2])
p1_data = get_stats("p1", [1, 2])
p2_data = get_stats("p2", [1, 2])
p3_data = get_stats("p3", [1, 2])

print(f"{'Chính sách':<14} | {'Missed%':<16} | {'Jank%':<16} | {'Gap95 (ms)':<14} | {'CritP95 (ms)':<22} | {'BgMaxWait (ms)':<20} | {'Done%'}")
print("-" * 125)
for name, d in [("NONE (Base)", none_data), ("P0 (Main)", p0_data), ("P1 (FIFO)", p1_data), ("P2 (Pri+Age)", p2_data), ("P3 (Chunk+Pri)", p3_data)]:
    missed_s = f"{st.median([x['missed'] for x in d]):.2f} [{min([x['missed'] for x in d]):.1f}-{max([x['missed'] for x in d]):.1f}]"
    jank_s = f"{st.median([x['jank'] for x in d]):.2f} [{min([x['jank'] for x in d]):.2f}-{max([x['jank'] for x in d]):.2f}]"
    gap_s = f"{st.median([x['gap95'] for x in d]):.2f} [{min([x['gap95'] for x in d]):.2f}-{max([x['gap95'] for x in d]):.2f}]"
    crit_s = f"{st.median([x['critP95'] for x in d]):.1f} [{min([x['critP95'] for x in d]):.0f}-{max([x['critP95'] for x in d]):.0f}]"
    bg_s = f"{st.median([x['bgWait'] for x in d]):.1f} [{min([x['bgWait'] for x in d]):.0f}-{max([x['bgWait'] for x in d]):.0f}]"
    done_s = f"{st.median([x['done'] for x in d]):.1f} [{min([x['done'] for x in d]):.1f}-{max([x['done'] for x in d]):.1f}]"
    print(f"{name:<14} | {missed_s:<16} | {jank_s:<16} | {gap_s:<14} | {crit_s:<22} | {bg_s:<20} | {done_s}")
