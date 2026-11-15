#!/usr/bin/env python3
"""
Tạo 4 biểu đồ báo cáo khoa học chất lượng cao:
- Fig 1: Trade-off scatter: Frame Missed % vs Critical Latency (S1)
- Fig 2: S2 Comparison bar chart: P1 vs P3 vs P4 (Jank, CritLatency, Makespan)
- Fig 3: Frame time timeline: P0 vs P1 vs P3 vs P4 (0-60s)
- Fig 4: Ablation components: P1 -> P3c -> P3r -> P3 (Hiệu quả từng cơ chế)
"""

import os
import json
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "raw")
FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Cấu hình font & style matplotlib
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
    "font.family": "sans-serif",
})

# ==============================================================================
# FIGURE 1: Trade-off Scatter Plot (Frame Missed % vs Critical Latency p95)
# ==============================================================================
def plot_fig1():
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    
    policies = {
        "P0 (Main Isolate)": ("p0", "s1", "L64W8", [11, 12, 13, 14], "#e74c3c", "X", 100),
        "P1 (WorkerPool FIFO)": ("p1", "s1", "L64W8", [11, 12, 13, 14], "#e67e22", "s", 80),
        "P2 (Priority + Aging)": ("p2", "s1", "L64W8", [11, 12, 13, 14], "#f1c40f", "D", 80),
        "P3 (Priority + Chunking)": ("p3", "s1", "L64W8", [11, 12, 13, 14], "#2ecc71", "o", 100),
        "Baseline (No Workload)": ("none", "s1", "L64W8", [11, 12, 13, 14], "#3498db", "*", 120),
    }

    for label, (pol, scn, tag, runs, color, marker, size) in policies.items():
        x_vals, y_vals = [], []
        for r in runs:
            p = os.path.join(ROOT, f"meta_{pol}_{scn}_a04e_{tag}_{r}.json")
            if os.path.exists(p):
                m = json.load(open(p, encoding="utf-8"))
                missed = m["frameSummary"].get("missedPct", 0)
                crit = m["taskSummary"].get("criticalLatencyP95Ms", 0.1)
                x_vals.append(crit)
                y_vals.append(missed)
        if x_vals and y_vals:
            ax.scatter(x_vals, y_vals, color=color, marker=marker, s=size, label=label, alpha=0.85, edgecolors="black", linewidth=0.7)
            med_x, med_y = np.median(x_vals), np.median(y_vals)
            ax.annotate(label.split()[0], (med_x, med_y), textcoords="offset points", xytext=(8, 5), fontweight="bold", color=color)

    ax.set_xscale("symlog", linthresh=10)
    ax.set_xlabel("Critical Task Latency p95 (ms) [Log scale]")
    ax.set_ylabel("Frame Missed Rate (%)")
    ax.set_title("Kịch bản S1 (L64, W8, C80): Đánh đổi giữa Độ mượt UI & Độ trễ Critical")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", framealpha=0.9)
    
    # Khu vực tối ưu (sweet spot)
    ax.axhspan(0, 2, color="green", alpha=0.08, label="Vùng mượt lý tưởng (<2% missed)")
    ax.axvspan(0, 50, color="green", alpha=0.08, label="Vùng trễ lý tưởng (<50ms)")
    
    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "fig1_s1_tradeoff.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Saved {out_path}")

