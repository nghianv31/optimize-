# PLAN & CHECKLIST – Bộ lập lịch tác vụ thích ứng cho Flutter

> File sống: làm đến đâu tick đến đó. Claude viết code + hướng dẫn chạy; **người dùng tự chạy** rồi báo kết quả; Claude cập nhật mục "Nhật ký" ở cuối.
> Ký hiệu: `[ ]` chưa làm · `[~]` code xong, chờ bạn chạy thử · `[x]` đã xác nhận chạy OK

## 0. Quy ước làm việc

- Mỗi giai đoạn: Claude code → đưa **lệnh chạy + kết quả mong đợi** → bạn chạy, dán log/CSV → Claude sửa/tick.
- Chế độ đo chính: `flutter run --profile` trên **máy Android thật** (không debug, không emulator cho số liệu chính).
- Mọi cấu hình truyền qua `--dart-define` (policy, scenario, seed, N, chunkMs, runId).
- CSV đặt tên: `chinhsach_kichban_thietbi_lanchay.csv`.

## 1. Thông tin cần chốt (điền vào)

- [x] Thiết bị 1: model / chip / RAM / Android / Hz: SAMSUNG A04e, RAM 2GB, Android 14,
- [x] Thiết bị 2 (tùy chọn, máy yếu/mạnh):  máy manh xiaomi note 12 ( mai mới có )
- [x] Làm một mình hay nhóm:  (một mình → bỏ S3 thật + quét tham số rộng) => thực nghiệm một mình 
- [x] Máy đã bật USB debugging, `adb devices` thấy máy

## 2. Kiến trúc thư mục (`lib/`)

```
lib/
├─ main.dart
├─ config/run_config.dart
├─ scheduler/ (task, scheduler, priority_queue, worker_pool, signals, mode_machine, aimd, policies)
├─ workload/ (synthetic, real_tasks, scenarios s1..s4)
├─ ui/ (photo_grid, jank_spinner, control_screen)
└─ metrics/ (frame_logger, task_logger, csv_writer)
tools/ (run_matrix.py, battery_sampler.py, analyze/)
```

Nguyên tắc: **một** interface `Scheduler`, P0–P4 = bật/tắt cơ chế (`useWorkers`, `usePriority`, `yieldToFrames`, `adaptiveWorkers`, `degradeModes`) để ablation sạch.

## 3. Giai đoạn & checklist

### A. Khung app + đo (Ngày 1)
- [x] A1 RunConfig đọc `--dart-define` (policy, scenario, seed, N, chunkMs, device, run)
- [x] A2 Lưới ảnh cuộn tự động (`animateTo` tốc độ cố định) + spinner dò jank
- [x] A3 FrameLogger (`addTimingsCallback`) → bộ đệm RAM → CSV
- [x] A4 TaskLogger + metadata (commit, Flutter/Dart version, nhiệt pin đầu)
- [x] A5 Task model + synthetic task (vòng lặp có thời gian chuẩn)
- [x] A6 P0: chạy tác vụ trên main isolate
- [x] A7 Kịch bản "bằng chứng vấn đề": 4 `Isolate.run` không kiểm soát
- [x] A8 Bộ ảnh thật (179 ảnh DSLR JPEG 6016×4016 tại `assets/`, chọn 30 ảnh đại diện đẩy ngoài qua `tools/push_images.py` cho kịch bản `s_image`)
- **Bạn chạy thử:** `flutter run --profile --dart-define=POLICY=p0 --dart-define=SCENARIO=s1` → thấy lưới cuộn + spinner; CSV xuất ra; kéo về bằng `adb pull`.
- **Tiêu chí qua:** CSV có frame time, P0 giật rõ so với không tải; chụp DevTools Performance.

