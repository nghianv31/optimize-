"""Chạy liên hoàn tất cả các kịch bản thực nghiệm (s1, s2) trên emulator-5554."""
import subprocess
import sys
import time


def run(cmd):
    print(f"\n>>> CHẠY LỆNH: {' '.join(cmd)}\n", flush=True)
    subprocess.run([sys.executable] + cmd, check=True)


def main():
    start_time = time.time()
    serial = "emulator-5554"
    device = "emu"
    load = "16"
    workers = "4"
    chunks = "80"
    duration = "30"
    cool = "5"
    reps = "2"

    print("=" * 60)
    print("BẮT ĐẦU CHẠY TOÀN BỘ CÁC KỊCH BẢN THỰC NGHIỆM TRÊN EMULATOR-5554")
    print("Lưới UI: 80 ảnh DSLR JPEG thật đang hoạt động")
    print(f"Cấu hình: L={load}, W={workers}, C={chunks}ms, dur={duration}s, reps={reps}")
    print("=" * 60)

    # 1. Kịch bản S1 (Tải tĩnh bão hòa: none, p0, p1, p2, p3)
    print("\n--- GIAI ĐOẠN 1: KỊCH BẢN S1 (Tải tĩnh bão hòa: none, p0, p1, p2, p3) ---")
    run([
        "tools/run_matrix.py",
        "--serial", serial,
        "--device", device,
        "--scenario", "s1",
        "--policies", "none,p0,p1,p2,p3",
        "--loads", load,
        "--workers", workers,
        "--chunks", chunks,
        "--duration", duration,
        "--cool-s", cool,
        "--reps", reps,
    ])

    # 2. Kịch bản S2 (Tải động bậc thang: p1, p3, p4)
    print("\n--- GIAI ĐOẠN 2: KỊCH BẢN S2 (Tải động bậc thang: p1, p3, p4) ---")
    run([
        "tools/run_matrix.py",
        "--serial", serial,
        "--device", device,
        "--scenario", "s2",
        "--policies", "p1,p3,p4",
        "--loads", load,
        "--workers", workers,
        "--chunks", chunks,
        "--duration", duration,
        "--cool-s", cool,
        "--reps", reps,
    ])

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"HOÀN TẤT TOÀN BỘ CÁC KỊCH BẢN TRÊN MÁY ẢO (Tổng thời gian: {elapsed / 60:.1f} phút)")
    print("=" * 60)


if __name__ == "__main__":
    main()
