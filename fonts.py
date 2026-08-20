"""
Font loading that doesn't fall over on a stock Mac.

The upstream skill hardcodes `/Library/Fonts/SF-Pro-Display-<Weight>.otf`. Those
files only exist if you've manually downloaded Apple's font pack from
developer.apple.com/fonts — on a clean macOS install they simply aren't there,
and Pillow dies with a bare `OSError: cannot open resource`.

macOS does ship the same typeface, just packaged differently: `/System/Library/Fonts/SFNS.ttf`
is a *variable* font where every weight (Ultralight → Black) lives inside the one
file as a named instance. So we try the real .otf first and fall back to SFNS
pinned to the weight we asked for.

Order matters: if the .otf pack ever gets installed, the skill silently upgrades
back to it with no code change.
"""

import os

from PIL import ImageFont

# Apple's downloadable font pack — preferred when present.
OTF_TEMPLATE = "/Library/Fonts/SF-Pro-Display-{weight}.otf"

# Always-present system variable font holding every SF weight as a named instance.
SFNS_PATH = "/System/Library/Fonts/SFNS.ttf"


def load_font(size, weight="Black"):
    """
    Load SF Pro Display at the given size and weight.

    @param size - Pixel size to render at
    @param weight - Named weight, e.g. "Black" or "Regular" (must match an
                    SFNS named instance when falling back)
    @returns A Pillow FreeTypeFont ready to draw with
    """
    otf = OTF_TEMPLATE.format(weight=weight)
    if os.path.exists(otf):
        return ImageFont.truetype(otf, size)

    font = ImageFont.truetype(SFNS_PATH, size)
    # Variable fonts load at their default instance — pin the weight explicitly,
    # otherwise every headline quietly renders as Regular.
    font.set_variation_by_name(weight)
    return font
