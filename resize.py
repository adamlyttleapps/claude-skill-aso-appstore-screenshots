#!/usr/bin/env python3
"""
Cross-platform screenshot resize for App Store / Play Store.
Replaces macOS-only `sips` commands with Pillow (already a dependency).

Crops to the target aspect ratio (center-crop, preserving the top edge
so headlines stay put) then resizes to exact pixel dimensions.
"""

import argparse
import os
from PIL import Image


def resize(input_path, output_path, target_w, target_h):
    img = Image.open(input_path)
    w, h = img.size

    target_ratio = target_w / target_h
    current_ratio = w / h

    if current_ratio > target_ratio:
        # Too wide — crop sides equally (center crop)
        new_w = round(h * target_ratio)
        offset_x = (w - new_w) // 2
        img = img.crop((offset_x, 0, offset_x + new_w, h))
    elif current_ratio < target_ratio:
        # Too tall — crop bottom (preserve top so headline stays)
        new_h = round(w / target_ratio)
        img = img.crop((0, 0, w, new_h))

    img = img.resize((target_w, target_h), Image.LANCZOS)

    # Ensure JPEG compatibility (RGBA cannot be saved as JPEG)
    if output_path.lower().endswith((".jpg", ".jpeg")) and img.mode == "RGBA":
        img = img.convert("RGB")

    img.save(output_path, quality=95)
    print(f"✓ {output_path} ({target_w}×{target_h})")


def main():
    p = argparse.ArgumentParser(
        description="Crop and resize screenshots to exact store dimensions"
    )
    p.add_argument("inputs", nargs="+", help="Input image paths")
    p.add_argument(
        "--width", type=int, default=1290, help="Target width (default: 1290)"
    )
    p.add_argument(
        "--height", type=int, default=2796, help="Target height (default: 2796)"
    )
    p.add_argument(
        "--suffix",
        default="-resized",
        help="Suffix for output files (default: -resized)",
    )
    args = p.parse_args()

    for input_path in args.inputs:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}{args.suffix}{ext}"
        resize(input_path, output_path, args.width, args.height)


if __name__ == "__main__":
    main()
