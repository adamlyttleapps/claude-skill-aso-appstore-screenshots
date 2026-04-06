#!/usr/bin/env python3
"""
App Store / Google Play Screenshot Composer
Composites headline text, device frame template, and app screenshot
into a pixel-perfect store-ready image.

Supports multiple device profiles via --device flag:
  iphone-6.7  (default) — 1290×2796, App Store Connect
  iphone-6.5  — 1242×2688, App Store Connect
  iphone-6.9  — 1320×2868, App Store Connect
  android      — 1080×1920, Google Play Store
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont, ImageChops

SKILL_DIR = os.path.dirname(__file__)
FONT_PATH = "/Library/Fonts/SF-Pro-Display-Black.otf"

# ── Device profiles ─────────────────────────────────────────────────
# All layout values are derived from canvas size so each profile
# produces correctly proportioned output.
DEVICE_PROFILES = {
    "iphone-6.7": {
        "canvas": (1290, 2796),
        "device_w": 1030,
        "bezel": 15,
        "screen_corner_r": 62,
        "device_y": 720,
        "text_top": 200,
        "frame_file": "device_frame.png",
    },
    "iphone-6.5": {
        "canvas": (1242, 2688),
        "device_w": 994,
        "bezel": 15,
        "screen_corner_r": 60,
        "device_y": 692,
        "text_top": 192,
        "frame_file": "device_frame.png",
    },
    "iphone-6.9": {
        "canvas": (1320, 2868),
        "device_w": 1056,
        "bezel": 15,
        "screen_corner_r": 64,
        "device_y": 738,
        "text_top": 205,
        "frame_file": "device_frame.png",
    },
    "android": {
        "canvas": (1080, 2400),
        "device_w": 864,
        "bezel": 8,
        "screen_corner_r": 44,
        "device_y": 625,
        "text_top": 163,
        "frame_file": "device_frame_android.png",
    },
}

# ── Typography (proportional to canvas width) ───────────────────────
TEXT_W_RATIO = 0.92        # max text width as fraction of canvas
VERB_SIZE_MAX_RATIO = 0.198   # ~256/1290
VERB_SIZE_MIN_RATIO = 0.116   # ~150/1290
DESC_SIZE_RATIO = 0.096       # ~124/1290
VERB_DESC_GAP = 20
DESC_LINE_GAP = 24


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


def fit_font(text, max_w, size_max, size_min):
    """Return the largest font size where text fits within max_w."""
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for size in range(size_max, size_min - 1, -4):
        font = ImageFont.truetype(FONT_PATH, size)
        bbox = dummy.textbbox((0, 0), text, font=font)
        if (bbox[2] - bbox[0]) <= max_w:
            return font
    return ImageFont.truetype(FONT_PATH, size_min)


def draw_centered(draw, y, text, font, canvas_w, max_w=None):
    lines = word_wrap(draw, text, font, max_w) if max_w else [text]
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        draw.text((canvas_w // 2, y - bbox[1]), line, fill="white", font=font, anchor="mt")
        y += h + DESC_LINE_GAP
    return y


def compose(bg_hex, verb, desc, screenshot_path, output_path, device="iphone-6.7"):
    profile = DEVICE_PROFILES[device]
    canvas_w, canvas_h = profile["canvas"]
    device_w = profile["device_w"]
    bezel = profile["bezel"]
    screen_w = device_w - 2 * bezel
    screen_corner_r = profile["screen_corner_r"]
    device_y = profile["device_y"]
    text_top = profile["text_top"]
    frame_path = os.path.join(SKILL_DIR, "assets", profile["frame_file"])

    # Compute typography sizes from canvas width
    max_text_w = int(canvas_w * TEXT_W_RATIO)
    max_verb_w = int(canvas_w * TEXT_W_RATIO)
    verb_size_max = int(canvas_w * VERB_SIZE_MAX_RATIO)
    verb_size_min = int(canvas_w * VERB_SIZE_MIN_RATIO)
    desc_size = int(canvas_w * DESC_SIZE_RATIO)

    bg = hex_to_rgb(bg_hex)

    # ── 1. Canvas ───────────────────────────────────────────────────
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (*bg, 255))
    draw = ImageDraw.Draw(canvas)

    # ── 2. Text ─────────────────────────────────────────────────────
    verb_font = fit_font(verb.upper(), max_verb_w, verb_size_max, verb_size_min)
    desc_font = ImageFont.truetype(FONT_PATH, desc_size)

    y = text_top
    y = draw_centered(draw, y, verb.upper(), verb_font, canvas_w)
    y += VERB_DESC_GAP
    draw_centered(draw, y, desc.upper(), desc_font, canvas_w, max_w=max_text_w)

    device_x = (canvas_w - device_w) // 2
    screen_x = device_x + bezel
    screen_y = device_y + bezel

    # ── 3. Screenshot into screen area ──────────────────────────────
    shot = Image.open(screenshot_path).convert("RGBA")
    visible_screen_h = canvas_h - screen_y + 500
    # Scale to fill: use the larger scale factor so the screenshot
    # covers both width and visible height (no black gaps)
    scale_w = screen_w / shot.width
    scale_h = visible_screen_h / shot.height
    scale = max(scale_w, scale_h)
    sc_w = int(shot.width * scale)
    sc_h = int(shot.height * scale)
    shot = shot.resize((sc_w, sc_h), Image.LANCZOS)

    screen_h = canvas_h - screen_y + 500

    scr_mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(scr_mask).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=screen_corner_r,
        fill=255,
    )

    scr_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(scr_layer).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=screen_corner_r,
        fill=(0, 0, 0, 255),
    )
    scr_layer.paste(shot, (screen_x, screen_y))
    scr_layer.putalpha(scr_mask)
    canvas = Image.alpha_composite(canvas, scr_layer)

    # ── 4. Device frame template ───────────────────────────────────
    frame_template = Image.open(frame_path).convert("RGBA")

    # Scale frame if device_w differs from template width
    if frame_template.width != device_w:
        scale_f = device_w / frame_template.width
        frame_template = frame_template.resize(
            (device_w, int(frame_template.height * scale_f)), Image.LANCZOS
        )

    frame_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    frame_layer.paste(frame_template, (device_x, device_y))
    canvas = Image.alpha_composite(canvas, frame_layer)

    # ── 5. Save ────────────────────────────────────────────────────
    canvas.convert("RGB").save(output_path, "PNG")
    print(f"✓ {output_path} ({canvas_w}×{canvas_h}) [{device}]")


def main():
    p = argparse.ArgumentParser(description="Compose store screenshot")
    p.add_argument("--bg", required=True, help="Background hex colour (#E31837)")
    p.add_argument("--verb", required=True, help="Action verb (TRACK)")
    p.add_argument("--desc", required=True, help="Benefit descriptor (TRADING CARD PRICES)")
    p.add_argument("--screenshot", required=True, help="Simulator/emulator screenshot path")
    p.add_argument("--output", required=True, help="Output file path")
    p.add_argument(
        "--device",
        choices=list(DEVICE_PROFILES.keys()),
        default="iphone-6.7",
        help="Device profile (default: iphone-6.7)",
    )
    args = p.parse_args()

    compose(args.bg, args.verb, args.desc, args.screenshot, args.output, device=args.device)


if __name__ == "__main__":
    main()