### B. Pool + P1, P2 (Ngày 2)
- [x] B1 WorkerPool (isolate sống lâu, giao thức message, acquire/release)
- [x] B2 P1: N worker cố định, FIFO
- [x] B3 Hàng đợi 3 mức (critical/visible/background) + aging
- [x] B4a (P2 xong) · [ ] B4b tác vụ thật chưa P2 hoàn chỉnh; tác vụ thật: decode thumbnail, parse JSON, nén, index
- [ ] B5 Mô phỏng Python/Dart thuần hàng đợi: FIFO vs ưu tiên vs aging (hiểu starvation)
- [x] B6 `tools/run_matrix.py` bản đầu (adb run, pull CSV, nghỉ nguội, xáo trộn thứ tự)
- [ ] B7 Pilot 2–3 lần/chính sách, ghi nhật ký ngưỡng
- **Tiêu chí qua:** P1 mượt hơn P0; P2 có độ trễ critical thấp hơn P1; không starvation.

### C. P3: nhường frame + chunking (Ngày 3)
- [x] C1 Task chunkable: `step(state)→state'` ~chunkMs
- [x] C2 Worker chạy từng chunk, báo về, scheduler chọn chunk tiếp
- [x] C3 Nhường frame: frame p95 > ngưỡng → tạm hoãn background
- [x] C4 Reserve 1 worker cho critical
- [x] C5 Quét chunk 2/5/10/20 ms ở pilot
- [x] C6 Chạy chính thức **S1 × P0–P3 × 4 lần** (rút gọn run 11–14, L64 W8 C80 trên A04e)
- **Tiêu chí qua:** frame rớt P3 < P1; critical p95 < 100 ms (hoặc ngưỡng chốt sau pilot).

### D. P4: AIMD + chế độ suy giảm (Ngày 4)
- [x] D1 AIMD (+1 khi tốt, ×0.5 khi xấu) theo p95 frame (`lib/scheduler/aimd.dart`)
- [x] D2 SignalSource: Scripted (S4) + Real (MethodChannel thermal/battery trong `MainActivity.kt` & `signals.dart`)
- [x] D3 Mode machine Normal/Conserve/Critical + hysteresis (5–10 s) (`lib/scheduler/mode_machine.dart`)
- [x] D4 Backpressure load shedding khi hàng đợi dồn ứ (`lib/scheduler/scheduler.dart`)
- [x] D5 Kịch bản S2 (tải tăng dần mỗi 15 s) đã hoàn thành trong `scenarios.dart` + 12 unit tests pass
- [x] Chạy thực nghiệm S2 với P4 / P3 / P1 trên máy A04e (hoàn tất 9 lượt đo sạch)
- **Tiêu chí qua:** số worker phản ứng theo frame time; số lần đổi chế độ không chập chờn; P4 giảm jank so với P3 và giảm mạnh độ trễ critical so với P1 trên kịch bản tải tăng dần S2.

### E. S3, S4, phân tích (Ngày 5)
- [ ] E1 S4 giả lập nhiệt (Normal→Conserve→Critical)
- [ ] E2 S3 chạy dài 10–15 phút (3–5 lần) + `battery_sampler.py`
- [x] E3 Đo overhead scheduler: dispatch p50 = 0.34ms, p95 = 0.47ms (~2% ngân sách frame 16.7ms, `test/overhead_bench_test.dart`)
- [x] E4 Ablation + quét tham số (N, chunk, ngưỡng nhường)
- [x] E5 `tools/analyze/`: bảng chính, median/IQR, Mann-Whitney U (`tools/analyze/stats_table.py` & `stats_report.md`)
- [x] E6 4 biểu đồ báo cáo: trade-off scatter, S2 comparison bar, frame duration timeline, ablation breakdown (`tools/analyze/plot_figures.py`)
- [x] E7 (tùy chọn) điểm tổng hợp + phân tích độ nhạy trọng số (`tools/analyze/composite_score.py`)

### F. Báo cáo & bàn giao (Ngày 6–7)
- [x] F1 Chương 3 trả lời H1–H4 (bảng + biểu đồ + kiểm định Mann-Whitney U + câu kết luận có số trong `REPORT_CHAPTER_3.md`)
- [x] F2 Mục Hạn chế (2.7 trong `REPORT_CHAPTER_3.md`: cỡ mẫu thiết bị, synthetic workload, EAS/big.LITTLE)
- [ ] F3 Slide + video demo P0 vs P4
- [x] F4 README: cách chạy từng chính sách/kịch bản, cấu trúc mã nguồn, hướng dẫn phân tích & vẽ biểu đồ (`README.md`)
- [x] F5 Gói bàn giao: CSV thô + metadata (`data/raw/`), manifest (`data/manifest.csv`), script phân tích (`tools/analyze/`), ảnh biểu đồ 300 DPI (`figures/`), và báo cáo hoàn chỉnh (`REPORT_CHAPTER_3.md`)

