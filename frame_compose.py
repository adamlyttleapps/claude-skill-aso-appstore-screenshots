#!/usr/bin/env python3
"""
App Store screenshot composer — "floating device" style.

An alternative to compose.py: instead of a flat frame on a solid background,
this composites the screenshot into a device frame PNG, floats it on a dark
radial-glow background, and sets a sentence-case headline above it. Output is
1290x2796 (App Store Connect 6.7").

Frame and font are both configurable via environment variables:

  ASO_FRAME   path to a device frame PNG (transparent screen cutout, opaque
              Dynamic Island). Defaults to the bundled *placeholder* frame,
              which is a plain flat outline — supply a real photographic device
              render here for production-quality output.
  ASO_FONT    path to a bold display .ttf/.otf for the headline. Defaults to a
              per-platform system font; override to match your brand.
  ASO_GLOW    optional "R,G,B" for the background glow (default violet).

The screen rectangle is detected from the frame's alpha channel, so any frame
with a transparent screen + opaque island works as a drop-in replacement.
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(__file__)
FRAME_PATH = os.environ.get("ASO_FRAME") or os.path.join(
    HERE, "assets", "frame-placeholder.png")


def _resolve_font():
    """First existing font from ASO_FONT then common per-platform defaults."""
    for path in (
        os.environ.get("ASO_FONT"),
        "/Library/Fonts/SF-Pro-Display-Black.otf",              # macOS
        "/System/Library/Fonts/SFCompactDisplay-Bold.otf",      # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Debian/Ubuntu
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",                      # Windows
    ):
        if path and os.path.exists(path):
            return path
    raise SystemExit(
        "No usable font found. Set ASO_FONT=/path/to/font.ttf (a bold display "
        "face) — see README.")


FONT_PATH = _resolve_font()

# App Store 6.7" canvas
CANVAS_W, CANVAS_H = 1290, 2796

# Layout
BG_BASE = (14, 14, 18)            # #0E0E12
GLOW = tuple(int(c) for c in os.environ.get("ASO_GLOW", "150,92,255").split(","))
PHONE_W_FRAC = 0.82               # phone width as fraction of canvas
PHONE_TOP_FRAC = 0.205            # phone top as fraction of canvas height
HEAD_TOP_FRAC = 0.066
HEAD_SIZE = 132
HEAD_LINE_GAP = 18
HEAD_COLOR = (245, 245, 250)


def build_background():
    yy, xx = np.mgrid[0:CANVAS_H, 0:CANVAS_W].astype(np.float32)
    cx, cy = CANVAS_W * 0.5, CANVAS_H * -0.02
    d = np.sqrt(((xx - cx) / (CANVAS_W * 0.72)) ** 2 +
                ((yy - cy) / (CANVAS_H * 0.40)) ** 2)
    inten = np.clip(1.0 - d, 0.0, 1.0) ** 1.7
    base = np.array(BG_BASE, np.float32)
    glow = np.array(GLOW, np.float32)
    img = base[None, None, :] + inten[:, :, None] * (glow - base)[None, None, :]
    img = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(img, "RGB").convert("RGBA")


def detect_screen(alpha):
    """Locate the screen rectangle (the interior transparent cutout).

    Scans the middle row for the screen's horizontal span, then a column just
    inside the left edge (which clears the centered island) for the vertical
    span. Falls back to a proportional rectangle if the frame has no detectable
    transparent screen.
    """
    h, w = alpha.shape
    transparent = alpha < 16
    xs = np.where(transparent[h // 2])[0]
    if len(xs):
        x0, x1 = int(xs.min()), int(xs.max()) + 1
        probe = x0 + max(4, (x1 - x0) // 20)
        ys = np.where(transparent[:, probe])[0]
        if len(ys) and (x1 - x0) > w * 0.4 and (int(ys.max()) - int(ys.min())) > h * 0.4:
            return x0, int(ys.min()), x1, int(ys.max()) + 1
    # Fallback: assume a thin uniform bezel.
    bx, by = int(w * 0.045), int(h * 0.02)
    return bx, by, w - bx, h - by


def frame_screenshot(shot_path):
    """Composite the screenshot into the device frame; return the RGBA phone.

    The full screenshot is shown with no vertical crop: it is contain-fit into
    the screen below a status-bar gap that clears the Dynamic Island. Any small
    leftover (thin side margins) is backfilled with the screen's own top colour.
    """
    frame = Image.open(FRAME_PATH).convert("RGBA")
    alpha = np.asarray(frame)[:, :, 3]
    x0, y0, x1, y1 = detect_screen(alpha)
    sw, sh = x1 - x0, y1 - y0

    # Measure the Dynamic Island (opaque cluster in the top of the screen) so
    # the status-bar gap clears it exactly.
    band = alpha[y0:y0 + int(sh * 0.16), x0:x1] > 200
    rows = np.where(band.any(axis=1))[0]
    di_bottom = (y0 + int(rows.max())) if len(rows) else y0
    gap = (di_bottom - y0) + max(20, int(sh * 0.012))

    shot = Image.open(shot_path).convert("RGBA")
    avail_w, avail_h = sw, sh - gap
    scale = min(avail_w / shot.width, avail_h / shot.height)
    nw, nh = round(shot.width * scale), round(shot.height * scale)
    rs = shot.resize((nw, nh), Image.LANCZOS)

    top_row = np.asarray(rs)[0:6].reshape(-1, 4)
    fill = tuple(int(c) for c in np.median(top_row, axis=0))
    screen_layer = Image.new("RGBA", (sw, sh), fill)
    ox = (sw - nw) // 2
    oy = gap + (avail_h - nh) // 2
    screen_layer.paste(rs, (ox, oy))

    phone = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    phone.paste(screen_layer, (x0, y0))
    phone = Image.alpha_composite(phone, frame)
    return phone


def compose(shot_path, lines, output):
    canvas = build_background()
    draw = ImageDraw.Draw(canvas)

    # ── Phone ───────────────────────────────────────────────
    phone = frame_screenshot(shot_path)
    pw = int(CANVAS_W * PHONE_W_FRAC)
    ph = round(phone.height * pw / phone.width)
    phone = phone.resize((pw, ph), Image.LANCZOS)
    px = (CANVAS_W - pw) // 2
    py = int(CANVAS_H * PHONE_TOP_FRAC)
    canvas.alpha_composite(phone, (px, py))

    # ── Headline ────────────────────────────────────────────
    # Keep each supplied line on one line: shrink the font until the widest fits.
    max_w = int(CANVAS_W * 0.86)
    size = HEAD_SIZE
    while size > 74:
        font = ImageFont.truetype(FONT_PATH, size)
        if all(draw.textlength(ln, font=font) <= max_w for ln in lines):
            break
        size -= 4
    font = ImageFont.truetype(FONT_PATH, size)
    y = int(CANVAS_H * HEAD_TOP_FRAC)
    for ln in lines:
        bbox = draw.textbbox((0, 0), ln, font=font)
        h = bbox[3] - bbox[1]
        draw.text((CANVAS_W // 2, y - bbox[1]), ln, fill=HEAD_COLOR, font=font, anchor="mt")
        y += h + HEAD_LINE_GAP

    canvas.convert("RGB").save(output, "PNG")
    print(f"wrote {output} ({CANVAS_W}x{CANVAS_H})")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--screenshot", required=True)
    p.add_argument("--line1", required=True)
    p.add_argument("--line2", default="")
    p.add_argument("--output", required=True)
    a = p.parse_args()
    lines = [a.line1] + ([a.line2] if a.line2 else [])
    compose(a.screenshot, lines, a.output)


if __name__ == "__main__":
    main()
