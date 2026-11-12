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
- [ ] A8 Bộ ảnh 200–500 ảnh 1–4 MP vào assets (hoặc sinh ảnh giả để chạy trước)
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
- [ ] C6 Chạy chính thức **S1 × P0–P3 × 10 lần** (kịch bản ngẫu nhiên hóa)
- **Tiêu chí qua:** frame rớt P3 < P1; critical p95 < 100 ms (hoặc ngưỡng chốt sau pilot).

### D. P4: AIMD + chế độ suy giảm (Ngày 4)
- [ ] D1 AIMD (+1 khi tốt, ×0.5 khi xấu) theo p95 frame
- [ ] D2 SignalSource: Scripted (S4) + Real (MethodChannel thermal/battery)
- [ ] D3 Mode machine Normal/Conserve/Critical + hysteresis (5–10 s)
- [ ] D4 Backpressure khi hàng đợi quá dài
- [ ] D5 Kịch bản S2 (tải tăng dần mỗi 15 s) và chạy chính thức 10 lần
- **Tiêu chí qua:** số worker phản ứng theo frame time; số lần đổi chế độ không chập chờn.

### E. S3, S4, phân tích (Ngày 5)
- [ ] E1 S4 giả lập nhiệt (Normal→Conserve→Critical)
- [ ] E2 S3 chạy dài 10–15 phút (3–5 lần) + `battery_sampler.py`
- [ ] E3 Đo overhead scheduler (hàng đợi rỗng/tải nhẹ)
- [ ] E4 Ablation + quét tham số (N, chunk, ngưỡng nhường)
- [ ] E5 `tools/analyze/`: bảng chính, median/IQR, Mann-Whitney U
- [ ] E6 4 biểu đồ: timeline P0/P1/P4 · scatter đánh đổi · worker vs frame time · throughput S3
- [ ] E7 (tùy chọn) điểm tổng hợp + phân tích độ nhạy trọng số

### F. Báo cáo & bàn giao (Ngày 6–7)
- [ ] F1 Chương 3 trả lời H1–H5 (bảng + biểu đồ + câu kết luận có số)
- [ ] F2 Mục Hạn chế (2.7)
- [ ] F3 Slide + video demo P0 vs P4
- [ ] F4 README: cách chạy từng chính sách/kịch bản
- [ ] F5 Gói: CSV thô + metadata, script phân tích, ảnh DevTools/Perfetto

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
| 2026-11-12 | Bắt đầu C6: S1 chính thức none,p0,p1,p2,p3 × L64 W8 C80 × 10 lần, `--max-temp 36` | [~] |
| 2026-11-12 | Theo yêu cầu rút gọn thời gian: dừng matrix 50 lần (mới xong p1_5), chuyển dữ liệu pilot L64 sang `data/pilot/` (tránh trộn chunk 10/80). Chạy lại gọn: none,p0,p1,p2,p3 × L64 W8 C80 × **4 lần** (run 11–14), ~1 giờ. Cỡ mẫu nhỏ → báo khoảng dao động, không khẳng định quá mức (mục 2.7) | [~] |
