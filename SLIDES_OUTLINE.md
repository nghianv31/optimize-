# ĐỀ CƯƠNG SLIDE THUYẾT TRÌNH BẢO VỆ ĐỀ TÀI & KỊCH BẢN DEMO VIDEO

**Tên đề tài:** Khung lập lịch tác vụ thích ứng theo thời gian dựng frame (Frame-Aware Adaptive Scheduling) trên thiết bị di động Flutter cấu hình thấp  
**Thiết bị thực nghiệm:** Samsung Galaxy A04e (MediaTek Helio P35, 8 nhân, RAM 2GB, Android 14)  
**Tác giả:** Nhóm nghiên cứu tối ưu hóa hiệu năng di động

---

## Slide 1: Tiêu đề & Giới thiệu
- **Tiêu đề:** Tối ưu hóa đa nhiệm và loại bỏ rớt khung hình trong Flutter trên thiết bị di động cấu hình yếu.
- **Vấn đề cốt lõi:**
  - Mô hình Single-Threaded Event Loop của Flutter: Main Isolate đảm nhận cả dựng hình UI (16.67ms) và xử lý sự kiện.
  - Tác vụ tính toán nặng chạy trên Main Isolate gây đứng hình (UI Freeze).
  - Sử dụng WorkerPool Isolate cố định đơn thuần vẫn dẫn đến **Head-of-Line Blocking** và nghẽn CPU khi quá tải.

---

## Slide 2: Mục tiêu & Đóng góp Nghiên cứu
- Xây dựng khung lập lịch thông minh từ $P_0 \to P_4$:
  1. Phân tách tác vụ ra WorkerPool Isolate nền ($P_1$).
  2. Hàng đợi 3 mức ưu tiên (`Critical > Visible > Background`) + Aging chống đói ($P_2$).
  3. Chia nhỏ tác vụ thành các chunk ~80ms, chừa 1 worker dự phòng, nhường frame khi UI bận ($P_3$).
  4. Thuật toán AIMD co/giãn worker động theo nhịp frame + Mode Machine + Backpressure ($P_4$).
- Kiểm chứng thực nghiệm trên thiết bị thật (Samsung Galaxy A04e) với các chỉ số đo lường chính xác.

---

## Slide 3: Kiến trúc Hệ thống ($P_0 \to P_4$)
- **Sơ đồ khối hệ thống:**
  - `FrameSignal` & `DeviceSignal`: Đo thời gian dựng frame qua `SchedulerBinding` và nhiệt độ/pin qua `MethodChannel`.
  - `TaskQueue`: 3 hàng đợi riêng biệt $O(1)$, hỗ trợ chèn đầu (`addFront`) cho các chunk dở dang.
  - `AimdController`: Pacing 500ms, tăng cộng $+1$ worker khi frame mượt, giảm nhân $\times 0.5$ khi frame chậm.
  - `ModeMachine`: Hysteresis 5 giây chống rung giật trạng thái (`Normal \to Conserve \to Critical`).

---

## Slide 4: Thiết lập Thực nghiệm & Phương pháp Đo lường
- **Phần cứng khắc nghiệt:** Samsung Galaxy A04e (8 nhân Cortex-A53, RAM 2GB).
- **Môi trường đo chuẩn hóa:** Chế độ `flutter build apk --profile`, kiểm soát nhiệt độ pin khởi đầu < 36°C.
- **Kịch bản kiểm thử:**
  - **S1:** Tải tĩnh bão hòa ($L=64, W=8, C=80$, thời lượng 60s).
  - **S2:** Tải động bậc thang 4 nấc ($0.25\times \to 0.5\times \to 1.0\times \to 2.0\times$, 8 tương tác critical ngẫu nhiên).
- **Thống kê:** Báo cáo Trung vị (Median), IQR, kiểm định phi tham số Mann-Whitney U.

---

## Slide 5: Kết quả H1 & H2 – Main Isolate vs WorkerPool FIFO
- **H1 (Nghẽn Main Isolate):**
  - $P_0$ (Main Isolate): Rớt **90.8%** frame, tốc độ hiển thị tụt xuống < 3 fps, độ trễ critical lên tới **68.5 giây**.
  - $P_1$ (WorkerPool FIFO): Giải phóng Main Isolate, tỷ lệ rớt frame giảm về **23.2%** ($p = 0.014$).
- **H2 (Giới hạn của Pool cố định):**
  - Tăng số worker không thể cứu được độ trễ tương tác: Tác vụ Critical ở $P_1$ vẫn phải xếp hàng sau các task nền khổng lồ $\to$ trễ **35.4 giây**.

---

## Slide 6: Kết quả H3 – Sự kết hợp giữa Chunking & Worker Reserve ($P_3$)
- **Điểm đột phá kiến trúc:**
  - Chia nhỏ tác vụ thành các chunk 80ms: Cho phép worker giải phóng nhanh, giải cứu UI $\to$ Tỷ lệ rớt frame giảm sốc từ **23.2% xuống 0.8%** (ngang baseline `none`).
  - Dành riêng 1 worker dự phòng cho Critical: Độ trễ critical giảm từ **35.4 giây xuống 31.0 ms** (giảm hơn 1.100 lần, $p = 0.014$).
  - Nhường frame (Frame Yielding): Tạm hoãn gửi task nền khi UI bận.
- *(Chèn hình ảnh: `fig1_s1_tradeoff.png` & `fig4_ablation_s1.png`)*

---

