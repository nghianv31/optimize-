#!/usr/bin/env python3
"""Công cụ Demo Trực Tiếp (Live Demo Launcher) cho buổi thuyết trình môn Tối Ưu.

Cho phép chuyển đổi tức thời giữa các chính sách P0, P1, P3, P4 bằng phím tắt
ngay trong khi đang nói, không cần gõ lệnh dài.
"""
import json
import os
import subprocess
import sys
import time

PKG = "com.example.optimize"
REMOTE_DIR = f"/sdcard/Android/data/{PKG}/files"


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


def get_device():
    lines = sh("adb devices").splitlines()
    devs = []
    for l in lines[1:]:
        if "\tdevice" in l:
            devs.append(l.split("\t")[0])
    if not devs:
        print("[!] Không tìm thấy thiết bị ADB nào! Hãy bật máy ảo hoặc cắm điện thoại.")
        return None
    # Ưu tiên emulator nếu có, hoặc thiết bị đầu tiên
    for d in devs:
        if "emulator" in d:
            return d
    return devs[0]


def launch_scenario(serial, policy, scenario, load, duration=35, chunk_ms=80, workers=4):
    cfg = {
        "policy": policy,
        "scenario": scenario,
        "device": "demo",
        "run": 1,
        "seed": 42,
        "workers": workers,
        "chunkMs": chunk_ms,
        "load": float(load),
        "durationS": int(duration),
        "settleS": 1,
        "warmupS": 1,
        "graceS": 5,
        "autorun": True,
        "tag": f"DEMO_{policy.upper()}"
    }

    cfg_str = json.dumps(cfg, indent=2)
    tmp_path = os.path.join(os.path.dirname(__file__), "_demo_cfg.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(cfg_str)

    print(f"\n[*] Đang nạp cấu hình: Policy={policy.upper()}, Scenario={scenario}, Load={load}, Workers={workers}...")
    sh(f'adb -s {serial} shell "mkdir -p {REMOTE_DIR}"')
    sh(f'adb -s {serial} push "{tmp_path}" "{REMOTE_DIR}/config.json"')
    try:
        os.remove(tmp_path)
    except Exception:
        pass

    sh(f'adb -s {serial} shell "am force-stop {PKG}; input keyevent KEYCODE_WAKEUP; am start -n {PKG}/.MainActivity"')
    print(f"[✓] Đã khởi chạy {policy.upper()} thành công trên [{serial}]! Màn hình đang cập nhật...")


def print_menu(serial):
    print("\n" + "=" * 65)
    print("   BỘ ĐIỀU KHIỂN LIVE DEMO - BỘ LẬP LỊCH THÍCH ỨNG FLUTTER")
    print(f"   Thiết bị kết nối: {serial}")
    print("=" * 65)
    print("  [1] DEMO 1 (Vấn đề): P0 - Chạy Main Isolate (Đóng băng & Drop ~80%)")
    print("  [2] DEMO 2 (Pool mù): P1 - Fixed Pool 4 Workers (Tranh chấp CPU, Jank ~25%)")
    print("  [3] DEMO 3 (Đột phá): P3 - Cooperative Chunking + Frame Yielding (Mượt 60 FPS)")
    print("  [4] DEMO 4 (Tự thích ứng): P4 - AIMD + Mode Throttling + Drop (Tải nặng L=16)")
    print("  [5] DEMO 5 (Ảnh thật): P4 với 80 ảnh DSLR thật (s_image)")
    print("  [s] Dừng ứng dụng (Force Stop)")
    print("  [q] Thoát trình điều khiển")
    print("=" * 65)


def main():
    dev = get_device()
    if not dev:
        sys.exit(1)

    while True:
        print_menu(dev)
        choice = input(">> Nhấn phím chọn kịch bản (1/2/3/4/5/s/q) và Enter: ").strip().lower()

        if choice == "1":
            print("\n>>> ĐANG CHẠY DEMO 1: P0 (Main Isolate - Thảm họa giật lag)...")
            print(">>> Điểm nhấn thuyết trình: Nhìn vòng xoay Spinner bị khựng, cột đỏ vượt ngân sách 16.7ms!")
            launch_scenario(dev, policy="p0", scenario="s1", load=1.0, duration=30, workers=1)
        elif choice == "2":
            print("\n>>> ĐANG CHẠY DEMO 2: P1 (Fixed Worker Pool - Tranh chấp CPU)...")
            print(">>> Điểm nhấn thuyết trình: Hết đơ cứng nhưng vẫn giật do CFS chia đều CPU với luồng Raster!")
            launch_scenario(dev, policy="p1", scenario="s1", load=4.0, duration=30, workers=4)
        elif choice == "3":
            print("\n>>> ĐANG CHẠY DEMO 3: P3 (Cooperative Chunking + Frame Yielding)...")
            print(">>> Điểm nhấn thuyết trình: Huy hiệu YIELDING màu vàng bật sáng, cột biểu đồ hạ dưới 16.7ms!")
            launch_scenario(dev, policy="p3", scenario="s1", load=2.0, duration=30, workers=4)
        elif choice == "4":
            print("\n>>> ĐANG CHẠY DEMO 4: P4 (AIMD Adaptive Control dưới tải cực đại L=16)...")
            print(">>> Điểm nhấn thuyết trình: AIMD tự siết worker từ 4 về 1, drop tác vụ nền để cứu Crit latency!")
            launch_scenario(dev, policy="p4", scenario="s2", load=16.0, duration=35, workers=4)
        elif choice == "5":
            print("\n>>> ĐANG CHẠY DEMO 5: P4 với 80 ảnh DSLR JPEG 24MP...")
            print(">>> Điểm nhấn thuyết trình: Lưới cuộn ảnh thật kết hợp giải mã nền mượt mà!")
            launch_scenario(dev, policy="p4", scenario="s_image", load=4.0, duration=35, workers=4)
        elif choice == "s":
            sh(f'adb -s {dev} shell "am force-stop {PKG}"')
            print(f"[✓] Đã dừng ứng dụng trên {dev}.")
        elif choice == "q":
            print("Tạm biệt!")
            break
        else:
            print("[!] Lựa chọn không hợp lệ, vui lòng chọn lại.")


if __name__ == "__main__":
    main()
