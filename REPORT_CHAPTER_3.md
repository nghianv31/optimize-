# CHƯƠNG 3: KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ ĐÓNG GÓP

## 3.1. Thiết lập Thực nghiệm & Phương pháp Đo lường

Các thực nghiệm được tiến hành trên thiết bị di động cấu hình phổ thông nhằm kiểm chứng các giả thuyết trong điều kiện phần cứng khắc nghiệt nhất:
- **Thiết bị thử nghiệm:** Samsung Galaxy A04e (Model `SM-A042F`), vi xử lý MediaTek Helio P35 (8 nhân Cortex-A53: 4 nhân 2.3 GHz + 4 nhân 1.8 GHz), RAM 2 GB (khả dụng ~700 MB), hệ điều hành Android 14 (One UI Core 6.0).
- **Môi trường đo lường:** Ứng dụng Flutter được biên dịch ở chế độ **Profile mode** (biên dịch AOT tối ưu, tắt toàn bộ debug assertions). Lưới UI hiển thị động gồm 16 ô màu biến đổi theo pha sóng sin và đồng hồ bấm giờ chạy ở tốc độ 60 fps.
- **Quy trình chuẩn hóa:** Thiết bị được kết nối qua ADB không dây/USB, pin luôn duy trì trên 40%, nhiệt độ pin khởi đầu được kiểm soát dưới 36°C. Mỗi lượt chạy tự động trải qua: Settle (10s) $\to$ Warmup (10s không ghi nhận) $\to$ Đo chính thức (60s) $\to$ Xuất file CSV và Metadata $\to$ Nghỉ nguội giữa các lượt đo.
- **Phương pháp phân tích:** Do các chỉ số độ trễ và thời gian dựng frame phân phối lệch (skewed distribution), toàn bộ báo cáo sử dụng **Trung vị (Median)**, **Khoảng tứ phân vị (IQR = Q75 - Q25)** và khoảng biến thiên $[Min - Max]$. Ý nghĩa thống kê được xác nhận thông qua kiểm định phi tham số **Mann-Whitney U** với mức ý nghĩa $\alpha = 0.05$.

---

## 3.2. Kiểm chứng Giả thuyết H1: Nghẽn Main Isolate và Hiệu quả của WorkerPool ($P_0$ vs $P_1$)

*Giả thuyết H1: Việc thực thi các tác vụ tính toán nặng trên Main Isolate ($P_0$) sẽ làm tê liệt vòng lặp dựng hình; chuyển tác vụ ra WorkerPool Isolate ($P_1$) sẽ khôi phục khả năng dựng frame mượt mà.*

### Kết quả đo lường (Kịch bản S1, $L=64, W=8, C=80$, $n=4$):
- **Chính sách $P_0$ (Main Isolate):** Tỷ lệ frame bị bỏ rơi (**Missed Frame**) lên tới **90.8%** [91–91%], khoảng cách giữa các frame dựng được ($gap_{p95}$) kéo dài đến **419.3 ms** (tương đương tốc độ hiển thị tụt xuống dưới 3 fps). Độ trễ tác vụ critical trung vị là **68,483 ms** (~68.5 giây) và thời gian chờ của tác vụ nền lên tới **81,719 ms**.
- **Chính sách $P_1$ (WorkerPool FIFO):** Khi chuyển sang pool 8 worker isolates, tỷ lệ missed frame giảm xuống **23.2%** [22–24%], $gap_{p95}$ đạt **48.2 ms**. Tỷ lệ hoàn thành tác vụ tăng từ **16.6% lên 86.5%**.

> **Kiểm định thống kê:** Kiểm định Mann-Whitney U giữa $P_0$ và $P_1$ về tỷ lệ Missed Frame cho thấy sự khác biệt vượt trội có ý nghĩa thống kê cao ($U = 16.0, p = 0.014 < 0.05$).  
> **Kết luận:** **Chấp nhận Giả thuyết H1**. Việc phân tách tác vụ nặng ra Isolate nền là điều kiện tiên quyết để giải cứu vòng lặp UI.

---

## 3.3. Kiểm chứng Giả thuyết H2: Giới hạn của Pool Cố định Dưới Tải Cao ($P_1$)

*Giả thuyết H2: Trong môi trường phần cứng hạn chế (8 nhân Cortex-A53), việc tăng số worker Isolate ($N$) trong một pool FIFO cố định không giải quyết được hiện tượng nghẽn đầu hàng (Head-of-Line Blocking) khi tải bão hòa, đồng thời gây gia tăng tranh chấp CPU với UI thread.*

