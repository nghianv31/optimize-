# BÁO CÁO PHÂN TÍCH THỐNG KÊ THỰC NGHIỆM (S1 & S2)

Thiết bị đo: Samsung Galaxy A04e (MediaTek Helio P35, 8 nhân, 2GB RAM, Android 14).

## 1. Kịch bản S1 (Tải tĩnh bão hòa: L64, W8, C80, 4 lượt chạy mỗi chính sách)

| Chính sách | Missed Frame (%) | Jank Frame (%) | Critical Latency p95 (ms) | Background Max Wait (ms) | Tỷ lệ hoàn thành (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NONE** | 0.9 (IQR 0.1) [1-1] | 2.2 (IQR 1.8) [0-3] | 0.0 (IQR 0.0) [0-0] | 0.0 (IQR 0.0) [0-0] | 0.0 (IQR 0.0) [0-0] |
| **P0** | 90.8 (IQR 0.1) [91-91] | 0.0 (IQR 0.1) [0-1] | 68483.5 (IQR 49.8) [68450-68508] | 81719.5 (IQR 56.5) [81674-81759] | 16.6 (IQR 0.0) [17-17] |
| **P1** | 23.2 (IQR 0.8) [22-24] | 9.9 (IQR 1.1) [9-11] | 35356.5 (IQR 2225.8) [33803-37111] | 39621.5 (IQR 1306.0) [38847-40588] | 86.5 (IQR 2.2) [85-88] |
| **P2** | 22.4 (IQR 2.1) [21-24] | 10.0 (IQR 0.3) [9-10] | 22760.5 (IQR 728.0) [21586-24201] | 39027.0 (IQR 696.5) [38354-39946] | 90.4 (IQR 1.4) [89-92] |
| **P3** | 0.8 (IQR 0.2) [1-1] | 17.0 (IQR 1.6) [16-19] | 31.0 (IQR 4.8) [28-35] | 46886.0 (IQR 2104.2) [45728-48301] | 77.1 (IQR 3.5) [75-79] |

## 2. Kịch bản S2 (Tải tăng dần bậc thang: L32, W8, C80, 4 phase, 3 lượt chạy mỗi chính sách)

| Chính sách | Missed Frame (%) | Jank Frame (%) | Critical Latency p95 (ms) | Makespan (ms) | Background Dropped |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P1 (FIFO)** | 5.1 (IQR 0.2) [5-5] | 4.8 (IQR 2.1) [4-8] | 4744.0 (IQR 52.0) [4716-4820] | 67839.0 (IQR 101.0) [67704-67906] | 0 |
| **P3 (Chunk + Priority)** | 0.7 (IQR 0.1) [1-1] | 24.8 (IQR 4.1) [18-26] | 34.0 (IQR 7.5) [29-44] | 77736.0 (IQR 162.5) [77632-77957] | 0 |
| **P4 (AIMD + Backpressure)** | 0.8 (IQR 0.0) [1-1] | 8.0 (IQR 4.7) [0-10] | 28.0 (IQR 1.5) [27-30] | 67865.0 (IQR 566.0) [67767-68899] | 1990 |

## 3. Kiểm định Giả thuyết Khoa học (Mann-Whitney U Test)

| Giả thuyết & Phép so sánh | Giá trị Median A | Giá trị Median B | Thống kê U | Mức ý nghĩa p | Kết luận |
| :--- | :--- | :--- | :--- | :--- | :--- |
| H1 (P0 vs P1 trên S1 - Frame Missed) | 90.8 | 23.2 | 16.0 | p < 0.05 (*) | Chấp nhận giả thuyết (**Có ý nghĩa thống kê**) |
| H3 (P1 vs P2 trên S1 - Critical Latency) | 35356.5 | 22760.5 | 16.0 | p < 0.05 (*) | Chấp nhận giả thuyết (**Có ý nghĩa thống kê**) |
| H3 (P1 vs P3 trên S1 - Critical Latency) | 35356.5 | 31.0 | 16.0 | p < 0.05 (*) | Chấp nhận giả thuyết (**Có ý nghĩa thống kê**) |
| H3 (P1 vs P3 trên S1 - Frame Missed) | 23.2 | 0.8 | 16.0 | p < 0.05 (*) | Chấp nhận giả thuyết (**Có ý nghĩa thống kê**) |
| H4 (P1 vs P4 trên S2 - Critical Latency) | 4744.0 | 28.0 | 9.0 | p = 0.050 | Chấp nhận giả thuyết (**Có ý nghĩa thống kê**) |
| H4 (P3 vs P4 trên S2 - Jank %) | 24.8 | 8.0 | 9.0 | p = 0.050 | Chấp nhận giả thuyết (**Có ý nghĩa thống kê**) |
| H4 (P3 vs P4 trên S2 - Makespan) | 77736.0 | 67865.0 | 9.0 | p = 0.050 | Chấp nhận giả thuyết (**Có ý nghĩa thống kê**) |
