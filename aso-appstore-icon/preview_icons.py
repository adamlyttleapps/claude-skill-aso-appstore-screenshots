#!/usr/bin/env python3
"""
Create a comparison board for one or more App Store icon candidates.
"""

import argparse
from pathlib import Path
from typing import Optional, Union

from PIL import Image, ImageDraw, ImageFont

PADDING = 64
TITLE_H = 84
COLUMN_W = 320
COLUMN_GAP = 36
CARD_RADIUS = 28
LABEL_GAP = 18
HERO_CARD_H = 320
CONTEXT_CARD_H = 164
BOTTOM_STRIP_H = 118
CARD_GAP = 20
CANVAS_BG = "#F4F1EB"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#DDD6CA"
TEXT = "#18181B"
MUTED = "#6B7280"
LIGHT_TILE = "#ECE7DE"
DARK_TILE = "#1F2937"
HOME_TILE = "#E7EEF8"
ROUND_RATIO = 0.223


def load_font(size: int, bold: bool = False) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
    candidates = [
        "/Library/Fonts/SF-Pro-Display-Semibold.otf" if bold else "/Library/Fonts/SF-Pro-Display-Regular.otf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def crop_square(image: Image.Image) -> Image.Image:
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return image.crop((left, top, left + side, top + side))


def rounded_icon(image: Image.Image, size: int) -> Image.Image:
    source = crop_square(image.convert("RGBA")).resize((size, size), Image.LANCZOS)
    radius = round(size * ROUND_RATIO)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(source, (0, 0))
    output.putalpha(mask)
    return output


def draw_centered_text(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], text: str, font, fill: str) -> None:
    left, top, right, bottom = bounds
    draw.text(((left + right) / 2, (top + bottom) / 2), text, font=font, fill=fill, anchor="mm")


def draw_card(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], fill: str, outline: Optional[str] = None) -> None:
    draw.rounded_rectangle(bounds, radius=CARD_RADIUS, fill=fill, outline=outline, width=2 if outline else 0)


def paste_center(canvas: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = box
    x = round(left + (right - left - image.width) / 2)
    y = round(top + (bottom - top - image.height) / 2)
    canvas.paste(image, (x, y), image)


def create_board(icon_paths: list[Path], output_path: Path, labels: list[str], app_name: str, title: Optional[str]) -> None:
    icons = [Image.open(path) for path in icon_paths]
    title_text = title or (f"{app_name} Icon Review" if app_name else "App Icon Review")
    canvas_w = PADDING * 2 + len(icons) * COLUMN_W + max(0, len(icons) - 1) * COLUMN_GAP
    canvas_h = PADDING * 2 + TITLE_H + HERO_CARD_H + CONTEXT_CARD_H + BOTTOM_STRIP_H + LABEL_GAP * 4
    canvas = Image.new("RGB", (canvas_w, canvas_h), CANVAS_BG)
    draw = ImageDraw.Draw(canvas)

    title_font = load_font(40, bold=True)
    label_font = load_font(24, bold=True)
    meta_font = load_font(18, bold=False)

    draw.text((PADDING, PADDING), title_text, font=title_font, fill=TEXT)

    content_top = PADDING + TITLE_H
    for index, icon in enumerate(icons):
        column_left = PADDING + index * (COLUMN_W + COLUMN_GAP)
        column_right = column_left + COLUMN_W

        label_top = content_top
        draw_centered_text(
            draw,
            (column_left, label_top, column_right, label_top + 26),
            labels[index],
            label_font,
            TEXT,
        )

        hero_top = label_top + 26 + LABEL_GAP
        hero_bounds = (column_left, hero_top, column_right, hero_top + HERO_CARD_H)
        draw_card(draw, hero_bounds, CARD_BG, CARD_BORDER)
        paste_center(canvas, rounded_icon(icon, 228), hero_bounds)

        context_top = hero_bounds[3] + CARD_GAP
        light_bounds = (column_left, context_top, column_left + (COLUMN_W - 12) // 2, context_top + CONTEXT_CARD_H)
        dark_bounds = (light_bounds[2] + 12, context_top, column_right, context_top + CONTEXT_CARD_H)
        draw_card(draw, light_bounds, LIGHT_TILE)
        draw_card(draw, dark_bounds, DARK_TILE)
        paste_center(canvas, rounded_icon(icon, 92), light_bounds)
        paste_center(canvas, rounded_icon(icon, 92), dark_bounds)

        light_label_bounds = (light_bounds[0], light_bounds[3] - 30, light_bounds[2], light_bounds[3] - 6)
        dark_label_bounds = (dark_bounds[0], dark_bounds[3] - 30, dark_bounds[2], dark_bounds[3] - 6)
        draw_centered_text(draw, light_label_bounds, "Light", meta_font, MUTED)
        draw_centered_text(draw, dark_label_bounds, "Dark", meta_font, "#D1D5DB")

        bottom_top = dark_bounds[3] + CARD_GAP
        bottom_bounds = (column_left, bottom_top, column_right, bottom_top + BOTTOM_STRIP_H)
        draw_card(draw, bottom_bounds, HOME_TILE)
        mini_icon = rounded_icon(icon, 64)
        mini_x = column_left + 28
        mini_y = bottom_top + (BOTTOM_STRIP_H - mini_icon.height) // 2
        canvas.paste(mini_icon, (mini_x, mini_y), mini_icon)
        app_label = app_name or "App Name"
        draw.text((mini_x + mini_icon.width + 18, bottom_top + 36), app_label, font=label_font, fill=TEXT)
        draw.text((mini_x + mini_icon.width + 18, bottom_top + 74), "Home screen scale", font=meta_font, fill=MUTED)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, "PNG")
    print(f"✓ {output_path} ({canvas_w}x{canvas_h})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an App Store icon review board")
    parser.add_argument("--icons", nargs="+", required=True, help="Icon paths")
    parser.add_argument("--labels", nargs="*", default=None, help="Labels for each icon")
    parser.add_argument("--app-name", default="", help="App name for the preview strip")
    parser.add_argument("--title", default=None, help="Optional board title")
    parser.add_argument("--output", required=True, help="Output PNG path")
    args = parser.parse_args()

    icon_paths = [Path(path) for path in args.icons]
    labels = args.labels or [path.stem for path in icon_paths]
    if len(labels) != len(icon_paths):
        raise SystemExit("The number of labels must match the number of icons")

    create_board(icon_paths, Path(args.output), labels, args.app_name, args.title)


if __name__ == "__main__":
    main()