# ==============================================================================
# FIGURE 2: S2 Comparison (P1 vs P3 vs P4)
# ==============================================================================
def plot_fig2():
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), dpi=300)
    
    pols = ["P1 (FIFO)", "P3 (Chunk+Pri)", "P4 (AIMD+BP)"]
    colors = ["#e67e22", "#3498db", "#2ecc71"]
    
    # Data extraction
    missed_meds = [5.06, 0.69, 0.75]
    jank_meds   = [4.77, 24.83, 8.01]
    crit_meds   = [4744.0, 34.0, 28.0]
    make_meds   = [67.8, 77.7, 67.9]
    
    # Subplot A: UI Quality (Missed % & Jank %)
    x = np.arange(len(pols))
    width = 0.35
    axes[0].bar(x - width/2, missed_meds, width, label="Missed Frame %", color="#e74c3c", alpha=0.85)
    axes[0].bar(x + width/2, jank_meds, width, label="Jank Frame %", color="#f39c12", alpha=0.85)
    axes[0].set_ylabel("Tỷ lệ (%)")
    axes[0].set_title("(A) Độ mượt UI (Missed & Jank)")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(pols, rotation=15)
    axes[0].legend()
    axes[0].grid(axis="y", linestyle="--", alpha=0.5)

    # Subplot B: Critical Latency p95
    bars2 = axes[1].bar(pols, crit_meds, color=colors, alpha=0.85, edgecolor="black", width=0.5)
    axes[1].set_yscale("log")
    axes[1].set_ylabel("Độ trễ Critical p95 (ms) [Log]")
    axes[1].set_title("(B) Độ trễ tác vụ Critical")
    axes[1].grid(axis="y", which="both", linestyle="--", alpha=0.5)
    for bar in bars2:
        yval = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2.0, yval * 1.3, f"{yval:.0f} ms", ha="center", va="bottom", fontweight="bold")

    # Subplot C: Makespan
    bars3 = axes[2].bar(pols, make_meds, color=colors, alpha=0.85, edgecolor="black", width=0.5)
    axes[2].set_ylabel("Makespan (giây)")
    axes[2].set_title("(C) Thời gian hoàn thành kịch bản")
    axes[2].set_ylim(50, 85)
    axes[2].grid(axis="y", linestyle="--", alpha=0.5)
    for bar in bars3:
        yval = bar.get_height()
        axes[2].text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"{yval:.1f}s", ha="center", va="bottom", fontweight="bold")

    plt.suptitle("Kịch bản S2 (Tải bậc thang 0.25x -> 2.0x): So sánh P1 vs P3 vs P4", fontsize=14, fontweight="bold")
    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "fig2_s2_comparison.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Saved {out_path}")

# ==============================================================================
# FIGURE 3: Frame Duration Timeline (P0 vs P1 vs P3 vs P4)
# ==============================================================================
def plot_fig3():
    fig, axes = plt.subplots(4, 1, figsize=(12, 9), sharex=True, dpi=300)
    
    traces = [
        ("P0 (Main Isolate - S1)", "data/raw/frames_p0_s1_a04e_L64W8_14.csv", "#e74c3c"),
        ("P1 (FIFO Pool - S1)", "data/raw/frames_p1_s1_a04e_L64W8_14.csv", "#e67e22"),
        ("P3 (Chunk + Priority - S1)", "data/raw/frames_p3_s1_a04e_L64W8_14.csv", "#3498db"),
        ("P4 (AIMD + Backpressure - S2)", "data/raw/frames_p4_s2_a04e_L32W8_4.csv", "#2ecc71"),
    ]
    
    for ax, (title, csv_path, col) in zip(axes, traces):
        full_path = os.path.join(os.path.dirname(ROOT), "..", csv_path)
        if not os.path.exists(full_path):
            full_path = csv_path
        if os.path.exists(full_path):
            df = pd.read_csv(full_path)
            t_s = df["vsync_us"] / 1e6
            frame_ms = df[["build_us", "raster_us"]].max(axis=1) / 1000.0
            
            # Subsample for clear visualization
            ax.plot(t_s, frame_ms, color=col, linewidth=0.8, alpha=0.85, label="Frame Render Time")
            ax.axhline(16.67, color="red", linestyle="--", linewidth=1.0, alpha=0.7, label="Budget 16.7ms (60fps)")
            ax.set_ylim(0, 60)
            ax.set_ylabel("Frame (ms)")
            ax.set_title(title, fontweight="bold", loc="left", fontsize=11)
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend(loc="upper right", framealpha=0.8)

    axes[-1].set_xlabel("Thời gian thực nghiệm (giây)")
    plt.suptitle("Biểu đồ thời gian render frame (Timeline) giữa các kiến trúc lập lịch", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "fig3_timeline_frames.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Saved {out_path}")

