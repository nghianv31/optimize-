"""Update markdown reports with latest 80-image experiment numbers."""

SEC_3_9 = """### Bảng Kết quả Kịch bản `s_image` với 80 Ảnh Thật (`Median [Min–Max]`):

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
4. **Hạn chế cỡ mẫu:** Với `n=2` lượt đo trên emulator, mặc dù $p_{\\min}$ của Mann-Whitney U là `0.2207 – 0.3333`, các khoảng giá trị `[Min–Max]` giữa `P4` và `P1` hoàn toàn tách biệt rõ rệt trên các chỉ số cốt lõi (`frames`: 499–522 vs 385–385; `p95Ms`: 147–161 vs 238–258 ms; `critP95Ms`: 270–302 ms vs 25.6–27.5 s).
"""

SEC_6_ARTIFACT = """## 6. Mở rộng Thực nghiệm Tác vụ Ảnh Thực tế từ Assets (`s_image` — Phương án A)

Để kiểm chứng khung lập lịch với **File I/O thật + phân tích ảnh JPEG kết hợp Render UI thật**, nghiên cứu triển khai kịch bản `s_image` sử dụng **80 ảnh DSLR JPEG** (`6016×4016`, `5.85–12.48 MB`/ảnh) trích từ 179 ảnh trong `assets/`, đồng bộ vào bộ nhớ nội bộ ứng dụng trên `emulator-5554` (4 vCPU, 60 Hz, Profile mode). Giao diện lưới cuộn 3 cột nạp trực tiếp 80 ảnh thật với thumbnail `cacheWidth: 240`. Mỗi chunk mở file ảnh thật qua `RandomAccessFile`, đọc header JPEG (`SOI`/`SOF0`/`SOF2`), đọc lát `256 KB`, tính histogram 256 bin và năng lượng điểm ảnh.

### Bảng 3: Kết quả `s_image` với 80 Ảnh Thật trên `emulator-5554` ($L=16, W=4, C=80\\text{ ms}, 30\\text{s}$, $n=2$, `Median [Min–Max]`)

| Chính sách | Frames (30s) | Missed (%) | Frame p95 (ms) | Raster p95 (ms) | Critical p95 (ms) | BG Max Wait (ms) | Makespan (ms) | Tasks Done / 2,130 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **NONE (UI only)** | 550 [542–557] | 69.47 [69.06–69.89] | 142.75 [140.22–145.27] | 73.02 [71.04–75.00] | – | – | – | – |
| **P0 (Main Isolate)** | 120 [116–123] | 93.37 [93.17–93.56] | 747.41 [747.08–747.75] | 42.13 [40.26–44.00] | 35,716.5 [34,243–37,190] | 44,699.0 [44,367–45,031] | 62,178 [62,029–62,327] | 620 (29.1%) |
| **P1 (FIFO Pool)** | 385 [385–385] | 78.61 [78.61–78.61] | 248.22 [238.34–258.10] | 123.48 [122.41–124.55] | 26,588.5 [25,659–27,518] | 42,817.0 [42,211–43,423] | 61,518 [61,516–61,521] | 744 (34.9%) |
| **P2 (Priority)** | 358 [329–386] | 80.14 [78.56–81.72] | 254.91 [235.59–274.22] | 135.35 [127.14–143.56] | 29,384.0 [26,176–32,592] | 43,966.0 [43,449–44,483] | 61,661 [61,652–61,670] | 875 (41.1%) |
| **P3 (Chunk+Yield)** | 364 [289–440] | 79.75 [75.56–83.94] | 290.61 [200.23–380.99] | 154.90 [104.70–205.09] | 506.0 [332–680] | 46,299.0 [45,597–47,001] | 61,501 [61,414–61,588] | 679 (31.9%) |
| **P4 (AIMD+Shed)** | **510 [499–522]** | **71.64 [71.00–72.28]** | **154.54 [147.58–161.50]** | **80.41 [75.33–85.49]** | **286.0 [270–302]** | **34,122.0 [33,153–35,091]** | **61,634 [61,549–61,720]** | 648 (30.4%) |

![Lưới 80 ảnh thực tế trên máy ảo](C:\\Users\\ADMIN\\.gemini\\antigravity\\brain\\15376df7-1083-477a-a020-db1a4a72b33d\\app_screen_80.png)

![Tác vụ 80 ảnh thực tế s_image](C:\\Users\\ADMIN\\.gemini\\antigravity\\brain\\15376df7-1083-477a-a020-db1a4a72b33d\\fig6_s_image_real_workload.png)

> [!NOTE]
> **Nhận định `s_image` với 80 Ảnh Thật:**
> - Trên OpenGL ES giả lập 4 vCPU, tải nạp 80 ảnh thật khiến `NONE` đạt `550` frames và `rasterP95 = 73.02 ms`.
> - **`P0`** khóa Main Isolate khiến số frame dựng được tụt dốc thê thảm (**120** frames trong 30 giây, `missedPct = 93.37%`), thời gian frame $p95$ kéo dài tới **747.41 ms**, và tác vụ critical bị trễ tới **35.7 giây**.
> - **`P4` (AIMD + ModeMachine + Backpressure)** bảo vệ UI đạt **510 frames** (gần tương đương baseline không tải `NONE` 550 frames), giữ `rasterP95` ở mức thấp lý tưởng **80.41 ms** (so với 123.5 ms của P1), và đưa độ trễ critical về mức kỷ lục **286.0 ms** (**nhanh hơn `P1` 93 lần** và **nhanh hơn `P0` 125 lần**).
"""


def main():
    with open('REPORT_CHAPTER_3.md', 'r', encoding='utf-8') as f:
        text = f.read()
    idx = text.find('### Bảng Kết quả Kịch bản `s_image`')
    if idx != -1:
        with open('REPORT_CHAPTER_3.md', 'w', encoding='utf-8') as f:
            f.write(text[:idx] + SEC_3_9)
        print('Updated REPORT_CHAPTER_3.md')

    with open(r'C:\Users\ADMIN\.gemini\antigravity\brain\15376df7-1083-477a-a020-db1a4a72b33d\EXPERIMENT_ANALYSIS_REPORT.md', 'r', encoding='utf-8') as f:
        text_art = f.read()
    idx_art = text_art.find('## 6. Mở rộng Thực nghiệm Tác vụ Ảnh Thực tế')
    if idx_art != -1:
        with open(r'C:\Users\ADMIN\.gemini\antigravity\brain\15376df7-1083-477a-a020-db1a4a72b33d\EXPERIMENT_ANALYSIS_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(text_art[:idx_art] + SEC_6_ARTIFACT)
        print('Updated EXPERIMENT_ANALYSIS_REPORT.md')


if __name__ == '__main__':
    main()