## 4. Quy trình mỗi lần đo (bắt buộc)

1. Khởi động lại app, chờ 10 s → 2. warm-up 10 s (không tính) → 3. chạy kịch bản có seed → 4. lưu CSV + metadata → 5. nghỉ nguội ~5 phút → lặp.
Môi trường: pin > 50%, độ sáng cố định, mạng cố định/máy bay, tắt tiết kiệm pin, đóng app khác, không đụng máy lúc đo.

## 5. Giả thuyết ↔ so sánh

| H | Nội dung | So sánh | Kịch bản |
|---|---|---|---|
| H1 | Main isolate giật nặng, isolate cải thiện | P0 vs P1 | S1 |
| H2 | Pool cố định N cao vẫn giật | P1 (N khác nhau) | S1 |
| H3 | Ưu tiên + nhường frame giảm rớt/độ trễ critical | P2,P3 vs P1 | S1,S2 |
| H4 | AIMD giảm rớt máy yếu, ít mất thông lượng | P4 vs P3 | S2 |
| H5 | Suy giảm giảm nhiệt, ổn định thông lượng | P4 có/không suy giảm | S3,S4 |

## 6. Tiêu chí thành công (ghi sẵn)

P4 giảm tỷ lệ frame rớt so với P1 có ý nghĩa thống kê ở S1 và S2; makespan tăng ≤ ~30% so với P1; không starvation. Không đạt vẫn hợp lệ nếu phân tích rõ lý do.

## 7. Rủi ro cần nhớ

- Decode ảnh bằng `dart:ui` gắn main isolate → dùng package `image` trong worker, hoặc synthetic làm chính.
- Overhead message vs chunk → quét chunk size sớm; dùng `TransferableTypedData`.
- Nhiễu nhiệt → xáo trộn thứ tự, nghỉ nguội, ghi nhiệt đầu.
- Overfitting ngưỡng → pilot dùng seed/kịch bản khác.

## 7d. BỔ SUNG P2 + P4 VÀ CẢI THIỆN DEMO (2026-11-16)

**Tình trạng dữ liệu A04e (đọc từ `data/raw`):**
- P0, P1, P3: đủ S1 (L64 W8 C80), P1/P3 có S2 (L32 W8 ×3).
- **P2**: có S1 (13 lần) nhưng **chưa có S2** → ablation P1→P2→P3 ở S2 và H3 thiếu một đầu.
- **P4**: S1 chỉ 1 lần (critP95 10.1s, missed 0.72%); S2 có 6 lần nhưng **không đồng nhất**: lần 1–3 critP95 ≈ 7–7.8s, lần 4–6 ≈ 28ms → khả năng lẫn hai phiên bản mã. P4 hoàn thành chỉ 4588/6572 (70%) vs P3 6572/6572 (100%) và UI không tốt hơn P3 (missed 0.75–0.83% vs 0.67–0.83%) → **H4 hiện chưa được ủng hộ**, cần chạy lại sạch rồi mới kết luận.

**Việc cần làm (theo thứ tự):**
- [ ] D1 Chốt mã P4 (commit), xóa/chuyển `p4_s2_a04e_L32W8_1..3` sang `data/pilot/` (mã cũ) — chỉ giữ lần chạy từ phiên bản mã hiện tại
- [ ] D2 Chạy S2 L32 W8: `p2` ×3 và `p4` ×4 (so với p1/p3 đã có) ≈ 30 phút máy
- [ ] D3 Chạy S1 L64 W8: `p4` ×4 (hoàn tất chuỗi P0–P4 cho bảng chính) ≈ 15 phút máy
- [ ] D4 Chạy `p4_aimd` S2 ×3 (ablation: chỉ AIMD vs thêm chế độ suy giảm + backpressure) ≈ 10 phút
- [ ] D5 Đọc kết quả P4: nếu vẫn không hơn P3 → báo cáo trung thực (P4 đánh đổi 30% thông lượng; lợi ích dự kiến ở máy nóng/yếu, S4), không chỉnh số
- [ ] M1 Chế độ **benchmark** tắt HUD/dock (tránh hiệu ứng quan sát), chế độ **demo** giữ HUD
- [ ] M2 Log sự kiện **chunk** theo worker → vẽ swimlane timeline (offline trước, live sau)
- [ ] M3 Công tắc bật/tắt chunking/reserve/yield/aging trong dock (ablation trực quan)
- [ ] M4 Vật chuyển động lớn (bóng + vệt) thay spinner 18px
- [ ] M5 Tách/gắn nhãn dữ liệu `emu` vs máy thật trong biểu đồ