# ==============================================================================
# FIGURE 4: Ablation Breakdown (P1 -> P3c -> P3r -> P3)
# ==============================================================================
def plot_fig4():
    fig, ax1 = plt.subplots(figsize=(8, 5), dpi=300)
    
    steps = ["P1 (Baseline)", "+ Chunking (P3c)", "+ Reserve (P3r)", "+ Yield (P3)"]
    missed_pct = [22.2, 0.8, 0.7, 0.7]
    crit_latency_s = [34.4, 44.8, 0.049, 0.035]  # in seconds
    
    x = np.arange(len(steps))
    width = 0.35
    
    color_missed = "#e74c3c"
    color_crit = "#2980b9"
    
    rects1 = ax1.bar(x - width/2, missed_pct, width, label="Missed Frame (%)", color=color_missed, alpha=0.85, edgecolor="black")
    ax1.set_ylabel("Tỷ lệ rớt Frame (%)", color=color_missed, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=color_missed)
    ax1.set_ylim(0, 30)
    
    ax2 = ax1.twinx()
    rects2 = ax2.bar(x + width/2, crit_latency_s, width, label="Critical Latency p95 (s)", color=color_crit, alpha=0.85, edgecolor="black")
    ax2.set_ylabel("Độ trễ Critical p95 (giây)", color=color_crit, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor=color_crit)
    ax2.set_yscale("log")
    ax2.set_ylim(0.01, 100)
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(steps, fontweight="bold")
    ax1.set_title("Ablation Study S1: Đóng góp của từng thành phần kiến trúc P3", fontsize=13, fontweight="bold")
    ax1.grid(axis="x", linestyle="--", alpha=0.5)
    
    # Ghi chú trực quan
    ax1.annotate("Chunking loại bỏ\nnghẽn frame", xy=(1 - width/2, 1), xytext=(1 - width/2, 10),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                 ha="center", fontsize=9, fontweight="bold")
    
    ax2.annotate("Worker Reserve\ngiảm 1000x độ trễ", xy=(2 + width/2, 0.06), xytext=(2 + width/2, 5),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                 ha="center", fontsize=9, fontweight="bold")
    
    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "fig4_ablation_s1.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Saved {out_path}")

