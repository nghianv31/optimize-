# Flutter Task Scheduling & Frame Optimization Framework (P0 – P4)

Nghiên cứu và hiện thực hóa khung lập lịch tác vụ thông minh thích ứng theo thời gian dựng frame (Frame-Aware & Adaptive Scheduling) trên các thiết bị di động cấu hình yếu (Low-end Android devices).

---

## 1. Kiến trúc & Các Chính sách Lập lịch

| Chính sách | Tên gọi | Mô tả cơ chế | Mục tiêu tối ưu |
| :--- | :--- | :--- | :--- |
| **NONE** | Baseline | Ứng dụng chạy hoạt ảnh UI, không có tác vụ nền | Đo trần hiệu năng phần cứng lý tưởng |
| **P0** | Main Isolate | Chạy toàn bộ tác vụ nền trực tiếp trên Main Isolate | Bằng chứng nghẽn UI (UI freeze) |
| **P1** | WorkerPool FIFO | Phân bổ tác vụ ra Pool $N$ Isolate nền theo thứ tự FIFO | Giải phóng Main Isolate |
| **P2** | Priority + Aging | Hàng đợi 3 mức ưu tiên (`Critical > Visible > Background`) + Aging | Giảm độ trễ cho tác vụ tương tác người dùng |
| **P3** | Chunking + Yield | Chia nhỏ tác vụ thành các chunk ~80ms, chừa 1 worker reserve, nhường frame khi UI bận | Bảo vệ 60fps mượt mà, triệt tiêu nghẽn đầu hàng |
| **P4** | AIMD + Backpressure | Thuật toán AIMD co/giãn worker động theo nhịp frame + Mode Machine + Load Shedding | Chống quá nhiệt, bảo vệ thiết bị yếu khi tải bùng nổ |

---

## 2. Cấu trúc Dự án

```text
optimize-/
├── lib/
│   ├── config/              # Cấu hình RunConfig (policy, scenario, load, workers, chunkMs)
│   ├── metrics/             # Thu thập frame timing, stopwatch, xuất CSV
│   ├── scheduler/           # Bộ lập lịch:
│   │   ├── scheduler.dart   # Factory & điều phối các chính sách P0-P4
│   │   ├── worker_pool.dart # Quản lý pool Isolate nền
│   │   ├── aimd.dart        # Thuật toán AIMD co giãn worker động (+1 / *0.5)
│   │   ├── mode_machine.dart# Máy trạng thái suy giảm Normal/Conserve/Critical + Hysteresis
│   │   ├── signals.dart     # Đọc tín hiệu nhịp frame & pin/nhiệt độ phần cứng
│   │   └── task.dart        # Định nghĩa tác vụ, độ ưu tiên, trạng thái chunk
│   ├── workload/            # Sinh tải tổng hợp (Synthetic CPU Burner) & kịch bản S1/S2
│   └── run_controller.dart  # Bộ điều khiển vòng đời đo tự động (settle -> warmup -> run -> save)
├── tools/
│   ├── run_matrix.py        # Tự động hóa đo lường qua ADB (không cần rebuild APK)
│   ├── summarize.py         # Tổng hợp nhanh kết quả thực nghiệm từ các file meta
│   └── analyze/             # Phân tích thống kê & kiểm định giả thuyết:
│       ├── stats_table.py   # Tính Median, IQR, Min-Max & kiểm định Mann-Whitney U
│       └── plot_figures.py  # Vẽ 4 biểu đồ khoa học chất lượng cao (300 DPI)
├── figures/                 # Chứa các biểu đồ xuất bản (PNG)
├── data/
│   ├── raw/                 # Dữ liệu đo thô từ thiết bị (frames_*.csv, tasks_*.csv, meta_*.json)
│   ├── manifest.csv         # Nhật ký toàn bộ các lượt chạy thực nghiệm
│   └── analyze/             # Báo cáo thống kê chi tiết (stats_report.md)
└── test/                    # Unit tests & Benchmark kiểm tra overhead
```