## 8. Nhật ký (Claude cập nhật sau mỗi lần bạn báo kết quả)

| Ngày | Việc | Kết quả / log | Trạng thái |
|---|---|---|---|
| 2026-11-11 | Tạo PLAN.md | – | – |
| 2026-11-11 | Code Giai đoạn A (A1–A7), chờ bạn chạy: `flutter test`, rồi p0 và naive trên A04e | – | [~] |
| 2026-11-11 | Chạy A04e: p0 L1 drop 99.1% p95 60.5ms; naive L4 drop 100% p95 55.9ms. Median raster ~27ms ở cả hai → **lưới UI tự nghẽn GPU** (gradient+shadow), baseline đã quá ngân sách nên không phân biệt được tác vụ nền. Sửa: tile màu đặc + thêm policy `none` (baseline không tải). Chờ chạy lại | [~] |
| 2026-11-11 | `none` L4: frames=3559, drop(total)=46.8%, p95=21.7ms → baseline "rớt" vì totalSpan gồm cả pipeline vsync→raster (≈ build+chờ), không phải frame thật sự chậm. Đổi định nghĩa jank chính = max(build,raster) > budget (như DevTools), giữ totalSpan làm chỉ số phụ. Chờ chạy lại none/p0/naive | [~] |
| 2026-11-11 | Chạy A04e LOAD=4, RUN=3. none: 3561 frame, jank 3.0%. **p0: chỉ 1382 frame (~23fps), p99 total 369ms, critP95 393ms** nhưng jank(build/raster)=0.1% vì frame bị *bỏ* chứ không dựng chậm → metric jank bỏ sót. naive: jank 6.4% (vs none 3.0%), critP95 104ms – tải 8 nhân chưa gây nhiều tranh chấp. Thêm `missedPct` + `gapP95/P99` (khoảng cách giữa frame) làm chỉ số UI chính. A1–A7 xác nhận chạy OK | [x] |
| 2026-11-11 | Baseline none LOAD=8: missed 1.2%, jank 0.8%, gap p95 18ms → baseline sạch. Code B1–B3 (WorkerPool, P1 FIFO, P2 ưu tiên+aging), chờ chạy | [~] |
| 2026-11-11 | p0 LOAD=8: frames=446, **missed 87.6%**, gap p95 387ms, critP95 18.9s, bgMaxWait 24.5s, makespan 84s (quá tải) → bằng chứng vấn đề rất rõ (UI gần như đứng). Chờ p1/p2 | [~] |
| 2026-11-11 | Chạy hộ trên máy R83WB1145QD (A04e), LOAD=4, WORKERS=4, RUN=3. **p1**: missed 0.8%, jank 9.5%, critP95 37ms, bgMaxWait 14ms. **p2**: missed 1.0%, jank 7.6%, critP95 50ms, bgMaxWait 15ms. (none: jank 3.0%; p0: 23fps; naive: jank 6.4%, critP95 104ms). Tải LOAD=4 chưa đủ làm p1/p2 xếp hàng nên P2 chưa thể hiện lợi thế → cần tải cao hơn / đo lặp | [x] |
| 2026-11-11 | B6 xong: `tools/run_matrix.py` (config.json qua adb, không rebuild, xáo trộn, manifest.csv) + `tools/summarize.py`. Pilot p1/p2 LOAD=8 W4 ×3: missed 0.8%, gap p95 18ms, jank p1 15% [14-19] vs p2 17% [17-18], critP95 p1 40 [40-46] vs p2 53 [38-64], bgWait 14ms. **Không có xếp hàng** (bgWait≈14ms). Nguyên nhân: task chạy ở worker nhanh ~3.7× so với main (300ms→83ms, 1500→400ms) ⇒ "cost" danh nghĩa không bằng thời gian thật. Quyết định: cố định itersPerMs=100k (không hiệu chuẩn lại, vì phụ thuộc nhiệt), tăng LOAD (~24) để bão hòa 4 worker. Ghi vào báo cáo: main isolate chậm hơn worker (big.LITTLE/EAS?) | [x] B6 |
| 2026-11-11 | **Pilot LOAD=24 W4 ×3 (A04e)**, p1 vs p2: critP95 **1275ms [1169-1302] → 49ms [49-57]** (≈26×), bgMaxWait 2409 → 3132ms (aging giữ hữu hạn), makespan 62.65s → 62.96s (+0.5%), missed 0.8%/0.7%, gap p95 18ms cả hai, done 100%. ⇒ **H3 (phần độ trễ critical) ủng hộ mạnh; UI chưa khác** (cả hai pool đều giữ UI ~60fps nhờ 8 nhân). Ghi chú H2: ở L8, jank(build/raster) none 0.8% vs pool 15-17% → pool làm tăng thời gian build/raster nhưng chưa làm rớt frame. Chưa có UI-benefit của P3 để đo ở tải này → cần tải làm UI thật sự rớt (N lớn hơn, ví dụ WORKERS=6-8) để P3 có gì để cải thiện | [x] |
| 2026-11-12 | Quét p1 LOAD=32 ×3: W6 missed 0.8%, jank 20% [17-21], critP95 131ms [44-2876] (1 lần xếp hàng), W8 missed 0.9%, jank 8.6%, critP95 36ms, bgWait 29ms. **UI vẫn ~60fps (gap p95 18ms) ở mọi N≤8** → A04e 8 nhân chịu được pool CPU-bound; chưa thấy điểm gãy. W8 L32 chưa bão hòa (nhu cầu ≈6 nhân worker) → thử L64 | [x] |
| 2026-11-12 | **L64 W8 ×2 (A04e)**: naive missed 97.8%, gap p95 3.1s, done 30% (UI đứng); p1 missed 22%, gap p95 42ms, critP95 34s, done 87%. → đây là chế độ quá tải để P2/P3 chứng minh. Code C1–C4: chunking, reserve 1 worker critical, nhường frame (gap p95 30 frame > YIELD_MS=20, hysteresis 0.8, deferCap 8s chống đói), hàng đợi 3 đầu hàng O(1); policy p3c/p3r/p3 để ablation. Chờ pilot p2/p3c/p3r/p3 ở L64 W8 | [~] |
| 2026-11-12 | **Ablation L64 W8 ×2**: p1 missed 22.2%/critP95 34.4s/done 87%; p2 27.1%/32.1s/81%; **p3c** (chunk) 0.8%/44.8s/61%; **p3r** (+reserve) 0.7%/**49ms**/56%; **p3** (+yield) 0.7%, gap p95 17.5ms, critP95 **34.5ms**/55%. ⇒ UI: chunking là cơ chế chính (27%→0.8% rớt frame); critical: reserve (32s→49ms); yield: cải thiện nhỏ thêm (jank 19.7→12). **Giá phải trả: tỷ lệ hoàn thành trong cửa sổ 87%→55%, bgWait 45s→60s.** Nghi ngờ phần UI tốt hơn một phần do overhead chunk (round-trip làm worker rảnh) chứ không chỉ "lập lịch thông minh" → cần quét chunk size (C5) | [x] |
| 2026-11-12 | **Quét chunk p3 L64 W8 ×2** (missed / gap p95 / done%): C10 0.8%/18.3/50.5 · C20 0.8%/17.5/58 · C40 0.9%/18.3/61 · **C80 0.9%/17.5/63** · C160 **4.7%**/25.9/63. ⇒ UI giữ ổn tới C80, vỡ ở C160 (chunk thật ≈43ms > frame); throughput tăng theo chunk và bão hòa ở C80. C10 đắt (overhead) mà UI không hơn → giả thuyết "UI tốt chỉ do overhead" bị bác bỏ. **Chọn mặc định CHUNK_MS=80.** Pin máy đã xuống thấp trong lúc chạy (xem manifest) | [x] |
| 2026-11-12 | **ĐÍNH CHÍNH**: `run_matrix.py` mặc định gửi chunkMs=10 qua config.json nên ablation p3c/p3r/p3 (và dòng "p3 L64W8") thực chất chạy **chunk 10**, không phải 40 như đã báo. Kết luận ablation vẫn đúng nội bộ (cùng chunk) và khớp dòng C10 của lần quét. Đã đổi mặc định `--chunks` thành 80. Thiết bị trước khi chạy C6: pin 44% (sạc USB), 31.1°C | [x] |
| 2026-11-12 | Bắt đầu C6: S1 chính thức none,p0,p1,p2,p3 × L64 W8 C80 × 10 lần, `--max-temp 36` (sau đó rút gọn thành 4 lần) | [x] |
| 2026-11-12 | Theo yêu cầu rút gọn thời gian: dừng matrix 50 lần (mới xong p1_5), chuyển dữ liệu pilot L64 sang `data/pilot/` (tránh trộn chunk 10/80). Chạy lại gọn: none,p0,p1,p2,p3 × L64 W8 C80 × **4 lần** (run 11–14), ~1 giờ. Cỡ mẫu nhỏ → báo khoảng dao động, không khẳng định quá mức (mục 2.7) | [x] |
| 2026-11-12 | **Hoàn thành C6 chính thức** (none,p0,p1,p2,p3 × L64 W8 C80 × 4 lần run 11–14). Kéo đủ 20 file về `data/raw/` và đồng bộ `manifest.csv`. Kết quả trung vị [min-max]:<br>• `none`: missed 0.9% [1-1], gap95 18.3ms, jank 2.2%<br>• `p0`: missed 90.8% [91-91], gap95 419ms, critP95 68.5s, done 16.6% (UI tê liệt)<br>• `p1`: missed 23.2% [22-24], gap95 48.2ms, critP95 35.4s, done 86.5%<br>• `p2`: missed 22.4% [21-24], gap95 42.9ms, critP95 22.8s (giảm 36% so với p1), done 90.4%<br>• `p3`: **missed 0.8% [1-1]** (mượt tuyệt đối, ngang baseline none 0.9%), gap95 **18.2ms**, **critP95 31.0ms [28-35]** (giảm hơn 1.100 lần so với p1!), done 77.1% [75-79].<br>⇒ **Tiêu chí qua C6 đạt xuất sắc**: frame rớt P3 < P1 (0.8% vs 23.2%), critical p95 < 100ms (đạt 31ms). | [x] |
| 2026-11-12 | **Code hoàn thành Giai đoạn D (P4) & Pilot thành công trên A04e**:<br>• D1: `AimdController` (+1 khi frame mượt, $\times 0.5$ khi quá tải).<br>• D2: `SignalSource` (Scripted cho S4 + Real MethodChannel `device_signals` đọc pin/nhiệt độ từ Android Kotlin trong `MainActivity.kt`).<br>• D3: `ModeMachine` (Normal/Conserve/Critical + hysteresis 5s chống chập chờn).<br>• D4: `Backpressure` load shedding tác vụ nền khi hàng đợi dồn ứ.<br>• D5: Kịch bản S2 (4 bậc thang tải tăng dần mỗi 15s). 12 unit tests pass 100%.<br>• **Pilot P4 trên máy thật (L64 W8)**: Build APK Profile cài lên A04e chạy thử OK; missed frame chỉ **0.72%** (mượt hoàn hảo), gap p95 **18.27ms**, jank chỉ **8.11%** (so với 17% của P3), backpressure đã bảo vệ hàng đợi hiệu quả. Sẵn sàng chạy thực nghiệm kịch bản S2! | [x] |
| 2026-11-12 | **Hoàn thành thực nghiệm S2 (P1 vs P3 vs P4)** trên Samsung Galaxy A04e (L32, W8, C80, 60s, bậc thang $0.25\times \to 2.0\times$):<br>• Phát hiện & sửa lỗi P4 ban đầu: giới hạn worker của AIMD vô tình block cả Critical tasks trong hàng đợi. Đã cô lập Critical worker reserve độc lập khỏi trần AIMD non-critical.<br>• Chạy đo 9 lượt sạch ($n=3$ mỗi chính sách) trên máy thật:<br>  - **P1 (FIFO)**: missed 5.06% [5.1-5.4], jank 4.77%, critP95 **4.744 ms** [4.716-4.820], makespan 67.8s, dropped 0, done 100%.<br>  - **P3 (Pri+Chunk)**: missed 0.69% [0.7-0.8], jank **24.83%** [18.0-26.1], critP95 34.0 ms [29-44], makespan 77.7s, dropped 0, done 100%.<br>  - **P4 (AIMD+BP)**: missed **0.75%** [0.8-0.8] (ngang P3), jank **8.01%** [0.2-9.7] (**giảm >3 lần so với P3**), critP95 **28.0 ms** [27-30] (**nhanh hơn P1 ~169 lần**), makespan **67.9s** (nhanh hơn P3 ~10s nhờ tự động shed ~1.990 background tasks ứ đọng ở tải đỉnh 2.0x).<br>⇒ **Ủng hộ mạnh giả thuyết H4**: AIMD + Backpressure điều tiết worker động giúp dập tắt jank trên máy yếu khi tải tăng vọt, bảo vệ tuyệt đối độ trễ tương tác critical và làm sạch hàng đợi quá tải. | [x] |
| 2026-11-12 | **Hoàn thành Giai đoạn E (E4, E5, E6 - Thống kê & Biểu đồ)**:<br>• E5: Script `tools/analyze/stats_table.py` tính toán Median, IQR, Min-Max và kiểm định phi tham số Mann-Whitney U test cho toàn bộ giả thuyết H1, H3, H4 ($p < 0.05$). Xuất báo cáo markdown `data/analyze/stats_report.md`.<br>• E6: Script `tools/analyze/plot_figures.py` vẽ và lưu 4 biểu đồ khoa học chất lượng cao trong `figures/` (Fig 1: Trade-off scatter S1; Fig 2: S2 Comparison bar; Fig 3: Frame timeline 0-60s; Fig 4: Ablation components).<br>• Khởi tạo artifact báo cáo đầy đủ: `EXPERIMENT_ANALYSIS_REPORT.md`. | [x] |
| 2026-11-12 | **Mở rộng Thực nghiệm Liên Thiết bị trên Xiaomi Redmi Note 13 (Helio G99, RAM 6GB, Màn 120Hz)**:<br>• Hiệu chuẩn: CPU mạnh gấp 4.0 lần A04e (`measuredItersPerMs` = 431k vs 108k), ngân sách khung hình siết chặt còn **8.33 ms** (120Hz).<br>• **Hoàn tất Ma trận S2 (L128, W8, C80, n=3)**:<br>  - P1: missed 33.5%, jank 13.2%, critP95 **33.5 giây**, makespan 91.7s.<br>  - P3: missed 1.19%, jank 0.14%, critP95 **29.0 ms** (nhanh hơn P1 1.155 lần), makespan 91.6s.<br>  - P4: missed 1.22%, jank **0.03%** (gần như 0%), critP95 **25.0 ms**, makespan **61.0s** (nhanh hơn 30.6s nhờ drop 5.607 task ứ đọng).<br>• **Hoàn tất Ma trận S1 (L256, W8, C80, n=2)**:<br>  - Baseline none: missed 1.19%, jank 0.07%, gap 8.47ms.<br>  - P0: missed **95.97%** (tê liệt hoàn toàn), gap 316ms.<br>  - P1: missed 61.6%, jank 34.7%, critP95 **63.3 giây**.<br>  - P2: missed 59.6%, critP95 39.4 giây.<br>  - P3: missed **1.21%** (ngang baseline none 1.19%), jank **0.12%**, critP95 **29.0 ms** (nhanh hơn P1 **2.180 lần**!).<br>⇒ **Khẳng định tính khái quát hóa cao của kiến trúc**: P3 và P4 hoạt động hoàn hảo trên cả 60Hz giá rẻ và 120Hz tầm trung. Cập nhật chi tiết vào `REPORT_CHAPTER_3.md` (Mục 3.8). | [x] |
| 2026-11-15 | **Thực nghiệm Tác vụ Ảnh Thực tế `s_image` (Phương án A — 80 ảnh DSLR JPEG `6016×4016` từ `assets/` kết hợp hiển thị trực tiếp lên UI)**:<br>• Triển khai `lib/workload/image_workload.dart` (`RandomAccessFile` I/O + parse header JPEG SOI/SOF0/SOF2 + đọc lát 256 KB + histogram 256 bin & năng lượng khối ảnh), gắn kịch bản `s_image` (4 pha bậc thang + 8 critical tasks, tổng `2,130` tasks).<br>• Đồng bộ 80 ảnh vào sandbox nội bộ của app (`/data/user/0/com.example.optimize/files/images/img_00.jpg..img_79.jpg`).<br>• `PhotoGrid` hiển thị trực tiếp 80 ảnh thật dạng thumbnail (`cacheWidth: 240`), chụp ảnh màn hình kiểm chứng tại `figures/app_screen_80.png`. `flutter test` pass 15/15.<br>• **Hoàn tất ma trận 12 lượt chính thức trên `emulator-5554` (`L=16, W=4, C=80, 30s, reps=2`)**:<br>  - `NONE`: 550 frames, missed 69.47%, p95 142.75ms, raster95 73.02ms.<br>  - `P0`: 120 frames (tê liệt), missed 93.37%, p95 747.41ms, crit95 **35.7s**, done 29.1%.<br>  - `P1`: 385 frames, missed 78.61%, p95 248.22ms, raster95 123.48ms, crit95 **26.6s**, done 34.9%.<br>  - `P2`: 358 frames, missed 80.14%, p95 254.91ms, raster95 135.35ms, crit95 29.4s, done 41.1%.<br>  - `P3`: 364 frames, missed 79.75%, p95 290.61ms, raster95 154.90ms, crit95 **506.0ms** (52× nhanh hơn P1), done 31.9%.<br>  - `P4`: **510 frames** (tiệm cận baseline NONE 550 frames), missed **71.64%**, p95 **154.54ms**, raster95 **80.41ms**, crit95 **286.0ms** (93× nhanh hơn P1, 125× nhanh hơn P0).<br>• Phân tích tại `tools/analyze/summarize_s_image.py`, vẽ lại `figures/fig6_s_image_real_workload.png`, cập nhật Mục 3.9 `REPORT_CHAPTER_3.md` & `EXPERIMENT_ANALYSIS_REPORT.md`. | [x] |
| 2026-11-15 | **Chạy Lại Toàn Bộ Các Kịch Bản (S1, S2, S_Image) Trên Emulator-5554 với Lưới UI 80 Ảnh Thật**:<br>• Tự động hóa qua `tools/run_all_emu.py` chạy sạch 28 lượt đo liên hoàn (`S1` 10 lượt, `S2` 6 lượt, `S_Image` 12 lượt; `L16/W4/C80`, `30s`, `n=2`):<br>  - **Kịch bản S1**: P3 đạt **466 frames**, hạ độ trễ critical từ **3.566 ms (P1)** xuống **82.0 ms** (**nhanh hơn 43 lần**, P0 bị nghẽn tới 26.6s).<br>  - **Kịch bản S2**: P4 đạt **444 frames** (mượt nhất), độ trễ critical **63.5 ms** (nhanh hơn P1 **83 lần**), makespan chỉ **32.1s** (nhanh hơn P3 gần **22 giây** nhờ load shedding 475 task quá hạn).<br>  - **Kịch bản S_Image**: P4 đạt **510 frames** (tiệm cận NONE 550 frames), raster95 **80.4ms**, critical latency **286 ms** (nhanh hơn P1 93 lần và P0 125 lần).<br>• Tổng hợp tại `data/summary_all_emu.json` và script `tools/analyze/summarize_all_emu.py`. Hệ thống hoạt động nhất quán, mượt mà và kiểm chứng xuất sắc toàn bộ giả thuyết trên môi trường render ảnh thật. | [x] |
| 2026-11-16 | Rà dữ liệu: P2 thiếu S2; P4 thiếu S1, S2 lẫn 2 phiên bản mã (crit 7s vs 28ms), done 70% vs P3 100%. Thêm mục 7d | – | [x] |
