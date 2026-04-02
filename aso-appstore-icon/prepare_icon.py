#!/usr/bin/env python3
"""
Normalize a generated app icon into an App Store-safe 1024x1024 PNG.

- Center-crops non-square images
- Resizes to the target dimensions
- Flattens stray transparency onto an inferred matte
"""

import argparse
from pathlib import Path

from PIL import Image


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    if len(value) != 6:
        raise ValueError("Expected a 6-digit hex colour")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def infer_matte(image: Image.Image) -> tuple[int, int, int]:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    corners = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
    ]
    for x, y in corners:
        r, g, b, a = rgba.getpixel((x, y))
        if a > 0:
            return (r, g, b)
    return (255, 255, 255)


def flatten_alpha(image: Image.Image, matte: tuple[int, int, int]) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    alpha_min, alpha_max = alpha.getextrema()
    if alpha_min == 255 and alpha_max == 255:
        return rgba.convert("RGB")
    background = Image.new("RGBA", rgba.size, (*matte, 255))
    return Image.alpha_composite(background, rgba).convert("RGB")


def crop_to_square(image: Image.Image) -> Image.Image:
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return image.crop((left, top, left + side, top + side))


def prepare_icon(input_path: Path, output_path: Path, size: int, matte_arg: str) -> None:
    image = Image.open(input_path)
    matte = infer_matte(image) if matte_arg == "auto" else hex_to_rgb(matte_arg)
    prepared = flatten_alpha(image, matte)
    prepared = crop_to_square(prepared)
    prepared = prepared.resize((size, size), Image.LANCZOS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prepared.save(output_path, "PNG")
    print(f"✓ {output_path} ({size}x{size})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare an App Store icon PNG")
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--output", required=True, help="Prepared output path")
    parser.add_argument("--size", type=int, default=1024, help="Output size")
    parser.add_argument(
        "--matte",
        default="auto",
        help="Background matte for flattening transparency: auto or #RRGGBB",
    )
    args = parser.parse_args()

    prepare_icon(Path(args.input), Path(args.output), args.size, args.matte)


if __name__ == "__main__":
    main()