---

## 3. Hướng dẫn Chạy Thực nghiệm

### 3.1. Build & Cài đặt APK Profile Mode
Ứng dụng bắt buộc phải được biên dịch ở chế độ **Profile** để đo lường chính xác hiệu năng AOT và độ trễ frame:

```bash
flutter build apk --profile
adb install -r build/app/outputs/flutter-apk/app-profile.apk
```

### 3.2. Chạy Ma trận Thực nghiệm Tự động (Không Rebuild)
Khung đo hỗ trợ truyền cấu hình qua file `config.json` đẩy trực tiếp vào `/data/local/tmp/` trên thiết bị:

```bash
# Chạy kịch bản S1 (Tải bão hòa L64, W8, C80) cho P1, P2, P3:
python tools/run_matrix.py --scenario s1 --policies p1 p2 p3 --loads 64 --workers 8 --chunks 80 --reps 4 --device a04e

# Chạy kịch bản S2 (Tải bậc thang tăng dần) cho P4:
python tools/run_matrix.py --scenario s2 --policies p4 --loads 32 --workers 8 --chunks 80 --reps 3 --device a04e
```

---

## 4. Phân tích Số liệu & Xuất Biểu đồ

### 4.1. Tổng hợp Thống kê & Kiểm định Mann-Whitney U
Chạy script phân tích để tính toán Median, IQR và kiểm định giả thuyết $p$-value:

```bash
python tools/analyze/stats_table.py
```
Kết quả được xuất tại `data/analyze/stats_report.md`.

### 4.2. Tạo Biểu đồ Khoa học
Chạy script để vẽ 4 biểu đồ khoa học lưu vào thư mục `figures/`:

```bash
python tools/analyze/plot_figures.py
```

- **`fig1_s1_tradeoff.png`**: Scatter plot đánh đổi giữa Tỷ lệ rớt Frame và Độ trễ Critical (S1).
- **`fig2_s2_comparison.png`**: Biểu đồ so sánh P1 vs P3 vs P4 trên kịch bản tải tăng dần (S2).
- **`fig3_timeline_frames.png`**: Biểu đồ chuỗi thời gian (Timeline) thể hiện thời gian render frame (0–60s).
- **`fig4_ablation_s1.png`**: Phân rã đóng góp của từng thành phần kiến trúc (`Chunking`, `Worker Reserve`, `Yielding`).

---

## 5. Kết quả Thực nghiệm Nổi bật (Trên Samsung Galaxy A04e)

- **H1 (Nghẽn Main Isolate):** $P_0$ làm rớt **90.8%** frame (tê liệt giao diện). Chuyển sang WorkerPool ($P_1$) lập tức hồi phục khả năng dựng hình ($p = 0.014$).
- **H3 (Độ trễ Critical & Frame Missed):** Phối hợp Chunking + Worker Reserve ở $P_3$ giúp giảm tỷ lệ rớt frame về **0.8%** (ngang baseline `none`), và hạ độ trễ critical từ **35.4 giây (P1) xuống chỉ 31.0 ms** (giảm >1.100 lần, $p = 0.014$).
- **H4 (AIMD & Backpressure trên máy yếu):** Trên kịch bản tải tăng đột biến $S_2$, $P_4$ giúp giảm tỷ lệ frame jank từ **24.8% xuống 8.0%** (giảm >3 lần so với $P_3$), đồng thời cơ chế Backpressure loại bỏ các tác vụ nền quá hạn giúp rút ngắn thời gian hoàn thành kịch bản nhanh hơn ~10 giây.
- **Overhead Bộ lập lịch:** Chi phí điều phối và truyền thông điệp giữa các Isolate chỉ tốn **0.34 ms (p50)** và **0.47 ms (p95)**, chỉ chiếm ~2% ngân sách một khung hình 16.7ms.
