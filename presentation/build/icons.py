"""Draw the Tip light-bulb icon (transparent PNG) into presentation/assets.

    python3 -m presentation.build.icons
"""
import math

from PIL import Image, ImageDraw

from .theme import ASSETS

BULB = ASSETS / "tip-bulb.png"
GLOW = (252, 211, 77, 255)      # amber 300
BASE = (148, 163, 184, 255)     # slate 400 (theme "muted")


def make_bulb(path=BULB, size=256):
    s = 4 * size  # supersample, then downscale for smooth edges
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = s / 32  # 32-unit grid
    cx, cy, r = 16 * u, 13.5 * u, 7.5 * u
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GLOW)
    d.polygon([(cx - 5.2 * u, cy + 5.2 * u), (cx + 5.2 * u, cy + 5.2 * u),
               (cx + 3.4 * u, 24 * u), (cx - 3.4 * u, 24 * u)], fill=GLOW)
    for y in (24.8, 27.0):
        d.rounded_rectangle([cx - 3.6 * u, y * u, cx + 3.6 * u, (y + 1.5) * u],
                            radius=0.75 * u, fill=BASE)
    d.rounded_rectangle([cx - 2 * u, 29 * u, cx + 2 * u, 30.4 * u],
                        radius=0.7 * u, fill=BASE)
    for deg in (-150, -120, -90, -60, -30):  # rays above the glass
        a = math.radians(deg)
        p1 = (cx + (r + 1.6 * u) * math.cos(a), cy + (r + 1.6 * u) * math.sin(a))
        p2 = (cx + (r + 3.4 * u) * math.cos(a), cy + (r + 3.4 * u) * math.sin(a))
        d.line([p1, p2], fill=GLOW, width=int(1.2 * u))
    im.resize((size, size), Image.LANCZOS).save(path)
    return path


if __name__ == "__main__":
    print(make_bulb())
