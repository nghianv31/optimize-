import glob, json, os, statistics as st

root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")

print("=== CHI TIẾT CÁC LƯỢT CHẠY P4 TRÊN KỊCH BẢN S2 ===")
print(f"{'Run':<12} {'Missed%':<10} {'Jank%':<10} {'Gap95(ms)':<12} {'CritP95(ms)':<14} {'BgMaxWait(ms)':<16} {'Makespan(ms)':<14} {'Dropped':<10} {'Done%':<8}")
print("-" * 105)

p4_runs = {}
for r in range(1, 7):
    path = os.path.join(root, f"meta_p4_s2_a04e_L32W8_{r}.json")
    if os.path.exists(path):
        with open(path) as f:
            m = json.load(f)
            fs, ts = m["frameSummary"], m["taskSummary"]
            row = {
                "missed": fs.get("missedPct", float("nan")),
                "jank": fs["dropPct"],
                "gap95": fs.get("gapP95Ms", float("nan")),
                "critP95": ts["criticalLatencyP95Ms"],
                "bgWait": ts["bgMaxWaitMs"],
                "makespan": ts["makespanMs"],
                "dropped": ts.get("dropped", 0),
                "done": ts["done"] / max(1, ts["total"]) * 100,
            }
            p4_runs[r] = row
            fix_note = " (Fixed)" if r >= 4 else " (Pre-fix)"
            print(f"{str(r)+fix_note:<12} {row['missed']:<10.2f} {row['jank']:<10.2f} {row['gap95']:<12.2f} {row['critP95']:<14.1f} {row['bgWait']:<16.1f} {row['makespan']:<14.0f} {row['dropped']:<10} {row['done']:<8.1f}")

print("\n=== SO SÁNH P1 vs P3 vs P4(Fixed) TRÊN KỊCH BẢN S2 (L32, W8) ===")
cols = ["missed", "jank", "gap95", "critP95", "bgWait", "makespan", "dropped", "done"]

def get_stats(policy, runs):
    data = []
    for r in runs:
        path = os.path.join(root, f"meta_{policy}_s2_a04e_L32W8_{r}.json")
        if os.path.exists(path):
            with open(path) as f:
                m = json.load(f)
                fs, ts = m["frameSummary"], m["taskSummary"]
                data.append({
                    "missed": fs.get("missedPct", float("nan")),
                    "jank": fs["dropPct"],
                    "gap95": fs.get("gapP95Ms", float("nan")),
                    "critP95": ts["criticalLatencyP95Ms"],
                    "bgWait": ts["bgMaxWaitMs"],
                    "makespan": ts["makespanMs"],
                    "dropped": ts.get("dropped", 0),
                    "done": ts["done"] / max(1, ts["total"]) * 100,
                })
    return data

p1_data = get_stats("p1", [1, 2, 3])
p3_data = get_stats("p3", [1, 2, 3])
p4_fix_data = get_stats("p4", [4, 5, 6])

print(f"{'Policy':<14} {'Missed%':<15} {'Jank%':<15} {'Gap95(ms)':<15} {'CritP95(ms)':<18} {'Makespan(ms)':<18} {'Done%':<15} {'Dropped':<12}")
print("-" * 120)

for name, d in [("P1 (FIFO)", p1_data), ("P3 (Pri+Chunk)", p3_data), ("P4 (AIMD+BP)", p4_fix_data)]:
    missed_s = f"{st.median([x['missed'] for x in d]):.2f} [{min([x['missed'] for x in d]):.1f}-{max([x['missed'] for x in d]):.1f}]"
    jank_s = f"{st.median([x['jank'] for x in d]):.2f} [{min([x['jank'] for x in d]):.1f}-{max([x['jank'] for x in d]):.1f}]"
    gap95_s = f"{st.median([x['gap95'] for x in d]):.2f} [{min([x['gap95'] for x in d]):.1f}-{max([x['gap95'] for x in d]):.1f}]"
    crit_s = f"{st.median([x['critP95'] for x in d]):.1f} [{min([x['critP95'] for x in d]):.0f}-{max([x['critP95'] for x in d]):.0f}]"
    make_s = f"{st.median([x['makespan'] for x in d]):.0f} [{min([x['makespan'] for x in d]):.0f}-{max([x['makespan'] for x in d]):.0f}]"
    done_s = f"{st.median([x['done'] for x in d]):.1f} [{min([x['done'] for x in d]):.1f}-{max([x['done'] for x in d]):.1f}]"
    drop_s = f"{int(st.median([x['dropped'] for x in d]))}"
    print(f"{name:<14} {missed_s:<15} {jank_s:<15} {gap95_s:<15} {crit_s:<18} {make_s:<18} {done_s:<15} {drop_s:<12}")