## Slide 7: Kết quả H4 – Thích ứng Động AIMD & Backpressure trên Máy Yếu ($P_4$)
- **Thử thách kịch bản tải bậc thang S2:**
  - Ở pha tải đỉnh $2.0\times$, $P_3$ giữ 8 worker chạy tối đa gây nghẽn CPU $\to$ **Jank tăng vọt lên 24.8%**, makespan kéo dài 77.7 giây.
  - $P_4$ dùng AIMD co worker nền: **Jank giảm hơn 3 lần xuống 8.0%** (có run chỉ 0.25%).
  - Độ trễ critical ở $P_4$ đạt kỷ lục: **28.0 ms** (nhanh hơn $P_1$ 169 lần).
  - Backpressure loại bỏ 1.990 task dồn ứ $\to$ Hệ thống không bị OOM, kết thúc nhanh hơn P3 gần 10 giây.
- *(Chèn hình ảnh: `fig2_s2_comparison.png`)*

---

## Slide 8: Phân tích Chuỗi thời gian Frame Timeline
- Trực quan hóa diễn biến render frame trong 60 giây giữa các chính sách:
  - $P_0$: UI bị đóng băng gần như hoàn toàn.
  - $P_1$: Rung giật liên tục, nhiều frame vượt quá 30–40ms.
  - $P_3$ & $P_4$: Đường thời gian frame bám sát đường ngân sách 16.7ms (60fps mượt mà).
- *(Chèn hình ảnh: `fig3_timeline_frames.png`)*

---

## Slide 9: Đo lường Scheduler Overhead
- Chi phí điều phối vi mô (Microbenchmark trên 200 tác vụ):
  - Round-trip Dispatch Latency $p50$: **0.34 ms** (345 µs).
  - Round-trip Dispatch Latency $p95$: **0.47 ms** (467 µs).
- **Kết luận:** Chi phí lập lịch chỉ chiếm **~2% ngân sách một frame (16.7ms)**, hoàn toàn vô hình đối với người dùng.

---

## Slide 10: Phân tích Điểm tổng hợp & Độ nhạy Trọng số
- Đánh giá Utility Score trên thang 100 theo 4 cấu hình: Cân bằng, Thiên về Mượt UI, Thiên về Độ trễ, và Thiên về Thông lượng.
  - **S1:** $P_3$ đạt điểm tuyệt đối từ **89.2 đến 93.5/100** (so với $P_1$ chỉ 32.4–54.5/100 và $P_0$ chỉ 5.5/100).
  - **S2:** $P_4$ đạt điểm xuất sắc **90.9–92.9/100** ở các kịch bản ưu tiên độ mượt UI và phản hồi tức thì.

---

## Slide 11: Hạn chế & Hướng phát triển
- **Hạn chế:**
  - Cỡ mẫu thực nghiệm trên máy thật ($n=3$ đến $n=4$) do yêu cầu làm nguội phần cứng.
  - Tải tổng hợp thuần CPU-bound (chưa xét I/O mạng hoặc truy xuất database).
- **Hướng phát triển:**
  - Mở rộng sang các tác vụ I/O bất đồng bộ và decode hình ảnh lớn.
  - Đóng gói thành thư viện mã nguồn mở Flutter package công khai cho cộng đồng.

---

## Slide 12: Tổng kết
1. **$P_0 \to P_1$:** Tách isolate là bắt buộc để UI không chết.
2. **$P_1 \to P_3$:** Chunking 80ms + Worker Reserve là chìa khóa duy nhất để đồng thời đạt **60fps** và **phản hồi critical < 35ms**.
3. **$P_3 \to P_4$:** AIMD + Backpressure là giải pháp sống còn trên thiết bị yếu khi chịu tải bùng nổ, giảm jank 3 lần và ngăn tràn RAM.

---

# KỊCH BẢN QUAY VIDEO DEMO SO SÁNH ($P_0$ vs $P_4$)

### Chuẩn bị:
- Thiết bị: Samsung Galaxy A04e (cài bản APK Profile).
- Màn hình hiển thị: Ứng dụng `optimize` với lưới 16 ô màu biến thiên và nút bấm "Tương tác Critical" (khi bấm sẽ đổi màu tức thì và hiển thị độ trễ).

### Kịch bản quay (Thời lượng: ~2 phút):

1. **Phần 1: Demo Chính sách $P_0$ (Main Isolate) – 0:00 - 0:45**
   - Chọn Policy: `p0`, Scenario: `s1`. Bấm "BẮT ĐẦU CHẠY".
   - **Hiện tượng:** Sau 10 giây warmup, khi tải $L=64$ kích hoạt, lưới màu và đồng hồ bấm giờ **hoàn toàn đứng yên (Freeze cứng)**.
   - Người dùng liên tục chạm vào màn hình: Nút bấm không có bất kỳ phản hồi nào.
   - Kết quả xuất hiện: Missed Frame > 90%, Độ trễ Critical > 60 giây.

2. **Phần 2: Demo Chính sách $P_4$ (AIMD + Backpressure) – 0:46 - 1:45**
   - Chọn Policy: `p4`, Scenario: `s2`. Bấm "BẮT ĐẦU CHẠY".
   - **Hiện tượng:** 
     - Lưới ô màu biến thiên mượt mà liên tục ở 60 fps.
     - Khi tải tăng vọt từ $1.0\times \to 2.0\times$, đồ thị thanh trạng thái hiển thị AIMD tự động co số worker từ 8 xuống 3-4 để nhường tài nguyên cho UI thread.
     - Người dùng chạm vào màn hình bất kỳ lúc nào: Nút bấm đổi màu ngay tức thì, đồng hồ thông báo **Độ trễ Critical: 28 ms**.
   - Kết quả xuất hiện: Missed Frame 0.75%, Jank 8%, Makespan 67s.

3. **Phần 3: So sánh Kết quả Tổng kết – 1:46 - 2:00**
   - Hiển thị bảng so sánh đối đầu giữa $P_0$ (Freeze, 68s trễ) và $P_4$ (Mượt 60fps, 28ms trễ).
