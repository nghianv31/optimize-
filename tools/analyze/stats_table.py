#!/usr/bin/env python3
"""
Thống kê Median, IQR, Min-Max và kiểm định phi tham số Mann-Whitney U
cho các kịch bản thực nghiệm S1 và S2 trên thiết bị Samsung Galaxy A04e.
"""

import json
import os
import glob
import numpy as np
from scipy import stats

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "raw")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "analyze")
os.makedirs(OUT_DIR, exist_ok=True)

def load_run(policy, scenario, tag, run_id):
    path = os.path.join(ROOT, f"meta_{policy}_{scenario}_a04e_{tag}_{run_id}.json")
    if not os.path.exists(path):
        # fallback without tag if named differently
        path = os.path.join(ROOT, f"meta_{policy}_{scenario}_a04e_{run_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        m = json.load(f)
    fs, ts = m["frameSummary"], m["taskSummary"]
    return {
        "policy": policy,
        "run": run_id,
        "missed_pct": fs.get("missedPct", float("nan")),
        "gap95_ms": fs.get("gapP95Ms", float("nan")),
        "jank_pct": fs.get("dropPct", float("nan")),
        "crit_p95_ms": ts.get("criticalLatencyP95Ms", float("nan")),
        "bg_wait_ms": ts.get("bgMaxWaitMs", float("nan")),
        "makespan_ms": ts.get("makespanMs", float("nan")),
        "dropped": ts.get("dropped", 0),
        "done_pct": ts.get("done", 0) / max(1, ts.get("total", 1)) * 100,
    }

def summarize_group(data_list):
    res = {}
    metrics = ["missed_pct", "gap95_ms", "jank_pct", "crit_p95_ms", "bg_wait_ms", "makespan_ms", "dropped", "done_pct"]
    for m in metrics:
        vals = [d[m] for d in data_list if not np.isnan(d[m])]
        if not vals:
            continue
        q25, q50, q75 = np.percentile(vals, [25, 50, 75])
        iqr = q75 - q25
        res[m] = {
            "median": q50,
            "q25": q25,
            "q75": q75,
            "iqr": iqr,
            "min": np.min(vals),
            "max": np.max(vals),
            "raw": vals
        }
    return res

def format_cell(s):
    if not s:
        return "N/A"
    return f"{s['median']:.1f} (IQR {s['iqr']:.1f}) [{s['min']:.0f}-{s['max']:.0f}]"

# -------------------------------------------------------------
# 1. PHÂN TÍCH S1 CHÍNH THỨC (L64, W8, C80, Runs 11-14)
# -------------------------------------------------------------
s1_configs = [
    ("none", [11, 12, 13, 14]),
    ("p0",   [11, 12, 13, 14]),
    ("p1",   [11, 12, 13, 14]),
    ("p2",   [11, 12, 13, 14]),
    ("p3",   [11, 12, 13, 14]),
]

s1_data = {}
for pol, runs in s1_configs:
    dlist = [load_run(pol, "s1", "L64W8", r) for r in runs]
    dlist = [x for x in dlist if x is not None]
    s1_data[pol] = summarize_group(dlist)

# -------------------------------------------------------------
# 2. PHÂN TÍCH S2 CHÍNH THỨC (L32, W8, C80, Staircase)
# -------------------------------------------------------------
s2_configs = [
    ("p1", [1, 2, 3]),
    ("p3", [1, 2, 3]),
    ("p4", [4, 5, 6]),  # Runs 4, 5, 6 sau khi cô lập Critical worker
]

s2_data = {}
for pol, runs in s2_configs:
    dlist = [load_run(pol, "s2", "L32W8", r) for r in runs]
    dlist = [x for x in dlist if x is not None]
    s2_data[pol] = summarize_group(dlist)

# -------------------------------------------------------------
# 3. KIỂM ĐỊNH MANN-WHITNEY U
# -------------------------------------------------------------
def mwu(group_a, group_b, metric, alternative='two-sided'):
    vals_a = group_a[metric]["raw"]
    vals_b = group_b[metric]["raw"]
    try:
        u_stat, p_val = stats.mannwhitneyu(vals_a, vals_b, alternative=alternative)
        return u_stat, p_val
    except Exception as e:
        return float("nan"), float("nan")

# Print S1 Table
print("=========================================================================================")
print("BẢNG 1: KẾT QUẢ THỰC NGHIỆM KỊCH BẢN S1 (L64, W8, C80, n=4) TRÊN SAMSUNG GALAXY A04e")
print("=========================================================================================")
header = f"{'Chính sách':<10} {'Missed%':<22} {'Jank%':<22} {'CritP95 (ms)':<25} {'BgMaxWait (ms)':<25} {'Done%':<15}"
print(header)
print("-" * 120)
for pol in ["none", "p0", "p1", "p2", "p3"]:
    d = s1_data[pol]
    m_str = format_cell(d.get("missed_pct"))
    j_str = format_cell(d.get("jank_pct"))
    c_str = format_cell(d.get("crit_p95_ms"))
    b_str = format_cell(d.get("bg_wait_ms"))
    d_str = format_cell(d.get("done_pct"))
    print(f"{pol.upper():<10} {m_str:<22} {j_str:<22} {c_str:<25} {b_str:<25} {d_str:<15}")

# Print S2 Table
print("\n=========================================================================================")
print("BẢNG 2: KẾT QUẢ THỰC NGHIỆM KỊCH BẢN S2 (L32, W8, C80, Staircase, n=3) TRÊN A04e")
print("=========================================================================================")
header2 = f"{'Chính sách':<12} {'Missed%':<22} {'Jank%':<22} {'CritP95 (ms)':<22} {'Makespan (ms)':<22} {'Dropped':<10}"
print(header2)
print("-" * 115)
for pol in ["p1", "p3", "p4"]:
    d = s2_data[pol]
    m_str = format_cell(d.get("missed_pct"))
    j_str = format_cell(d.get("jank_pct"))
    c_str = format_cell(d.get("crit_p95_ms"))
    mk_str = format_cell(d.get("makespan_ms"))
    dr_str = f"{int(d['dropped']['median'])}"
    name = "P4 (AIMD+BP)" if pol == "p4" else ("P3 (Chunk+Pri)" if pol == "p3" else "P1 (FIFO)")
    print(f"{name:<12} {m_str:<22} {j_str:<22} {c_str:<22} {mk_str:<22} {dr_str:<10}")

# Tests
print("\n=========================================================================================")
print("KIỂM ĐỊNH GIẢ THUYẾT THỐNG KÊ (Mann-Whitney U Test)")
print("=========================================================================================")
comparisons = [
    ("H1 (P0 vs P1 trên S1 - Frame Missed)", s1_data["p0"], s1_data["p1"], "missed_pct", "greater"),
    ("H3 (P1 vs P2 trên S1 - Critical Latency)", s1_data["p1"], s1_data["p2"], "crit_p95_ms", "greater"),
    ("H3 (P1 vs P3 trên S1 - Critical Latency)", s1_data["p1"], s1_data["p3"], "crit_p95_ms", "greater"),
    ("H3 (P1 vs P3 trên S1 - Frame Missed)", s1_data["p1"], s1_data["p3"], "missed_pct", "greater"),
    ("H4 (P1 vs P4 trên S2 - Critical Latency)", s2_data["p1"], s2_data["p4"], "crit_p95_ms", "greater"),
    ("H4 (P3 vs P4 trên S2 - Jank %)", s2_data["p3"], s2_data["p4"], "jank_pct", "greater"),
    ("H4 (P3 vs P4 trên S2 - Makespan)", s2_data["p3"], s2_data["p4"], "makespan_ms", "greater"),
]

test_records = []
for name, ga, gb, metric, alt in comparisons:
    u, p = mwu(ga, gb, metric, alternative=alt)
    med_a = ga[metric]['median']
    med_b = gb[metric]['median']
    sig = "p < 0.05 (*)" if p < 0.05 else f"p = {p:.3f}"
    print(f"{name:<45} | MedA={med_a:.1f} vs MedB={med_b:.1f} | U={u:.1f}, {sig}")
    test_records.append((name, med_a, med_b, u, p, sig))

# Save markdown report to data/analyze/stats_report.md
with open(os.path.join(OUT_DIR, "stats_report.md"), "w", encoding="utf-8") as f:
    f.write("# BÁO CÁO PHÂN TÍCH THỐNG KÊ THỰC NGHIỆM (S1 & S2)\n\n")
    f.write("Thiết bị đo: Samsung Galaxy A04e (MediaTek Helio P35, 8 nhân, 2GB RAM, Android 14).\n\n")
    f.write("## 1. Kịch bản S1 (Tải tĩnh bão hòa: L64, W8, C80, 4 lượt chạy mỗi chính sách)\n\n")
    f.write("| Chính sách | Missed Frame (%) | Jank Frame (%) | Critical Latency p95 (ms) | Background Max Wait (ms) | Tỷ lệ hoàn thành (%) |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
    for pol in ["none", "p0", "p1", "p2", "p3"]:
        d = s1_data[pol]
        f.write(f"| **{pol.upper()}** | {format_cell(d.get('missed_pct'))} | {format_cell(d.get('jank_pct'))} | {format_cell(d.get('crit_p95_ms'))} | {format_cell(d.get('bg_wait_ms'))} | {format_cell(d.get('done_pct'))} |\n")
    
    f.write("\n## 2. Kịch bản S2 (Tải tăng dần bậc thang: L32, W8, C80, 4 phase, 3 lượt chạy mỗi chính sách)\n\n")
    f.write("| Chính sách | Missed Frame (%) | Jank Frame (%) | Critical Latency p95 (ms) | Makespan (ms) | Background Dropped |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
    for pol in ["p1", "p3", "p4"]:
        d = s2_data[pol]
        name = "P4 (AIMD + Backpressure)" if pol == "p4" else ("P3 (Chunk + Priority)" if pol == "p3" else "P1 (FIFO)")
        f.write(f"| **{name}** | {format_cell(d.get('missed_pct'))} | {format_cell(d.get('jank_pct'))} | {format_cell(d.get('crit_p95_ms'))} | {format_cell(d.get('makespan_ms'))} | {int(d['dropped']['median'])} |\n")
    
    f.write("\n## 3. Kiểm định Giả thuyết Khoa học (Mann-Whitney U Test)\n\n")
    f.write("| Giả thuyết & Phép so sánh | Giá trị Median A | Giá trị Median B | Thống kê U | Mức ý nghĩa p | Kết luận |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
    for name, med_a, med_b, u, p, sig in test_records:
        ket_luan = "Chấp nhận giả thuyết (**Có ý nghĩa thống kê**)" if p <= 0.05 else "Chưa đủ ý nghĩa thống kê (do n nhỏ)"
        f.write(f"| {name} | {med_a:.1f} | {med_b:.1f} | {u:.1f} | {sig} | {ket_luan} |\n")

print(f"\n[OK] Đã lưu báo cáo thống kê vào {os.path.join(OUT_DIR, 'stats_report.md')}")
