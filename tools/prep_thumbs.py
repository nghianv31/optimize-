#!/usr/bin/env python3
"""Tạo 80 ảnh thumbnail nhẹ (width=240px) từ 80 ảnh DSLR 24MP trong assets/ để PhotoGrid cuộn mượt 60 FPS."""
import argparse
import os
import subprocess
import sys

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from push_images import find_asset_images

PKG = "com.example.optimize"
LOCAL_THUMBS = os.path.join(ROOT, "build", "thumbs")
REMOTE_EXT_THUMBS = f"/sdcard/Android/data/{PKG}/files/thumbs"


def generate_thumbs(count=80, width=240):
    os.makedirs(LOCAL_THUMBS, exist_ok=True)
    images = find_asset_images(count)
    if not images:
        raise RuntimeError("Không tìm thấy ảnh nào trong assets/")

    total_bytes = 0
    for idx, src in enumerate(images):
        dst = os.path.join(LOCAL_THUMBS, f"img_{idx:02d}.jpg")
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im)
            if im.mode != "RGB":
                im = im.convert("RGB")
            ratio = width / float(im.width)
            height = max(1, int(round(im.height * ratio)))
            resized = im.resize((width, height), Image.Resampling.LANCZOS)
            resized.save(dst, "JPEG", quality=85, optimize=True)
        total_bytes += os.path.getsize(dst)

    print(
        f"[OK] Đã tạo {len(images)} thumbnail tại {LOCAL_THUMBS} "
        f"(tổng dung lượng: {total_bytes / 1024:.1f} KB, TB {total_bytes / len(images) / 1024:.1f} KB/ảnh)."
    )
    return len(images)


def push_thumbs(serial=None):
    base = ["adb"] + (["-s", serial] if serial else [])
    if not os.path.isdir(LOCAL_THUMBS):
        raise FileNotFoundError(f"Chưa có thư mục {LOCAL_THUMBS}")

    # Đẩy vào /data/local/tmp/thumbs để run-as đọc và chép vào internal storage dễ dàng trên Android 11+
    tmp_remote = "/data/local/tmp/opt_thumbs"
    subprocess.run(base + ["shell", f"rm -rf {tmp_remote} && mkdir -p {tmp_remote}"], check=True)
    files = sorted(f for f in os.listdir(LOCAL_THUMBS) if f.endswith(".jpg"))
    for f in files:
        subprocess.run(
            base + ["push", os.path.join(LOCAL_THUMBS, f), f"{tmp_remote}/{f}"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    subprocess.run(base + ["shell", f"chmod -R 755 {tmp_remote}"], check=True)
    subprocess.run(
        base + ["shell", f"run-as {PKG} sh -c 'rm -rf /data/user/0/{PKG}/files/thumbs && mkdir -p /data/user/0/{PKG}/files/thumbs && cp {tmp_remote}/*.jpg /data/user/0/{PKG}/files/thumbs/'"],
        check=True,
    )
    subprocess.run(base + ["shell", f"rm -rf {tmp_remote}"], check=True)

    # Cũng đẩy bản dự phòng ra bộ nhớ ngoài của app
    subprocess.run(base + ["shell", f"mkdir -p {REMOTE_EXT_THUMBS}"], check=False)
    for f in files:
        subprocess.run(
            base + ["push", os.path.join(LOCAL_THUMBS, f), f"{REMOTE_EXT_THUMBS}/{f}"],
            check=False,
            stdout=subprocess.DEVNULL,
        )

    res = subprocess.run(
        base + ["shell", f"run-as {PKG} sh -c 'ls -1 /data/user/0/{PKG}/files/thumbs | wc -l'"],
        capture_output=True,
        text=True,
        check=True,
    )
    print(f"[OK] Đã đồng bộ {res.stdout.strip()} thumbnail vào /data/user/0/{PKG}/files/thumbs trên {serial or 'default device'}.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serial", default=None)
    ap.add_argument("--count", type=int, default=80)
    ap.add_argument("--width", type=int, default=240)
    ap.add_argument("--generate-only", action="store_true")
    ap.add_argument("--push-only", action="store_true")
    a = ap.parse_args()

    if not a.push_only:
        generate_thumbs(count=a.count, width=a.width)
    if not a.generate_only:
        push_thumbs(serial=a.serial)


if __name__ == "__main__":
    main()
