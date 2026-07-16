#!/usr/bin/env python3
"""
Generate a *placeholder* iPhone frame for frame_compose.py.

This is a deliberately plain, flat device outline — it is NOT a photorealistic
render and is not meant to be. It exists only so frame_compose.py works out of
the box. For production screenshots, supply your own device frame PNG (a real
photographic render) via the ASO_FRAME environment variable; see README.

The frame is a transparent-background RGBA PNG: an opaque rounded body with a
transparent screen cutout and an opaque Dynamic Island pill. frame_compose.py
detects the screen rectangle from the alpha channel, so any frame with the same
structure (transparent screen, opaque island) works as a drop-in replacement.

Run once to (re)create assets/frame-placeholder.png.
"""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "assets", "frame-placeholder.png")

W, H = 1080, 2340
BODY_CORNER = 132
BEZEL = 26
SCREEN_CORNER = 104
BODY_COLOR = (18, 18, 20, 255)
ISLAND_COLOR = (10, 10, 12, 255)

# Dynamic Island pill
DI_W, DI_H = 300, 34
DI_TOP = BEZEL + 30


def main():
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)

    # Opaque rounded body.
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=BODY_CORNER, fill=BODY_COLOR)

    # Transparent screen cutout (punch a hole in the alpha channel).
    cut = Image.new("L", (W, H), 255)
    ImageDraw.Draw(cut).rounded_rectangle(
        [BEZEL, BEZEL, W - BEZEL, H - BEZEL], radius=SCREEN_CORNER, fill=0)
    frame.putalpha(Image.composite(frame.getchannel("A"), Image.new("L", (W, H), 0), cut))

    # Opaque Dynamic Island pill (frame_compose measures this to clear the
    # status bar).
    dx = (W - DI_W) // 2
    ImageDraw.Draw(frame).rounded_rectangle(
        [dx, DI_TOP, dx + DI_W, DI_TOP + DI_H], radius=DI_H // 2, fill=ISLAND_COLOR)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    frame.save(OUT, "PNG")
    print(f"wrote {OUT} ({W}x{H}); screen ~= ({BEZEL},{BEZEL})-({W - BEZEL},{H - BEZEL})")


if __name__ == "__main__":
    main()
