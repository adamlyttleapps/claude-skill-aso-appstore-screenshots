#!/usr/bin/env python3
"""
Generate device frame template PNGs.
Output: assets/device_frame.png (iPhone) or assets/device_frame_android.png
compose.py positions these dynamically based on text height.

Usage:
  python3 generate_frame.py                 # generates iPhone frame (default)
  python3 generate_frame.py --device iphone # same as above
  python3 generate_frame.py --device android
  python3 generate_frame.py --device all    # generates both
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageChops

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# ── iPhone dimensions ──────────────────────────────────────────────
IPHONE_W = 1030
IPHONE_H = 2800
IPHONE_CORNER_R = 77
IPHONE_BEZEL = 15
IPHONE_SCREEN_CORNER_R = 62
IPHONE_DI_W = 130               # Dynamic Island width
IPHONE_DI_H = 38                # Dynamic Island height
IPHONE_DI_TOP = 14              # offset from top of screen

# ── Android dimensions ─────────────────────────────────────────────
# Sized for 1080×1920 Google Play canvas (~80% width)
ANDROID_W = 864
ANDROID_H = 2750
ANDROID_CORNER_R = 50
ANDROID_BEZEL = 8
ANDROID_SCREEN_CORNER_R = 44
ANDROID_PUNCH_HOLE_R = 14       # punch-hole camera radius
ANDROID_PUNCH_HOLE_TOP = 16     # offset from top of screen


def generate_iphone():
    device_w, device_h = IPHONE_W, IPHONE_H
    bezel = IPHONE_BEZEL
    screen_w = device_w - 2 * bezel
    screen_h = device_h - 2 * bezel

    frame = Image.new("RGBA", (device_w, device_h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # ── Device body (dark grey outer, darker inner) ─────────────────
    fd.rounded_rectangle(
        [0, 0, device_w - 1, device_h - 1],
        radius=IPHONE_CORNER_R,
        fill=(30, 30, 30, 255),
    )
    fd.rounded_rectangle(
        [1, 1, device_w - 2, device_h - 2],
        radius=IPHONE_CORNER_R - 1,
        fill=(20, 20, 20, 255),
    )

    # ── Screen cutout (transparent) ─────────────────────────────────
    screen_x, screen_y = bezel, bezel
    cutout = Image.new("L", (device_w, device_h), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=IPHONE_SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # ── Dynamic Island ──────────────────────────────────────────────
    di_x = (device_w - IPHONE_DI_W) // 2
    di_y = screen_y + IPHONE_DI_TOP
    ImageDraw.Draw(frame).rounded_rectangle(
        [di_x, di_y, di_x + IPHONE_DI_W, di_y + IPHONE_DI_H],
        radius=IPHONE_DI_H // 2,
        fill=(0, 0, 0, 255),
    )

    # ── Side buttons ────────────────────────────────────────────────
    btn_color = (25, 25, 25, 255)
    fd2 = ImageDraw.Draw(frame)
    fd2.rounded_rectangle([device_w, 340, device_w + 4, 460], radius=2, fill=btn_color)
    fd2.rounded_rectangle([-4, 280, 0, 360], radius=2, fill=btn_color)
    fd2.rounded_rectangle([-4, 380, 0, 460], radius=2, fill=btn_color)
    fd2.rounded_rectangle([-4, 180, 0, 220], radius=2, fill=btn_color)

    out = os.path.join(ASSETS_DIR, "device_frame.png")
    frame.save(out, "PNG")
    print(f"✓ {out} ({device_w}×{device_h})")
    print(f"  BEZEL={bezel}, SCREEN_W={screen_w}, SCREEN_H={screen_h}")
    print(f"  SCREEN_CORNER_R={IPHONE_SCREEN_CORNER_R}")


def generate_android():
    device_w, device_h = ANDROID_W, ANDROID_H
    bezel = ANDROID_BEZEL
    screen_w = device_w - 2 * bezel
    screen_h = device_h - 2 * bezel

    frame = Image.new("RGBA", (device_w, device_h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # ── Device body (dark grey outer, darker inner) ─────────────────
    fd.rounded_rectangle(
        [0, 0, device_w - 1, device_h - 1],
        radius=ANDROID_CORNER_R,
        fill=(30, 30, 30, 255),
    )
    fd.rounded_rectangle(
        [1, 1, device_w - 2, device_h - 2],
        radius=ANDROID_CORNER_R - 1,
        fill=(20, 20, 20, 255),
    )

    # ── Screen cutout (transparent) ─────────────────────────────────
    screen_x, screen_y = bezel, bezel
    cutout = Image.new("L", (device_w, device_h), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=ANDROID_SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # ── Punch-hole camera (centered, top of screen) ─────────────────
    ph_x = device_w // 2
    ph_y = screen_y + ANDROID_PUNCH_HOLE_TOP + ANDROID_PUNCH_HOLE_R
    ImageDraw.Draw(frame).ellipse(
        [ph_x - ANDROID_PUNCH_HOLE_R, ph_y - ANDROID_PUNCH_HOLE_R,
         ph_x + ANDROID_PUNCH_HOLE_R, ph_y + ANDROID_PUNCH_HOLE_R],
        fill=(0, 0, 0, 255),
    )

    # ── Side buttons ────────────────────────────────────────────────
    btn_color = (25, 25, 25, 255)
    fd2 = ImageDraw.Draw(frame)
    # Power button (right side)
    fd2.rounded_rectangle([device_w, 260, device_w + 3, 340], radius=2, fill=btn_color)
    # Volume up (right side, above power)
    fd2.rounded_rectangle([device_w, 160, device_w + 3, 220], radius=2, fill=btn_color)

    out = os.path.join(ASSETS_DIR, "device_frame_android.png")
    frame.save(out, "PNG")
    print(f"✓ {out} ({device_w}×{device_h})")
    print(f"  BEZEL={bezel}, SCREEN_W={screen_w}, SCREEN_H={screen_h}")
    print(f"  SCREEN_CORNER_R={ANDROID_SCREEN_CORNER_R}")


def main():
    p = argparse.ArgumentParser(description="Generate device frame template")
    p.add_argument(
        "--device",
        choices=["iphone", "android", "all"],
        default="iphone",
        help="Which device frame to generate (default: iphone)",
    )
    args = p.parse_args()

    os.makedirs(ASSETS_DIR, exist_ok=True)

    if args.device in ("iphone", "all"):
        generate_iphone()
    if args.device in ("android", "all"):
        generate_android()


if __name__ == "__main__":
    main()