### Kết quả đo lường:
1. Ở mức tải trung bình ($L=32$), việc tăng worker từ $W=6$ lên $W=8$ giúp độ trễ critical giảm từ 131 ms xuống 36 ms do có đủ nhân tính toán rảnh.
2. Tuy nhiên, khi tải vượt ngưỡng bão hòa ($L=64$, nhu cầu tính toán vượt xa năng lực của 8 nhân CPU):
   - Ngay cả khi cấp tối đa 8 worker, chính sách $P_1$ vẫn để xảy ra **23.2% missed frames** và **9.9% jank frames**.
   - Do tuân theo cơ chế FIFO không phân biệt độ ưu tiên, một tác vụ quan trọng (Critical Task - mô phỏng thao tác chạm của người dùng) phải xếp hàng sau các tác vụ nền khổng lồ, dẫn đến **độ trễ critical $p95$ vọt lên 35,356 ms (hơn 35 giây)**.

> **Kết luận:** **Ủng hộ Giả thuyết H2**. Tăng số lượng worker trong cơ chế FIFO chỉ có tác dụng khi tải chưa bão hòa; khi hệ thống quá tải, pool cố định hoàn toàn thất bại trong việc bảo vệ độ trễ tương tác người dùng.

---

## 3.4. Kiểm chứng Giả thuyết H3: Vai trò của Ưu tiên, Chunking và Nhường Frame ($P_1 \to P_2 \to P_3$)

*Giả thuyết H3: Cơ chế hàng đợi ưu tiên kèm aging ($P_2$), kết hợp chia nhỏ tác vụ (chunking), dành riêng worker dự phòng và chủ động nhường frame ($P_3$) sẽ triệt tiêu độ trễ critical và đưa tỷ lệ rớt frame về mức tương đương baseline không tải.*

### Bảng đối đầu chi tiết (Kịch bản S1, $n=4$ mỗi chính sách):

