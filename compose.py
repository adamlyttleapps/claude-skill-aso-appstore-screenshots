#!/usr/bin/env python3
"""
App Store Screenshot Composer
Composites headline text, device frame template, and app screenshot
into a pixel-perfect 1290×2796 App Store Connect image.

The device frame is positioned dynamically based on text height,
matching the proportions seen in professional App Store screenshots.
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont, ImageChops

# ── Canvas ──────────────────────────────────────────────────────────
CANVAS_W = 1290
CANVAS_H = 2796

# ── Device template constants (must match generate_frame.py) ───────
DEVICE_W = 1030
BEZEL = 15
SCREEN_W = DEVICE_W - 2 * BEZEL    # 1000
SCREEN_CORNER_R = 62

# ── Layout ──────────────────────────────────────────────────────────
DEVICE_Y = 720                       # device top position (fixed)
MIN_TEXT_DEVICE_GAP = 40             # minimum gap between text bottom and device top

# ── Typography ──────────────────────────────────────────────────────
VERB_SIZE_MAX = 256
VERB_SIZE_MIN = 150
DESC_SIZE = 124
VERB_DESC_GAP = 20
DESC_LINE_GAP = 24
MAX_TEXT_W = int(CANVAS_W * 0.92)
MAX_VERB_W = int(CANVAS_W * 0.92)

FONT_ROOT = "/Library/Fonts"
DEFAULT_FONT = "SF-Pro-Display-Black.otf"
FRAME_PATH = os.path.join(os.path.dirname(__file__), "assets", "device_frame.png")


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def word_wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(text, max_w, size_max, size_min, font_path):
    """Return the largest font size where text fits within max_w."""
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for size in range(size_max, size_min - 1, -4):
        f = ImageFont.truetype(font_path, size)
        bbox = dummy.textbbox((0, 0), text, font=f)
        if (bbox[2] - bbox[0]) <= max_w:
            return f
    return ImageFont.truetype(font_path, size_min)


def draw_centered(draw, y, text, font, max_w=None):
    lines = word_wrap(draw, text, font, max_w) if max_w else [text]
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        # Use anchor="mt" (middle-top) for pixel-perfect horizontal centering
        # Adjust y by bbox[1] offset so text top aligns with intended position
        draw.text((CANVAS_W // 2, y - bbox[1]), line, fill="white", font=font, anchor="mt")
        y += h + DESC_LINE_GAP
    return y


def compose(bg_hex, verb, desc, screenshot_path, output_path, font):
    bg = hex_to_rgb(bg_hex)
    font_path = os.path.join(FONT_ROOT, font)

    # ── 1. Canvas ───────────────────────────────────────────────────
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (*bg, 255))
    draw = ImageDraw.Draw(canvas)

    # ── 2. Measure text, then center between top of canvas & device ─
    verb_font = fit_font(verb.upper(), MAX_VERB_W, VERB_SIZE_MAX, VERB_SIZE_MIN, font_path)
    desc_font = ImageFont.truetype(font_path, DESC_SIZE)

    # Measure total text block height (dry run at y=0)
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    m_y = 0
    m_y = draw_centered(dummy, m_y, verb.upper(), verb_font)
    m_y += VERB_DESC_GAP
    text_height = draw_centered(dummy, m_y, desc.upper(), desc_font, max_w=MAX_TEXT_W)

    # Device at fixed Y; text starts at fixed position
    device_y = DEVICE_Y
    text_top = 200

    # Draw text at centered position
    y = text_top
    y = draw_centered(draw, y, verb.upper(), verb_font)
    y += VERB_DESC_GAP
    draw_centered(draw, y, desc.upper(), desc_font, max_w=MAX_TEXT_W)
    device_x = (CANVAS_W - DEVICE_W) // 2
    screen_x = device_x + BEZEL
    screen_y = device_y + BEZEL

    # ── 4. Screenshot into screen area ──────────────────────────────
    shot = Image.open(screenshot_path).convert("RGBA")

    # Scale to fill screen width
    scale = SCREEN_W / shot.width
    sc_w = SCREEN_W
    sc_h = int(shot.height * scale)
    shot = shot.resize((sc_w, sc_h), Image.LANCZOS)

    # Screen extends to bottom of canvas + overflow
    screen_h = CANVAS_H - screen_y + 500

    # Screen mask (rounded rect)
    scr_mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(scr_mask).rounded_rectangle(
        [screen_x, screen_y, screen_x + SCREEN_W, screen_y + screen_h],
        radius=SCREEN_CORNER_R,
        fill=255,
    )

    # Black screen bg + screenshot on top
    scr_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(scr_layer).rounded_rectangle(
        [screen_x, screen_y, screen_x + SCREEN_W, screen_y + screen_h],
        radius=SCREEN_CORNER_R,
        fill=(0, 0, 0, 255),
    )
    scr_layer.paste(shot, (screen_x, screen_y))
    scr_layer.putalpha(scr_mask)

    canvas = Image.alpha_composite(canvas, scr_layer)

    # ── 6. Device frame template ───────────────────────────────────
    frame_template = Image.open(FRAME_PATH).convert("RGBA")

    # Place frame template onto canvas-sized layer at calculated position
    frame_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    frame_layer.paste(frame_template, (device_x, device_y))
    canvas = Image.alpha_composite(canvas, frame_layer)

    # ── 7. Save ────────────────────────────────────────────────────
    canvas.convert("RGB").save(output_path, "PNG")
    print(f"✓ {output_path} ({CANVAS_W}×{CANVAS_H})")


def main():
    p = argparse.ArgumentParser(description="Compose App Store screenshot")
    p.add_argument("--bg", required=True, help="Background hex colour (#E31837)")
    p.add_argument("--font", help="Font filename in /Library/Fonts (default: SF-Pro-Display-Black.otf)", default=DEFAULT_FONT)
    p.add_argument("--verb", required=True, help="Action verb (TRACK)")
    p.add_argument("--desc", required=True, help="Benefit descriptor (TRADING CARD PRICES)")
    p.add_argument("--screenshot", required=True, help="Simulator screenshot path")
    p.add_argument("--output", required=True, help="Output file path")
    args = p.parse_args()

    compose(args.bg, args.verb, args.desc, args.screenshot, args.output, args.font)


if __name__ == "__main__":
    main()
