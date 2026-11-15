# TÀI LIỆU KỸ THUẬT & HƯỚNG DẪN THỰC NGHIỆM LIVE DEMO
## Đề tài: Tối Ưu Hóa Bộ Lập Lịch Tác Vụ Đa Luồng Thích Ứng Cho Ứng Dụng Di Động (Flutter)

---

## PHẦN 1: LÀM RÕ CÁC KHÁI NIỆM & TỪ KHÓA CỐT LÕI

Trước khi đi vào 5 chính sách lập lịch, cần nắm vững 4 khái niệm nền tảng trong môi trường thực thi của Flutter/Android:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   MÔ HÌNH THỰC THI (ISOLATE & THREADS)                 │
├──────────────────────────────────┬─────────────────────────────────────┤
│      MAIN ISOLATE (UI Thread)    │     BACKGROUND WORKER POOL          │
│                                  │                                     │
│  • Xử lý sự kiện cảm ứng (Touch) │  • Pool gồm W Isolate sống lâu      │
│  • Tính toán bố cục (Layout/Build│  • Chạy trên các CPU Core khác      │
│  • Gửi lệnh vẽ sang GPU Raster   │  • Xử lý tác vụ CPU-bound nặng      │
│  • Bị ràng buộc bởi Vsync 16.7ms │    (Decode ảnh, lọc ma trận, băm)   │
│                                  │                                     │
│         [Event Loop]             │     [Port Message Passing]          │
│         Tuần tự, non-preemptive  │     SendPort <---> ReceivePort      │
└──────────────────────────────────┴─────────────────────────────────────┘
```

### 1. Frame (Khung hình) & Ngân sách Vsync (16.67ms / 8.33ms)
* **Khung hình (Frame):** Màn hình điện thoại hoạt động như một máy chiếu phim, liên tục vẽ lại giao diện theo chu kỳ cố định gọi là tần số quét (Refresh Rate).
* **Ngân sách Vsync:** 
  * Màn hình chuẩn **60Hz**: Cứ sau $1000\text{ ms} / 60 \approx \mathbf{16.67\text{ ms}}$, màn hình yêu cầu một khung hình mới.
  * Màn hình cao cấp **120Hz**: Ngân sách rút xuống chỉ còn $\mathbf{8.33\text{ ms}}$.
* **Jank (Rớt khung hình / Giật lag):** Nếu Main Isolate bận tính toán một phép toán nặng mất $>16.67\text{ ms}$, nó không kịp gửi lệnh vẽ đến nhịp Vsync. Màn hình buộc phải hiển thị lại khung hình cũ $\to$ Giao diện bị đơ, con quay giật cục, cuộn trang bị khựng.

---

### 2. Main Isolate (Luồng giao diện)
* Là luồng chính thực thi mã nguồn Dart của ứng dụng.
* Hoạt động theo cơ chế **Đơn luồng - Vòng lặp sự kiện (Single-threaded Event Loop)**: Lấy từng sự kiện ra xử lý tuần tự (Nhận cảm ứng $\to$ Tính toán Widget $\to$ Render $\to$ Chạy Timer...).
* **Đặc tính:** Không thể bị ngắt ngang (*Non-preemptive*). Nếu một hàm tính toán CPU-bound chạy mất $500\text{ ms}$ trên Main Isolate, toàn bộ ứng dụng sẽ bị **đóng băng (Freeze) đúng $500\text{ ms}$ đó**.

---

### 3. Worker Pool (TRỌNG TÂM CỦA HỆ THỐNG)
* **Vấn đề của cách làm thông thường (`Isolate.run()` / `compute()`):** Mỗi khi có tác vụ, hệ thống lại khởi tạo một Isolate mới rồi hủy đi. Chi phí tạo mới một Isolate trên Android rất đắt đỏ: tốn **$25\text{ ms} – 80\text{ ms}$** và cấp phát hàng chục MB RAM, gây áp lực cực lớn lên bộ gom rác Garbage Collector (GC).
* **Worker Pool là gì?**
  * Là một tập hợp gồm $W$ **Isolate sống lâu (Long-running Isolates)** được tạo sẵn ngay khi ứng dụng khởi động (Pre-warmed).
  * Các Worker này nằm chờ sẵn ở chế độ nền trên các lõi CPU khác, không bao giờ bị hủy đi trong suốt vòng đời phiên làm việc.
* **Cơ chế giao tiếp (Message Passing):**
  * Dart Isolate không chia sẻ bộ nhớ (Share-nothing). Main Isolate và Worker trao đổi dữ liệu thông qua cặp cổng: `SendPort` (Gửi) và `ReceivePort` (Nhận).
* **Cơ chế hoạt động:**
  1. `acquire()`: Scheduler quét danh sách Worker trong Pool. Nếu thấy Worker nào có cờ `busy == false`, cấp Worker đó cho tác vụ. Nếu tất cả đều bận, tác vụ phải chờ trong Queue.
  2. `run(task)`: Đánh dấu `w.busy = true`, gửi mã tác vụ qua `SendPort`. Worker tính toán độc lập 100% trên lõi CPU riêng.
  3. `onDone(taskId)`: Worker tính xong, gửi tín hiệu về Main Isolate. Đánh dấu `w.busy = false` (giải phóng), sẵn sàng nhận tác vụ tiếp theo.

---

### 4. Phân cấp Tác vụ (Task Priority) & Phân vị Độ trễ ($p95$)
* Hệ thống phân loại tác vụ thành 3 mức độ ưu tiên:
  1. **Critical (Khẩn cấp):** Tác vụ phục vụ trực tiếp phản hồi tương tác người dùng (ví dụ: bấm mở chi tiết ảnh, bấm nút chuyển tab). **Yêu cầu độ trễ phản hồi $< 100\text{ ms}$**.
  2. **Interactive (Tương tác):** Tác vụ tải nội dung của các ô ảnh đang nằm trong tầm mắt nhìn thấy trên màn hình.
  3. **Background (Tác vụ nền):** Tác vụ tiền xử lý, nén ảnh, lưu cache, tính toán hàng loạt không yêu cầu người dùng thấy kết quả ngay.
* **Chỉ số $p95$ (Phân vị thứ 95):** Đại diện cho 95% trường hợp có thời gian phản hồi tốt hơn con số này. Nó phản ánh chính xác các cú giật lag tồi tệ nhất (Tail Latency) mà giá trị trung bình cộng thường che giấu.

---

## PHẦN 2: NĂM CHÍNH SÁCH LẬP LỊCH ($P_0 \to P_4$) — MÔ HÌNH TIẾN HÓA

Hệ thống được phát triển qua 5 nấc thang chính sách. Mỗi chính sách cấp cao ra đời là để **giải quyết trực tiếp một khiếm khuyết vật lý cụ thể** của chính sách tiền nhiệm.

```
P0 (Main Isolate) 
   │ [Nhược điểm: Block Main Thread]
   ▼
P1 (Fixed Worker Pool - FIFO)
   │ [Nhược điểm: Head-of-Line Blocking việc VIP bị kẹt sau việc nền]
   ▼
P2 (Priority Queue + Aging)
   │ [Nhược điểm: Tác vụ nền quá to chiếm giữ Worker, việc VIP không chen ngang được]
   ▼
P3 (Cooperative Chunking + Reserve + Frame Yielding)
   │ [Nhược điểm: Cấu hình tĩnh; khi quá tải bùng nổ hoặc máy nóng thì bão hòa]
   ▼
P4 (Adaptive AIMD + Degrade Mode Machine + Backpressure)
```

---

### 1. Chính sách $P_0$: Main Isolate (Baseline thấp nhất)
* **Cơ chế hoạt động:** Toàn bộ tác vụ nặng (decode ảnh, tính toán) đều được đẩy trực tiếp vào Event Loop của Main Isolate. Các tác vụ chạy tuần tự nối đuôi nhau ngay trên luồng vẽ giao diện.
* **Kỹ thuật áp dụng:** `Queue<Task>` đơn giản, dùng `Future.delayed(Duration.zero)` để nhường nhịp Event Loop giữa các task.
* **Ưu điểm:** Đơn giản nhất, không tốn tài nguyên quản lý luồng, không tốn chi phí đồng bộ hóa dữ liệu.
* **Nhược điểm:** **Đóng băng hoàn toàn giao diện (UI Freeze)**. Khi xử lý một ảnh mất $200\text{ ms}$, Main Isolate dừng mọi hoạt động vẽ khung hình $\to$ Tỷ lệ rớt khung hình vọt lên $>80\%$, FPS tụt về 5-10, con quay giao diện đứng yên.

---

### 2. Chính sách $P_1$: Fixed Worker Pool (Hàng đợi FIFO)
* **Cơ chế hoạt động:** Tạo ra một Worker Pool cố định ($W = 4$ Isolate chạy nền). Khi có tác vụ gửi đến, đưa vào hàng đợi `FIFO (First-In, First-Out)`. Bất kỳ Worker nào rảnh sẽ lấy tác vụ đầu tiên ra chạy trên lõi CPU riêng.
* **Kỹ thuật cốt lõi:** `WorkerPool` (tập các long-lived isolate), giao tiếp qua `SendPort / ReceivePort`.
* **Ưu điểm:** Giải phóng hoàn toàn tính toán nặng ra khỏi Main Isolate. Luồng UI rảnh tay để dựng hình.
* **Nhược điểm:**
  1. **Nghẽn đầu hàng (Head-of-Line Blocking):** Nếu có 50 tác vụ nền (Background) gửi vào trước, sau đó người dùng bấm xem 1 ảnh khẩn cấp (`Critical`), tác vụ Critical buộc phải xếp sau 50 tác vụ nền $\to$ Độ trễ `Crit p95` vọt lên **hàng chục giây**.
  2. **Tranh chấp CPU:** Cả 4 worker nền cùng chạy 100% công suất làm cạn kiệt tài nguyên CPU trên máy yếu, khiến luồng UI thỉnh thoảng vẫn bị hụt khung hình.

---

### 3. Chính sách $P_2$: Priority Queue + Aging (Hàng đợi Ưu tiên & Chống đói)
* **Mục tiêu sinh ra:** Khắc phục nhược điểm "Nghẽn đầu hàng" của $P_1$.
* **Cơ chế hoạt động:** Thay thế hàng đợi FIFO bằng **Hàng đợi ưu tiên 3 mức**. Tác vụ `Critical` được ưu tiên đưa lên trước để Worker lấy chạy ngay. Tác vụ Background chờ càng lâu sẽ được cộng điểm "thâm niên" (Aging) để thăng hạng dần.
* **Kỹ thuật cốt lõi:**
  * **Priority Queue 3 tầng:** Cấp độ `Critical (0) > Interactive (1) > Background (2)` lấy ra trong thời gian $O(1)$.
  * **Hàm toán học Aging:** $\text{Score} = \text{Rank} \times \tau_{\text{aging}} - \text{WaitTime}$. Nếu tác vụ nền chờ quá thời gian $\tau_{\text{aging}} = 3000\text{ ms}$, điểm của nó sẽ vượt qua tác vụ mới, đảm bảo **không một tác vụ nào bị bỏ đói vĩnh viễn (Zero Starvation)**.
* **Ưu điểm:** Tác vụ khẩn cấp `Critical` được nhảy hàng lên đầu, giảm đáng kể thời gian chờ đợi.
* **Nhược điểm (Rào cản vật lý):** Dart Isolate **không hỗ trợ cơ chế ngắt cưỡng bức (Non-preemptive)**. Nếu cả 4 Worker nền đang lỡ nhận 4 tác vụ lớn (mỗi tác vụ chạy mất $500\text{ ms}$), thì dù tác vụ `Critical` có đứng đầu hàng đợi, nó vẫn phải đứng chờ ít nhất cho đến khi có 1 Worker chạy xong hẳn tác vụ cũ.

---

### 4. Chính sách $P_3$: Chunking + Worker Reserve + Frame Yielding
* **Mục tiêu sinh ra:** Phá vỡ rào cản "không thể ngắt ngang" của Dart Isolate trong $P_2$.
* **Cơ chế hoạt động:**
  1. **Băm nhỏ tác vụ (Cooperative Chunking):** Không giao nguyên 1 tác vụ lớn cho Worker. Tác vụ được chia thành các lát cắt nhỏ có thời lượng $\Delta t \approx \mathbf{80\text{ ms}}$. Sau mỗi 80ms, Worker gửi kết quả về và giải phóng trạng thái $\to$ Tạo ra **Điểm chen ngang (Preemption Boundary)** cho tác vụ Critical.
  2. **Dự phòng Worker (Worker Reserve):** Số worker chạy việc thông thường luôn bị giới hạn: $N_{\text{non\_crit}} \le W - 1$. Hệ thống **luôn để dành sẵn ít nhất 1 Worker rảnh rỗi** chỉ chờ tác vụ `Critical`.
  3. **Nhường khung hình (Frame Yielding):** Main Isolate đo khoảng cách khung hình. Nếu UI có dấu hiệu trễ (vượt ngưỡng $20\text{ ms}$), hệ thống bật cờ hoãn không phát thêm việc Background.
* **Ưu điểm:** **Bước ngoặt hiệu năng**. `Crit p95` ngay lập tức tụt xuống dưới ngưỡng sinh tử **$< 100\text{ ms}$**. Tỷ lệ rớt khung hình UI tiệm cận về $0\%$.
* **Nhược điểm:** Toàn bộ tham số ($W=4$, chunk 80ms, reserve 1) là **cố định tĩnh**. Khi gặp tình huống tải đột biến cực hạn (Burst Load) hoặc thiết bị quá nhiệt (Thermal Throttling), hệ thống không tự thích nghi được.

---

### 5. Chính sách $P_4$: Adaptive AIMD + Mode Machine + Backpressure
* **Mục tiêu sinh ra:** Chuyển từ hệ thống cấu hình tĩnh ($P_3$) sang hệ thống **tự điều khiển thích ứng vòng đóng (Closed-loop Adaptive System)**, giải quyết triệt để vấn đề tranh chấp CPU khi có ứng dụng khác chạy ngầm hoặc khi chạy trên các thiết bị cấu hình khác nhau.

* **Bản chất kiến trúc cốt lõi:**
  * **Luồng UI (Main Isolate):** Ứng dụng **luôn chỉ có duy nhất 1 luồng chính** phụ trách toàn bộ giao diện và thao tác cảm ứng.
  * **Worker Pool:** Là các luồng phụ (Background Isolate) được tạo thêm **chỉ để tính toán nặng** (decode ảnh, lọc ma trận) nhằm giải phóng luồng UI.
  * **Bản chất luồng & CPU:** Isolate là luồng phần mềm. Hệ điều hành Android (Linux CFS) sẽ chịu trách nhiệm phân phối các Isolate này lên các nhân CPU vật lý.
  * **Vấn đề thực tế đặt ra:** Khi máy có **ứng dụng khác chạy ngầm** (Spotify, Zalo, sao lưu ảnh) hoặc khi máy nóng lên, CPU toàn hệ thống bị san sẻ bớt. Nếu bộ lập lịch cứ cố định chạy 4 worker nền ($P_1 - P_3$) thì tổng nhu cầu CPU sẽ vượt quá 100% $\to$ CPU bị nghẽn $\to$ Luồng chính UI bị cướp quyền ưu tiên gây giật lag (Jank).

* **Cơ chế vận hành thực tế của $P_4$ (Mô hình: Cảm biến $\to$ Bộ chỉ huy $\to$ Bộ não AIMD $\to$ Thi hành):**

```
┌────────────────────────────────────────────────────────────────────────┐
│                        QUY TRÌNH ĐIỀU PHỐI CỦA P4                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. CẢM BIẾN (FrameSignal):                                             │
│    • Cắm hook vào Flutter: SchedulerBinding.addPersistentFrameCallback │
│    • Đo khoảng cách giữa 2 khung hình UI liên tiếp: gapP95Ms           │
│    • Nếu UI bị đơ, Stopwatch đo ngay thời gian trễ tức thời (stall)    │
│                               │                                        │
│                               ▼                                        │
│ 2. BỘ CHỈ HUY (Vòng lặp Timer 100ms trong P4Scheduler):                │
│    • Cứ mỗi 100ms thức dậy kiểm tra sức khỏe UI một lần                │
│    • Lấy số đo gapP95Ms từ cảm biến                                    │
│    • TRỰC TIẾP GỌI: aimd.update(gapP95Ms) ──────────────────────────┐  │
│                                                                     │  │
│                                                                     ▼  │
│ 3. BỘ NÃO TÍNH TOÁN (AimdController): ◄─────────────────────────────┘  │
│    • So sánh gapP95Ms với ngưỡng an toàn targetGapMs (20ms):           │
│      - Nếu UI chớm nghẽn (> 20ms): Phanh gấp x 0.5 (cắt giảm 50% worker)│
│      - Nếu UI mượt mà (<= 16ms): Tăng từ tốn +1 worker sau mỗi 500ms    │
│      - Vùng đệm 16ms - 20ms: Giữ nguyên số worker chống rung             │
│    • Trả về con số trần Worker mới cho Scheduler                       │
│                               │                                        │
│                               ▼                                        │
│ 4. THI HÀNH ĐIỀU PHỐI (_dispatch()):                                   │
│    • Scheduler áp đặt ngay con số worker mới của AIMD                  │
│    • Khóa bớt các worker nền lại (không giao thêm việc)                │
│    • Trả ngay các nhân CPU vật lý cho Main Isolate hoàn thành frame UI │
└────────────────────────────────────────────────────────────────────────┘
```

* **Hai cơ chế phòng vệ bổ trợ trong $P_4$:**
  1. **Máy trạng thái môi trường (Mode Machine):**
     * Đọc cảm biến phần cứng qua `MethodChannel`: Nếu máy bị nóng ($\ge 38^\circ\text{C}$ chế độ `Conserve`, $\ge 42^\circ\text{C}$ chế độ `Critical`) hoặc pin yếu $\le 10\%$, hệ thống tự động khóa trần CPU (chỉ cho tối đa 1 worker chạy) để hạ nhiệt máy và chống sập nguồn (có trễ Hysteresis 5s chống chập chờn).
  2. **Cơ chế xả tải chống sập app (Backpressure & Load Shedding):**
     * Khi có quá nhiều việc dồn vào khiến hàng đợi phình to ($>20$ tác vụ nền), hệ thống tự động **hủy bỏ (Drop)** các tác vụ nền cũ đến muộn mà người dùng chưa cuộn tới, ngăn chặn triệt để nguy cơ tràn RAM (Out of Memory - OOM).

* **Ưu điểm:** Khả năng tự thích ứng tuyệt đối: máy mạnh tự động mở thêm worker, máy yếu hoặc máy đang bị app khác chạy ngầm thì tự động co cụm worker để bảo vệ trải nghiệm 60 FPS của người dùng.
* **Nhược điểm:** Hệ thống cần tinh chỉnh chu kỳ lấy mẫu (pacing epoch 500ms) để giữ trạng thái cân bằng động ổn định.

---

## BẢNG SO SÁNH TỔNG HỢP 5 CHÍNH SÁCH

| Tiêu chí | $P_0$ (Main Isolate) | $P_1$ (Pool FIFO) | $P_2$ (Priority + Aging) | $P_3$ (Chunk + Reserve) | $P_4$ (Adaptive AIMD) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Nơi tính toán** | Main Isolate | Worker Pool | Worker Pool | Worker Pool | Worker Pool |
| **Số Worker** | 1 (UI Thread) | 4 (Cố định) | 4 (Cố định) | 4 (Chừa 1 cho VIP) | **1 – 4 (Co giãn AIMD)** |
| **Cấu trúc hàng đợi** | Đơn luồng | FIFO | 3 cấp + Aging | 3 cấp + Aging | 3 cấp + Backpressure |
| **Cắt nhỏ tác vụ** | Không | Không | Không | **Có ($\approx 80\text{ ms}$)** | **Có ($\approx 80\text{ ms}$)** |
| **Bảo vệ tác vụ VIP** | Không | Không | Ưu tiên chờ | **Worker riêng + Chen ngang**| **Ưu tiên + Bảo vệ tuyệt đối** |
| **Tự thích ứng tải** | Không | Không | Không | Không | **Có (AIMD + Nhiệt/Pin)** |
| **Tỷ lệ rớt Frame** | Rất cao ($>80\%$) | Trung bình ($15-25\%$) | Khá ($10-18\%$) | **Rất thấp ($< 1\%$)** | **Gần như $0\%$** |
| **Độ trễ VIP (`Crit p95`)** | Hàng chục giây | Hàng chục giây | 300 – 800ms | **$< 100\text{ ms}$** | **$< 80\text{ ms}$** |

---

## PHẦN 3: KỊCH BẢN THỰC NGHIỆM LIVE DEMO TRỰC TIẾP TRÊN ỨNG DỤNG ẢNH

> **Mục tiêu của phần Demo:** Chứng minh bằng mắt thấy tai nghe sự khác biệt giữa các chính sách trên **chính lưới ảnh thật (Photo Gallery)** của ứng dụng.

---

### BỐ CỤC MÀN HÌNH DEMO TƯƠNG TÁC (3 KHU VỰC TRỰC QUAN):
1. **Khu vực Trung tâm (Lưới ảnh Photo Grid):** 
   * Mở khóa cho ngón tay vuốt lướt tự do. 
   * **Mỗi ô ảnh có thể chạm vào được:** Khi bạn chạm vào ô ảnh nào, ô đó sẽ gửi ngay 1 tác vụ khẩn cấp (Critical) để giải mã chất lượng cao và hiển thị thời gian mở ảnh ngay trên góc ô ảnh đó!
2. **Khu vực Góc trên (Monitor HUD v2):**
   * Hiển thị thời gian thực FPS, Frame Time, độ trễ mở ảnh `CRIT P95`, thanh CPU Worker slots, trạng thái Mode/Yielding.
3. **Khu vực Góc dưới (Demo Control Dock):**
   * **Dải nút chọn nhanh 5 Chính sách:** `[ P0 | P1 | P2 | P3 | P4 ]` (bấm đổi chính sách ngay lập tức, không cần khởi động lại app).
   * **Nút bấm kích hoạt tải:**
     * `⚡ Nạp 30 ảnh`: Bơm 30 tác vụ giải mã ảnh nền vào hàng đợi.
     * `🔥 Bão tải 60`: Bơm 60 tác vụ dồn dập để thử thách độ bền hệ thống.
     * `🗑️ Xóa`: Dọn sạch hàng đợi.

---

### KỊCH BẢN 5 MÀN TRÌNH DIỄN (THAO TÁC TẬN TAY — MẮT THẤY TAI NGHE):

#### MÀN 1: DEMO CHÍNH SÁCH $P_0$ (Chưa tối ưu — Đơn luồng Main Isolate)
* **Ý nghĩa khoa học:** Cho thấy tác hại của việc xử lý ảnh nặng ngay trên Main Isolate làm phong tỏa Vòng lặp sự kiện (Event Loop).
* **Thao tác:**
  1. Bấm nút **`P0`** ở thanh điều khiển dưới màn hình.
  2. Bấm nút **`⚡ Nạp 30 ảnh`**.
  3. Lấy ngón tay vuốt lướt màn hình và chạm thử vào 1 ô ảnh.
* **Hiện tượng mắt thấy tai nghe:**
  * **Con quay Spinner ở góc trên CHẾT CỨNG ĐỨNG YÊN** rõ ràng từng nhịp 0.3s – 0.5s!
  * Thao tác vuốt ngón tay bị tê liệt, chạm vào ô ảnh **không có phản hồi** vì Main Isolate đang bị nghẽn decode.
  * Toàn bộ cột Frame Time trên HUD biến thành **màu ĐỎ rực** vọt lên $>200\text{ ms}$, FPS tụt thảm hại còn **`4 – 8 FPS`**, Miss **`>80%`**.
* **Lời nói với Thầy Cô:**
  > *"Kính thưa Thầy Cô, ở P0 khi không dùng đa luồng, mỗi bức ảnh nền chiếm trọn Main Isolate 300ms khiến con quay và thao tác chạm của người dùng bị đóng băng hoàn toàn."*

---

#### MÀN 2: DEMO CHÍNH SÁCH $P_1$ (Đưa ra Worker Pool nhưng dùng hàng đợi FIFO)
* **Ý nghĩa khoa học:** Đưa việc ra luồng phụ đã cứu được giao diện, nhưng bộc lộ nhược điểm **Nghẽn đầu hàng (Head-of-Line Blocking)**.
* **Thao tác:**
  1. Bấm nút **`P1`**.
  2. Bấm nút **`⚡ Nạp 30 ảnh`** (Hàng đợi `Queue` trên HUD nhảy lên 30).
  3. **Lấy ngón tay chạm ngay vào ô ảnh `#12`**.
* **Hiện tượng mắt thấy tai nghe:**
  * Con quay Spinner đã quay được mượt mà (chứng minh tính toán đã ra khỏi luồng chính).
  * **NHƯNG:** Ô ảnh `#12` hiện vòng xoay nhỏ quay chờ... và bạn phải **đợi mòn mỏi 5 – 8 giây sau ảnh mới mở được!**
  * Khi mở xong, ô ảnh hiện nhãn màu ĐỎ: **`⏳ 6.2s`** (và chỉ số `CRIT P95` trên HUD báo đỏ hàng nghìn ms).
* **Lời nói với Thầy Cô:**
  > *"Thưa Thầy Cô, ở P1 giao diện đã hết đơ, nhưng do dùng hàng đợi FIFO nên yêu cầu mở ảnh của người dùng bị xếp sau 30 bức ảnh nền, khiến người dùng phải chờ tới hơn 6 giây mới xem được ảnh!"*

---

#### MÀN 3: DEMO CHÍNH SÁCH $P_2$ (Hàng đợi Ưu tiên Priority Queue + Aging)
* **Ý nghĩa khoa học:** Khắc phục nghẽn đầu hàng của P1, nhưng vấp phải rào cản **Dart Isolate không thể bị ngắt ngang**.
* **Thao tác:**
  1. Bấm nút **`P2`**.
  2. Bấm nút **`⚡ Nạp 30 ảnh`**.
  3. **Lấy ngón tay chạm vào ô ảnh `#15`**.
* **Hiện tượng mắt thấy tai nghe:**
  * Nhanh hơn P1 rất nhiều (không còn phải chờ 6 giây), nhưng **vẫn bị khựng sượng khoảng nửa giây (300 – 600ms)** mới mở được.
  * Ô ảnh hiện nhãn màu VÀNG: **`⏳ 450ms`**.
* **Lời nói với Thầy Cô:**
  > *"Ở P2, tác vụ mở ảnh đã được ưu tiên nhảy lên đầu hàng. Tuy nhiên, vì Dart Isolate không hỗ trợ ngắt cưỡng bức, cú chạm của em vẫn phải chờ 1 trong 4 worker làm xong hẳn bức ảnh nền 500ms dở dang thì mới được phục vụ."*

---

#### MÀN 4: DEMO CHÍNH SÁCH $P_3$ (Cooperative Chunking 80ms + Worker Reserve)
* **Ý nghĩa khoa học:** Bẻ gãy rào cản không thể ngắt bằng cách băm nhỏ việc 80ms và luôn dành 1 worker dự phòng cho tương tác người dùng.
* **Thao tác:**
  1. Bấm nút **`P3`**.
  2. Bấm nút **`⚡ Nạp 30 ảnh`**.
  3. **Lấy ngón tay chạm vào ô ảnh `#20`**.
* **Hiện tượng mắt thấy tai nghe:**
  * **CHẠM PHÁT MỞ NGAY TỨC THÌ (<80ms)!**
  * Ô ảnh nhấp nháy sáng viền xanh và hiện nhãn xanh lá: **`⚡ 42ms`**!
  * Chỉ số `CRIT P95` trên HUD xẹp xuống xanh mướt **`< 80ms`**, biểu đồ Frame Time nằm phẳng dưới vạch $16.7\text{ ms}$, đạt chuẩn **60 FPS** tròn trĩnh.
* **Lời nói với Thầy Cô:**
  > *"Nhờ băm nhỏ việc nền thành các lát cắt 80ms tạo điểm chen ngang và luôn dự phòng sẵn 1 worker rảnh rỗi, cú chạm mở ảnh của người dùng đạt phản hồi tức thì dưới 50ms, đáp ứng hoàn hảo tiêu chuẩn tương tác thời gian thực!"*

---

#### MÀN 5: THỬ THÁCH BÃO TẢI $P_3$ VS $P_4$ (Cấu hình tĩnh vs Thích ứng tự động AIMD)
* **Ý nghĩa khoa học:** Chứng minh điểm yếu của cấu hình tĩnh $P_3$ khi quá tải, và sự vượt trội của hệ thống tự lái $P_4$.
* **Thao tác 1 (Thử thách trên $P_3$):**
  1. Đang ở **`P3`**, bấm nút **`🔥 Bão tải 60`**.
  2. Lấy ngón tay **vuốt cuộn lưới ảnh thật nhanh lên xuống liên tục**.
  3. **Hiện tượng:** Thao tác vuốt bị **sượng tay, giật cục**, FPS tụt xuống **`35 – 45 FPS`**, cột Frame Time trên HUD đổi sang màu Vàng/Đỏ (do 4 worker nền chạy 100% CPU làm nghẽn luồng vẽ UI).
* **Thao tác 2 (Xem $P_4$ tự động cứu hệ thống):**
  1. Bấm chuyển sang **`P4`**, bấm nút **`🔥 Bão tải 60`**.
  2. Lấy ngón tay **vuốt cuộn lưới ảnh thật nhanh lên xuống liên tục**.
  3. **Hiện tượng mắt thấy kinh ngạc:**
     * Mắt nhìn vào thanh Worker Pool trên HUD: Ngay khi ngón tay bạn đang cuộn, AIMD lập tức phanh gấp, **khóa bớt 3 worker lại `1/1 (AIMD khóa 3) 🔒`**!
     * Thao tác vuốt cuộn của bạn **MƯỢT NHƯ LỤA CHUẨN 60 FPS** (cột Frame Time xanh mướt)!
     * Khi bạn **buông tay ra không vuốt nữa** (UI rảnh) $\to$ Số worker trên màn hình tự động nhảy tăng trở lại: **1 $\to$ 2 $\to$ 4** để giải quyết nốt việc nền!
     * Ô **`🛡️ Drop`** tự động nhảy số (Backpressure xả bớt việc nền cũ ở xa, chống tràn RAM).
* **Lời nói kết thúc đắt giá trước Hội đồng:**
  > *"Kính thưa Thầy Cô, qua màn thử thách bão tải vừa rồi, sự khác biệt giữa P3 và P4 hiện lên rõ rệt nhất:
  > - Ở P3 cấu hình tĩnh, máy bị giật lag và tụt khung hình khi người dùng vuốt nhanh trong lúc tải nặng.
  > - Nhưng ở P4, hệ thống như **'biết thở' theo ngón tay của người dùng**: vuốt tay thì worker tự động co lại để giữ mượt 60 FPS; buông tay thì worker tự động bung xõa để hoàn thành việc nền. Đây chính là giá trị cốt lõi của bộ điều khiển thích ứng AIMD!"*

---

## TỔNG KẾT BÀI NÓI (KẾT LUẬN 1 PHÚT)
> *"Kính thưa Thầy Cô và Hội đồng, qua 4 màn demo thực nghiệm vừa rồi, chúng em đã chứng minh rõ: 
> 1. Để ứng dụng mượt mà, việc chỉ đẩy tác vụ ra Isolate chạy nền ($P_1$) là chưa đủ.
> 2. Chìa khóa để đạt Zero-Jank và độ trễ phản hồi dưới 100ms nằm ở sự phối hợp giữa **Phân mảnh hợp tác 80ms (Cooperative Chunking)** và **Dự phòng luồng khẩn cấp ($P_3$)**.
> 3. Cuối cùng, với **Bộ điều khiển thích ứng AIMD và Xả tải Backpressure ($P_4$)**, ứng dụng có khả năng tự bảo vệ và hoạt động bền bỉ ngay cả trong điều kiện quá tải khắc nghiệt nhất."*