# ==============================================================================
# FIGURE 5: Cross-Device Comparison (Galaxy A04e 60Hz vs Redmi Note 13 120Hz)
# ==============================================================================
def plot_fig5():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8), dpi=300)
    
    devices = ["Galaxy A04e (60Hz)", "Redmi Note 13 (120Hz)"]
    pols = ["P1 (FIFO)", "P3 (Chunk+Pri)", "P4 (AIMD+BP)"]
    
    # Subplot A: Critical Latency p95 (Log scale)
    # A04e: P1=4744, P3=34, P4=28
    # Note13: P1=33501, P3=29, P4=25
    x = np.arange(len(devices))
    width = 0.25
    
    crit_p1 = [4744.0, 33501.0]
    crit_p3 = [34.0, 29.0]
    crit_p4 = [28.0, 25.0]
    
    b1 = axes[0].bar(x - width, crit_p1, width, label="P1 (FIFO)", color="#e67e22", alpha=0.9, edgecolor="black")
    b2 = axes[0].bar(x, crit_p3, width, label="P3 (Chunk+Pri)", color="#3498db", alpha=0.9, edgecolor="black")
    b3 = axes[0].bar(x + width, crit_p4, width, label="P4 (AIMD+BP)", color="#2ecc71", alpha=0.9, edgecolor="black")
    
    axes[0].set_yscale("log")
    axes[0].set_ylabel("Critical Latency p95 (ms) [Log]")
    axes[0].set_title("(A) Độ trễ Tác vụ Critical", fontweight="bold")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(devices, fontweight="bold")
    axes[0].grid(axis="y", which="both", linestyle="--", alpha=0.5)
    axes[0].legend(loc="upper right", framealpha=0.9)
    
    for bar in b1:
        yval = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2.0, yval * 1.3, f"{yval/1000:.1f}s", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    for bar in b2 + b3:
        yval = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2.0, yval * 1.3, f"{yval:.0f}ms", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    # Subplot B: Missed Frame Rate (%)
    missed_p1 = [5.06, 33.51]
    missed_p3 = [0.69, 1.19]
    missed_p4 = [0.75, 1.22]
    
    axes[1].bar(x - width, missed_p1, width, label="P1 (FIFO)", color="#e67e22", alpha=0.9, edgecolor="black")
    axes[1].bar(x, missed_p3, width, label="P3 (Chunk+Pri)", color="#3498db", alpha=0.9, edgecolor="black")
    axes[1].bar(x + width, missed_p4, width, label="P4 (AIMD+BP)", color="#2ecc71", alpha=0.9, edgecolor="black")
    axes[1].set_ylabel("Tỷ lệ rớt Frame (%)")
    axes[1].set_title("(B) Tỷ lệ rớt Khung hình (Missed %)", fontweight="bold")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(devices, fontweight="bold")
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)
    axes[1].set_ylim(0, 40)
    
    # Subplot C: Makespan (s)
    make_p1 = [67.8, 91.7]
    make_p3 = [77.7, 91.6]
    make_p4 = [67.9, 61.0]
    
    axes[2].bar(x - width, make_p1, width, label="P1 (FIFO)", color="#e67e22", alpha=0.9, edgecolor="black")
    axes[2].bar(x, make_p3, width, label="P3 (Chunk+Pri)", color="#3498db", alpha=0.9, edgecolor="black")
    axes[2].bar(x + width, make_p4, width, label="P4 (AIMD+BP)", color="#2ecc71", alpha=0.9, edgecolor="black")
    axes[2].set_ylabel("Makespan (giây)")
    axes[2].set_title("(C) Tổng thời gian hoàn thành (Makespan)", fontweight="bold")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(devices, fontweight="bold")
    axes[2].grid(axis="y", linestyle="--", alpha=0.5)
    axes[2].set_ylim(40, 105)

    plt.suptitle("So sánh Liên Thiết bị trên Kịch bản S2: Samsung Galaxy A04e (60Hz) vs Redmi Note 13 (120Hz)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "fig5_cross_device_comparison.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Saved {out_path}")


def plot_fig6():
    """Fig 6: Real Image Workload (s_image) across none and P0-P4 on emulator-5554."""
    raw_dir = ROOT if os.path.basename(os.path.normpath(ROOT)) == "raw" else os.path.join(ROOT, "data", "raw")
    files = sorted(glob.glob(os.path.join(raw_dir, "meta_*_s_image_emu_L16W4_*.json")))
    if not files:
        fallback_raw = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "raw")
        files = sorted(glob.glob(os.path.join(fallback_raw, "meta_*_s_image_emu_L16W4_*.json")))
    if not files:
        print("[WARN] No s_image metadata files found for Fig 6.")
        return

    grouped = {}
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pol = data.get("config", {}).get("policy", "")
        fs = data.get("frameSummary", {})
        ts = data.get("taskSummary", {})
        grouped.setdefault(pol, []).append({
            "frames": float(fs.get("frames", 0)),
            "missedPct": float(fs.get("missedPct", 0)),
            "p95Ms": float(fs.get("p95Ms", 0)),
            "rasterP95Ms": float(fs.get("rasterP95Ms", 0)),
            "critP95Ms": float(ts.get("criticalLatencyP95Ms", 0)),
            "donePct": 100.0 * float(ts.get("done", 0)) / max(1.0, float(ts.get("total", 1))),
        })

    policies = [p for p in ["none", "p0", "p1", "p2", "p3", "p4"] if p in grouped]
    labels = [p.upper() if p != "none" else "NONE\n(UI only)" for p in policies]
    colors = {
        "none": "#64748b",
        "p0": "#dc2626",
        "p1": "#ea580c",
        "p2": "#ca8a04",
        "p3": "#0284c7",
        "p4": "#16a34a",
    }

    def stats(pol_list, key):
        meds, lo_err, hi_err = [], [], []
        for p in pol_list:
            vals = [r[key] for r in grouped[p]]
            med = float(np.median(vals))
            meds.append(med)
            lo_err.append(max(0.0, med - float(np.min(vals))))
            hi_err.append(max(0.0, float(np.max(vals)) - med))
        return np.array(meds), np.array([lo_err, hi_err])

    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.2), dpi=300)
    fig.suptitle(
        "Real Image I/O + JPEG Workload (s_image, 80 DSLR JPEGs, L16/W4, emulator-5554)",
        fontsize=13,
        fontweight="bold",
        y=1.02,
    )

    # Panel A: Frame P95 Total vs Raster P95 (CPU/GPU Contention)
    ax = axes[0]
    x = np.arange(len(policies))
    w = 0.36
    p95_med, p95_err = stats(policies, "p95Ms")
    rst_med, rst_err = stats(policies, "rasterP95Ms")
    ax.bar(x - w / 2, p95_med, width=w, yerr=p95_err, capsize=3, color="#3b82f6", label="Frame Total p95 (ms)", alpha=0.9)
    ax.bar(x + w / 2, rst_med, width=w, yerr=rst_err, capsize=3, color="#f97316", label="Raster p95 (ms)", alpha=0.9)
    ax.axhline(p95_med[0] if "none" in policies else 0, color="#64748b", linestyle="--", linewidth=1.0, alpha=0.7)
    for i, (tv, rv) in enumerate(zip(p95_med, rst_med)):
        ax.text(i - w / 2, tv + p95_err[1][i] + 5, f"{tv:.0f}", ha="center", va="bottom", fontsize=7.5, fontweight="bold")
        ax.text(i + w / 2, rv + rst_err[1][i] + 5, f"{rv:.0f}", ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylim(0, max(p95_med + p95_err[1]) * 1.18)
    ax.set_ylabel("Latency (ms, lower is better)", fontsize=9.5)
    ax.set_title("(A) Frame & Raster Contention (p95)", fontsize=10.5, fontweight="bold")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    ax.legend(fontsize=8, loc="upper right")

    # Panel B: Critical Task Latency P95 (log scale, excluding none)
    ax = axes[1]
    sched_pols = [p for p in policies if p != "none"]
    sched_labels = [p.upper() for p in sched_pols]
    crit_med, crit_err = stats(sched_pols, "critP95Ms")
    x2 = np.arange(len(sched_pols))
    bar_cols = [colors[p] for p in sched_pols]
    ax.bar(x2, crit_med, width=0.55, yerr=crit_err, capsize=3, color=bar_cols, alpha=0.9)
    ax.set_yscale("log")
    ax.set_ylim(20, max(crit_med + crit_err[1]) * 3.0)
    for i, cv in enumerate(crit_med):
        lbl = f"{cv/1000:.1f}s" if cv >= 1000 else f"{cv:.0f}ms"
        top = cv + crit_err[1][i]
        ax.text(i, top * 1.18, lbl, ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    ax.set_xticks(x2)
    ax.set_xticklabels(sched_labels, fontsize=9)
    ax.set_ylabel("Critical Latency p95 (ms, log scale)", fontsize=9.5)
    ax.set_title("(B) Critical Task Response (93x Faster P4 vs P1)", fontsize=10.5, fontweight="bold")
    ax.grid(axis="y", which="both", linestyle=":", alpha=0.45)

    # Panel C: Rendered Frames vs Task Completion %
    ax = axes[2]
    frm_med, frm_err = stats(policies, "frames")
    done_med, _ = stats(policies, "donePct")
    ax2 = ax.twinx()
    bars = ax.bar(x - 0.18, frm_med, width=0.35, yerr=frm_err, capsize=3, color=[colors[p] for p in policies], alpha=0.88, label="Rendered Frames (30s)")
    bars2 = ax2.bar(x + 0.18, done_med, width=0.35, color="#1e293b", alpha=0.35, hatch="//", edgecolor="#0f172a", label="Tasks Completed (%)")
    for i, fv in enumerate(frm_med):
        ax.text(i - 0.18, fv + frm_err[1][i] + 12, f"{fv:.0f}", ha="center", va="bottom", fontsize=7.5, fontweight="bold")
    for i, dv in enumerate(done_med):
        if policies[i] != "none":
            ax2.text(i + 0.18, dv + 2.2, f"{dv:.0f}%", ha="center", va="bottom", fontsize=7.5, color="#0f172a")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylim(0, max(frm_med + frm_err[1]) * 1.22)
    ax2.set_ylim(0, 118)
    ax.set_ylabel("Rendered Frames in 30s (higher is smoother)", fontsize=9)
    ax2.set_ylabel("Tasks Completed (%)", fontsize=9)
    ax.set_title("(C) UI Throughput vs Background Completion", fontsize=10.5, fontweight="bold")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=7.5, loc="upper left")

    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "fig6_s_image_real_workload.png")
    plt.savefig(out_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"[OK] Saved {out_path}")


if __name__ == "__main__":
    plot_fig1()
    plot_fig2()
    plot_fig3()
    plot_fig4()
    plot_fig5()
    plot_fig6()
    print("[ALL DONE] Tất cả 6 biểu đồ đã được tạo thành công trong thư mục figures/")