| Chính sách | Missed Frame (%) | Frame Jank (%) | Critical Latency p95 (ms) | Background Max Wait (ms) | Tỷ lệ hoàn thành (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **NONE (Baseline)** | 0.9% [1–1%] | 2.2% [0–3%] | – | – | – |
| **P1 (FIFO)** | 23.2% [22–24%] | 9.9% [9–11%] | 35,356.5 ms [33.8–37.1s] | 39,621.5 ms | 86.5% |
| **P2 (Priority + Aging)** | 22.4% [21–24%] | 10.0% [9–10%] | 22,760.5 ms [21.6–24.2s] | 39,027.0 ms | 90.4% |
| **P3 (Chunk + Yield)** | **0.8% [1–1%]** | 17.0% [16–19%] | **31.0 ms [28–35 ms]** | 46,886.0 ms | 77.1% |

### Phân rã Đóng góp Kiến trúc (Ablation Study):
- **Chính sách $P_2$ (Ưu tiên đơn thuần):** Độ trễ critical giảm từ 35.4s xuống 22.8s ($p = 0.014$), nhưng vẫn ở mức hàng chục giây. Lý do: Một khi 8 worker đang bận thực thi các tác vụ nền chưa kết thúc (không thể dừng giữa chừng), tác vụ critical dù đứng đầu hàng đợi vẫn phải chịu hiện tượng nghẽn đầu hàng.
- **Chính sách $P_{3c}$ (Thêm Chunking 80ms):** Cắt nhỏ tác vụ thành các chunk ~80ms giúp worker liên tục giải phóng sau mỗi chunk. Tỷ lệ rớt frame lập tức giảm sốc từ **22.2% xuống 0.8%**.
- **Chính sách $P_{3r}$ (Thêm Critical Worker Reserve):** Dành riêng 1 worker dự phòng trong pool cho tương tác $\to$ Độ trễ critical giảm từ **44.8 giây xuống 49 ms** (giảm gần 1.000 lần).
- **Chính sách $P_3$ hoàn chỉnh (+ Frame Yielding):** Khi nhịp frame bị trễ, scheduler tạm dừng gửi tác vụ nền để nhường CPU cho UI thread $\to$ Độ trễ critical đạt mức tối ưu tuyệt đối: **31.0 ms**.

> **Kiểm định thống kê:** So sánh giữa $P_1$ và $P_3$ cho thấy:
> - Tỷ lệ Missed Frame giảm từ 23.2% xuống 0.8% ($U = 16.0, p = 0.014 < 0.05$).
> - Độ trễ Critical giảm từ 35.4 giây xuống 31.0 ms ($U = 16.0, p = 0.014 < 0.05$).  
> **Kết luận:** **Chấp nhận Giả thuyết H3**. Sự kết hợp giữa Chunking và Worker Reserve là giải pháp triệt để duy nhất giải quyết bài toán tương tác thời gian thực trên Flutter.

---

## 3.5. Kiểm chứng Giả thuyết H4: Thích ứng Động AIMD và Backpressure Trên Kịch bản S2 ($P_4$ vs $P_3$)

*Giả thuyết H4: Khi chịu tải biến động và tăng đột biến (Kịch bản S2: 4 bậc thang từ $0.25\times \to 2.0\times$), thuật toán AIMD co/giãn worker động kết hợp Backpressure (load shedding) sẽ giúp loại bỏ hiện tượng jank UI do nghẽn CPU, đồng thời rút ngắn makespan nhờ hủy bỏ các tác vụ nền dồn ứ.*

### Bảng kết quả thực nghiệm Kịch bản S2 ($L=32, W=8, C=80$, $n=3$ mỗi chính sách):

| Chỉ số đánh giá | P1 (FIFO) | P3 (Chunk + Priority) | P4 (AIMD + Backpressure) | Đánh giá so sánh ($P_4$ vs $P_3$) |
| :--- | :---: | :---: | :---: | :--- |
| **Missed Frame (%)** | 5.1% [5–5%] | **0.7% [1–1%]** | **0.8% [1–1%]** | Ngang nhau, duy trì mượt mà ~60fps |
| **Jank Frame (%)** | 4.8% [4–8%] | 24.8% [18–26%] | **8.0% [0–10%]** | **P4 giảm jank hơn 3 lần** ($U=9.0, p=0.050$) |
| **Critical Latency p95**| 4,744.0 ms | 34.0 ms | **28.0 ms [27–30 ms]** | **Nhanh nhất toàn diện** (nhanh hơn P1 169 lần) |
| **Makespan (Tổng thời gian)**| 67,839 ms | 77,736 ms | **67,865 ms** | **P4 nhanh hơn P3 gần 10 giây** ($p=0.050$) |
| **Tác vụ nền bị hủy (Dropped)**| 0 | 0 | **1,990 tasks** | Cơ chế Backpressure loại bỏ task ứ đọng |

### Cơ chế hoạt động của $P_4$:
1. **AIMD Pacing phản ứng theo frame:** Khi bước vào pha 4 của kịch bản S2 (tải đỉnh $2.0\times$), $P_3$ vẫn cố chấp duy trì 8 workers làm việc liên tục khiến GPU và UI rasterizer bị cạnh tranh dữ dội $\to$ **Jank% của $P_3$ tăng vọt lên 24.8%**. Ngược lại, $P_4$ phát hiện thời gian render vượt ngưỡng 16.7ms và tự động co giới hạn worker nền xuống $1-2$ workers, giữ cho tỷ lệ jank chỉ ở mức **8.0%** (có run đạt mức lý tưởng **0.25%**).
2. **Cô lập Critical Worker độc lập:** Nhờ quy tắc cô lập trần AIMD chỉ áp dụng cho non-critical, tác vụ chạm người dùng ở $P_4$ luôn chiếm dụng ngay worker rảnh rỗi mà không bị ảnh hưởng bởi việc co worker nền, đạt kỷ lục **28.0 ms**.
3. **Backpressure / Load Shedding:** Ở pha $2.0\times$, hàng nghìn tác vụ nền phát sinh vượt quá khả năng xử lý. $P_4$ tự động loại bỏ 1,990 tác vụ nền hết hạn, ngăn chặn hoàn toàn nguy cơ tràn bộ nhớ RAM (OOM) và giúp toàn bộ kịch bản kết thúc ở 67.8s (nhanh hơn P3 10 giây).

> **Kết luận:** **Chấp nhận Giả thuyết H4**. AIMD kết hợp Backpressure là mô hình tối ưu toàn diện cho các thiết bị di động phân khúc giá rẻ khi đối mặt với tải bùng nổ.

---

## 3.6. Đo lường Overhead của Khung Lập lịch (Microbenchmark E3)

Để chứng minh các cơ chế điều phối phức tạp của $P_3$ và $P_4$ không gây hao tổn tài nguyên của Main Isolate, thực nghiệm đo lường overhead độc lập trên 200 lượt điều phối tác vụ nhẹ:
- **Round-trip Dispatch Latency $p50$:** **0.34 ms** (345 µs).
- **Round-trip Dispatch Latency $p95$:** **0.47 ms** (467 µs).
- **Round-trip Dispatch Latency $p99$:** **0.73 ms** (730 µs).

> **Nhận xét:** Ngân sách cho 1 khung hình ở tần số quét 60Hz là $16.67\text{ ms}$. Tổng overhead truyền nhận thông điệp qua SendPort/ReceivePort và xếp hàng ưu tiên chỉ chiếm **~2.0% ngân sách frame**, hoàn toàn nằm trong ngưỡng vô hình đối với mắt người dùng.

---

## 3.8. Đánh giá Khả năng Khái quát hóa Liên Thiết bị (Cross-Device: Galaxy A04e vs Redmi Note 13 120Hz)

Để kiểm chứng khả năng áp dụng rộng rãi của khung lập lịch và bác bỏ nguy cơ "overfitting trên một cấu hình phần cứng duy nhất", nghiên cứu mở rộng toàn bộ ma trận thực nghiệm lên thiết bị tầm trung thế hệ mới: **Xiaomi Redmi Note 13** (Helio G99, 6GB RAM, Android 15, màn hình **120Hz** với ngân sách frame ngặt nghèo **8.33 ms**).

### Bảng So sánh Đối đầu Thực nghiệm giữa Hai Thế hệ Thiết bị:

#### 1. Kịch bản Tải bão hòa S1 (A04e $L=64$ vs Note 13 $L=256$, $W=8, C=80$):
| Thiết bị & Chính sách | Missed Frame (%) | Jank Frame (%) | Frame Gap p95 (ms) | Critical Latency p95 (ms) |
| :--- | :---: | :---: | :---: | :---: |
| **A04e (60Hz, Helio P35)** | | | | |
| • NONE (Baseline) | 0.9% | 2.2% | 18.3 ms | – |
| • P0 (Main Isolate) | 90.8% | 0.0% | 419.3 ms | 68,483 ms |
| • P1 (FIFO Pool) | 23.2% | 9.9% | 48.2 ms | 35,356 ms |
| • P2 (Priority + Aging) | 22.4% | 10.0% | 42.9 ms | 22,760 ms |
| • **P3 (Chunk + Priority)** | **0.8%** | 17.0% | **18.2 ms** | **31.0 ms** (Giảm >1.100x) |
| **Redmi Note 13 (120Hz, Helio G99)** | | | | |
| • NONE (Baseline) | 1.19% | 0.07% | 8.47 ms | – |
| • P0 (Main Isolate) | 95.97% | 0.17% | 316.2 ms | – (Tê liệt hoàn toàn) |
| • P1 (FIFO Pool) | 61.59% | 34.73% | 54.8 ms | 63,278 ms (~63.3s) |
| • P2 (Priority + Aging) | 59.59% | 32.12% | 54.8 ms | 39,351 ms |
| • **P3 (Chunk + Priority)** | **1.21%** | **0.12%** | **8.44 ms** | **29.0 ms** (Giảm >2.180x) |

#### 2. Kịch bản Tải bậc thang S2 (A04e $L=32$ vs Note 13 $L=128$, $W=8, C=80$):
| Thiết bị & Chính sách | Missed Frame (%) | Jank Frame (%) | Critical Latency p95 (ms) | Makespan (ms) | Background Dropped |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **A04e (60Hz, Helio P35)** | | | | | |
| • P1 (FIFO Pool) | 5.1% | 4.8% | 4,744 ms | 67,839 ms | 0 |
| • P3 (Chunk + Priority) | 0.7% | 24.8% | 34.0 ms | 77,736 ms | 0 |
| • **P4 (AIMD + Backpressure)** | **0.8%** | **8.0%** | **28.0 ms** | **67,865 ms** (Sớm ~10s) | **1,990 tasks** |
| **Redmi Note 13 (120Hz, Helio G99)** | | | | | |
| • P1 (FIFO Pool) | 33.51% | 13.18% | 33,501 ms | 91,680 ms | 0 |
| • P3 (Chunk + Priority) | 1.19% | 0.14% | 29.0 ms | 91,576 ms | 0 |
| • **P4 (AIMD + Backpressure)** | **1.22%** | **0.03%** | **25.0 ms** | **60,981 ms** (Sớm ~30.6s) | **5,607 tasks** |

### Kết luận Rút ra từ So sánh Liên thiết bị:
1. **Quy luật bất biến của FIFO Pool ($P_1$):** Dù thiết bị mạnh gấp 4 lần (Helio G99) và có 6GB RAM, việc dùng pool FIFO cố định vẫn gây nghẽn nghiêm trọng (độ trễ critical lên tới **33.5 giây ở S2** và **63.3 giây ở S1**), đồng thời làm rớt hơn **33% đến 61%** tổng số khung hình 120Hz.
2. **Hiệu quả triệt để của $P_3$ trên màn 120Hz:** Ngay cả khi ngân sách khung hình bị siết chặt còn **8.33 ms** (thay vì 16.67ms ở 60Hz), $P_3$ vẫn duy trì tỷ lệ rớt frame ở mức **1.21%** (trùng khớp hoàn hảo với baseline không tải 1.19%) và hạ độ trễ critical về **29.0 ms** (nhanh hơn $P_1$ **2.180 lần**).
3. **Giá trị của AIMD & Backpressure ($P_4$):** Trên Redmi Note 13, $P_4$ dập tắt hoàn toàn hiện tượng jank (chỉ còn **0.03%**), đưa độ trễ critical về mức kỷ lục **25.0 ms**, và cơ chế load shedding giúp toàn bộ kịch bản kết thúc đúng thời hạn 60.9s (nhanh hơn $P_1$ và $P_3$ hơn **30.6 giây**). Điều này khẳng định $P_4$ thích ứng linh hoạt và mang lại hiệu quả vượt bậc trên cả thiết bị 60Hz giá rẻ và 120Hz tầm trung.

---

## 3.9. Thực nghiệm Tác vụ Ảnh Thực tế (`s_image` — Phương án A: I/O + JPEG/Pixel từ Bộ ảnh Assets)

Để bác bỏ nghi ngờ kết quả chỉ đúng trên vòng lặp CPU thuần (`synthetic burn`) mà chưa phản ánh chi phí đọc file thật và giải tích cấu trúc ảnh từ bộ nhớ ngoài, nghiên cứu bổ sung kịch bản **`s_image`** theo **Phương án A** (đẩy ảnh ngoài qua ADB thay vì đóng gói 1,5+ GB vào APK).

### Thiết lập Bộ dữ liệu và Tác vụ Ảnh Thực tế
- **Nguồn ảnh:** Chọn **80 ảnh DSLR JPEG đại diện** (`img_00.jpg`–`img_79.jpg`, độ phân giải `6016×4016`, dung lượng `5.85–12.48 MB`/ảnh) từ tập 179 ảnh trong thư mục `assets/`, đồng bộ vào bộ nhớ nội bộ của ứng dụng tại `/data/user/0/com.example.optimize/files/images/`.
- **Giao diện hiển thị trực tiếp (`PhotoGrid`):** Lưới cuộn 3 cột nạp trực tiếp 80 ảnh thật, giải mã thumbnail tối ưu (`cacheWidth: 240`) để vừa tái hiện áp lực dựng hình đa phương tiện thực tế, vừa triệt tiêu nguy cơ tràn RAM bitmap 24MP.
- **Xử lý ngầm (`lib/workload/image_workload.dart`):** Mỗi chunk mở file ảnh thật bằng `RandomAccessFile` (trong `try/finally`), đọc header JPEG (`SOI`/`SOF0`/`SOF2`) để trích xuất kích thước ảnh, đọc tối đa lát dữ liệu `256 KB` theo vị trí chunk hiện tại, tính histogram 256 mức và năng lượng khối điểm ảnh kết hợp vòng lặp kiểm soát tải (`iters`).
- **Cấu hình chạy:** Kịch bản 4 pha bậc thang (`0.25x → 0.5x → 1.0x → 2.0x`) + 8 tác vụ critical (`total = 2,130` tác vụ) trên **`emulator-5554`** (`4 vCPUs`, `60 Hz`, Profile mode), tham số `L=16, W=4, C=80 ms, duration=30s`, lặp ngẫu nhiên `n=2` mỗi chính sách (`12` lượt chạy sạch).

### Bảng Kết quả Kịch bản `s_image` với 80 Ảnh Thật (`Median [Min–Max]`):

| Chính sách | Rendered Frames (30s) | Missed Frame (%) | Frame Total $p95$ (ms) | Raster $p95$ (ms) | Critical Latency $p95$ (ms) | Background Max Wait (ms) | Makespan (ms) | Tasks Done / 2,130 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **NONE (UI only)** | 550 [542–557] | 69.47% [69.06–69.89] | 142.75 [140.22–145.27] | 73.02 [71.04–75.00] | – | – | – | – |
| **P0 (Main Isolate)** | 120 [116–123] | 93.37% [93.17–93.56] | 747.41 [747.08–747.75] | 42.13 [40.26–44.00] | 35,716.5 [34,243–37,190] | 44,699.0 [44,367–45,031] | 62,178 [62,029–62,327] | 620 (29.1%) |
| **P1 (FIFO Pool)** | 385 [385–385] | 78.61% [78.61–78.61] | 248.22 [238.34–258.10] | 123.48 [122.41–124.55] | 26,588.5 [25,659–27,518] | 42,817.0 [42,211–43,423] | 61,518 [61,516–61,521] | 744 (34.9%) |
| **P2 (Priority Pool)** | 358 [329–386] | 80.14% [78.56–81.72] | 254.91 [235.59–274.22] | 135.35 [127.14–143.56] | 29,384.0 [26,176–32,592] | 43,966.0 [43,449–44,483] | 61,661 [61,652–61,670] | 875 (41.1%) |
| **P3 (Chunk + Yield)** | 364 [289–440] | 79.75% [75.56–83.94] | 290.61 [200.23–380.99] | 154.90 [104.70–205.09] | 506.0 [332–680] | 46,299.0 [45,597–47,001] | 61,501 [61,414–61,588] | 679 (31.9%) |
| **P4 (AIMD + Shed)** | **510 [499–522]** | **71.64% [71.00–72.28]** | **154.54 [147.58–161.50]** | **80.41 [75.33–85.49]** | **286.0 [270–302]** | **34,122.0 [33,153–35,091]** | **61,634 [61,549–61,720]** | 648 (30.4%) |

*(Ảnh chụp màn hình thực tế lưu tại `figures/app_screen_80.png`, biểu đồ đối đầu lưu tại `figures/fig6_s_image_real_workload.png`.)*

### Phân tích Kết quả trên Tác vụ 80 Ảnh Thực tế:
1. **Áp lực render ảnh thật kết hợp I/O trên `P0`:** Khi cả giao diện và tác vụ nền đều dùng ảnh thật, Main Isolate bị chiếm đoạt nghiêm trọng: số frame dựng được sụt từ **550** (`NONE`) xuống chỉ còn **120** frames trong 30 giây (`missedPct = 93.37%`), thời gian frame kéo dài tới **747.41 ms**, và tác vụ chạm của người dùng bị nghẽn tới **35.7 giây**.
2. **Nghẽn Rasterizer của Pool cố định (`P1`, `P2`) trên phần cứng 4 vCPU:** Do OpenGL ES dùng chung CPU host để raster hóa các thumbnail ảnh thật, `P1` và `P2` duy trì 4 worker I/O liên tục khiến `rasterP95` vọt lên **123.48 ms** (`P1`) và **135.35 ms** (`P2`). Vì các chunk ảnh lớn chưa được chia nhỏ, `P2` vẫn không giải quyết được hiện tượng nghẽn đầu hàng (độ trễ critical vẫn là **29.4 giây**).
3. **Hiệu quả vượt trội của $P_3$ và $P_4$:**
   - **`P3` (Chunking + Yielding):** Cắt nhỏ lát I/O ảnh theo chunk 80ms và dành riêng 1 worker cho critical giúp độ trễ critical tụt sốc từ **26.6 giây xuống 506.0 ms** (nhanh hơn **52 lần**).
   - **`P4` (AIMD + Backpressure):** Đạt phong độ toàn diện nhất. Bằng cách hạ worker nền khi phát hiện raster bị quá tải, `P4` bảo vệ UI dựng được **510 frames** (gần tương đương baseline không tải `NONE` 550 frames), giữ `rasterP95` ở mức thấp lý tưởng **80.41 ms** (so với 123.5 ms của P1), và đưa độ trễ critical về mức kỷ lục **286.0 ms** (**nhanh hơn `P1` 93 lần** và **nhanh hơn `P0` 125 lần**).
4. **Hạn chế cỡ mẫu:** Với `n=2` lượt đo trên emulator, mặc dù $p_{\min}$ của Mann-Whitney U là `0.2207 – 0.3333`, các khoảng giá trị `[Min–Max]` giữa `P4` và `P1` hoàn toàn tách biệt rõ rệt trên các chỉ số cốt lõi (`frames`: 499–522 vs 385–385; `p95Ms`: 147–161 vs 238–258 ms; `critP95Ms`: 270–302 ms vs 25.6–27.5 s).
