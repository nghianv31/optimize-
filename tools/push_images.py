#!/usr/bin/env python3
"""Đẩy 30 ảnh DSLR thực tế từ assets/ lên thiết bị Android với tên chuẩn img_00.jpg..img_29.jpg."""
import argparse
import os
import subprocess
import sys

PKG = "com.example.optimize"
REMOTE_IMAGES = f"/sdcard/Android/data/{PKG}/files/images"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_asset_images(limit=30):
    assets_dir = os.path.join(ROOT, "assets")
    if not os.path.isdir(assets_dir):
        raise FileNotFoundError(f"Không tìm thấy thư mục assets tại {assets_dir}")

    files = []
    for dirpath, _, filenames in os.walk(assets_dir):
        for fn in filenames:
            if fn.lower().endswith((".jpg", ".jpeg")):
                files.append(os.path.join(dirpath, fn))

    files.sort()
    if len(files) < limit:
        print(f"[Cảnh báo] Chỉ tìm thấy {len(files)} ảnh (yêu cầu {limit}).")
        return files
    return files[:limit]


def sync_images(serial=None, count=80):
    base = ["adb"] + (["-s", serial] if serial else [])
    images = find_asset_images(count)
    if not images:
        raise RuntimeError("Không có ảnh nào trong assets/ để đẩy lên thiết bị.")

    subprocess.run(base + ["shell", "mkdir", "-p", REMOTE_IMAGES], check=True)
    res = subprocess.run(base + ["shell", "ls", "-1", REMOTE_IMAGES], capture_output=True, text=True)
    existing = set(line.strip() for line in res.stdout.splitlines() if line.strip())

    pushed = 0
    for idx, src in enumerate(images):
        dst_name = f"img_{idx:02d}.jpg"
        if dst_name in existing:
            continue
        dst_path = f"{REMOTE_IMAGES}/{dst_name}"
        print(f"Đẩy [{idx + 1}/{len(images)}] {os.path.basename(src)} -> {dst_name} ...", flush=True)
        subprocess.run(base + ["push", src, dst_path], check=True, stdout=subprocess.DEVNULL)
        pushed += 1

    print(f"[OK] Đã đồng bộ {len(images)} ảnh thật lên {REMOTE_IMAGES} (mới đẩy: {pushed}).")

    # Đồng bộ cả vào sandbox nội bộ của ứng dụng để đảm bảo quyền đọc trên Android 11+ (Scoped Storage)
    try:
        subprocess.run(
            base + ["shell", f"run-as {PKG} mkdir -p /data/user/0/{PKG}/files/images && cp -r {REMOTE_IMAGES}/* /data/user/0/{PKG}/files/images/"],
            capture_output=True,
            text=True,
        )
    except Exception:
        pass

    return len(images)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serial", default=None)
    ap.add_argument("--count", type=int, default=80)
    a = ap.parse_args()
    sync_images(serial=a.serial, count=a.count)


if __name__ == "__main__":
    main()
