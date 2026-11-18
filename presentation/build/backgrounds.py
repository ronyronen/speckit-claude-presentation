"""Draw the slide backgrounds (PNG, 16:9) into presentation/assets.

    python3 -m presentation.build.backgrounds

bg.png        content slides: off-white paper with a faint blueprint grid
              (the spec as a blueprint) and soft pastel light in two corners.
bg-title.png  title and section slides: a bright stage with a pastel aurora
              rising behind a soft horizon, keynote style.
"""
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from .theme import ASSETS

W, H = 1920, 1080
BLUE = (59, 130, 246)
SKY = (56, 189, 248)
VIOLET = (139, 92, 246)
CYAN = (34, 211, 238)
GRID = (96, 165, 250)


def _vertical(top, bottom):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))
    return im


def _glow(im, box, color, alpha, blur):
    """Blend a blurred ellipse of colour over im (additive-looking light)."""
    layer = Image.new("RGBA", (W, H), color + (0,))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse(box, fill=alpha)
    layer.putalpha(mask.filter(ImageFilter.GaussianBlur(blur)))
    return Image.alpha_composite(im, layer)


def _grid(im, minor, major, a_minor, a_major, mask):
    layer = Image.new("RGBA", (W, H), GRID + (0,))
    lines = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(lines)
    for step, a in ((minor, a_minor), (major, a_major)):
        for x in range(0, W, step):
            d.line([(x, 0), (x, H)], fill=a)
        for y in range(0, H, step):
            d.line([(0, y), (W, y)], fill=a)
    layer.putalpha(ImageChops.multiply(lines, mask))
    return Image.alpha_composite(im, layer)


def _radial_mask(box, blur, base=0):
    m = Image.new("L", (W, H), base)
    ImageDraw.Draw(m).ellipse(box, fill=255)
    return m.filter(ImageFilter.GaussianBlur(blur))


def _dither(im, amount=6):
    """Fine noise so the gradients do not band on projectors."""
    noise = Image.effect_noise((W, H), 40).convert("RGB")
    return Image.blend(im.convert("RGB"), noise, amount / 255)


def make_content_bg(path=ASSETS / "bg.png"):
    im = _vertical((250, 251, 254), (238, 243, 251)).convert("RGBA")
    # grid strongest towards the bottom-right, almost gone behind the title
    mask = _radial_mask((W * 0.3, H * 0.2, W * 1.45, H * 1.6), 260, base=60)
    im = _grid(im, 48, 240, 26, 55, mask)
    im = _glow(im, (W * 0.62, H * 0.55, W * 1.25, H * 1.45), (147, 197, 253), 120, 220)
    im = _glow(im, (-W * 0.25, -H * 0.45, W * 0.3, H * 0.3), (196, 181, 253), 90, 200)
    _dither(im, 3).save(path)
    return path


def make_title_bg(path=ASSETS / "bg-title.png"):
    im = _vertical((252, 253, 255), (244, 247, 253)).convert("RGBA")
    mask = _radial_mask((-W * 0.1, -H * 0.6, W * 1.1, H * 0.75), 200, base=0)
    im = _grid(im, 60, 300, 22, 45, mask)
    # pastel aurora rising behind a soft horizon
    planet = (-W * 0.3, H * 0.80, W * 1.3, H * 2.2)
    im = _glow(im, (W * 0.0, H * 0.60, W * 0.55, H * 1.05), (196, 181, 253), 230, 120)
    im = _glow(im, (W * 0.45, H * 0.60, W * 1.0, H * 1.05), (153, 246, 228), 220, 120)
    im = _glow(im, (W * 0.2, H * 0.58, W * 0.8, H * 1.0), (147, 197, 253), 240, 110)
    body = Image.new("L", (W, H), 0)
    ImageDraw.Draw(body).ellipse(planet, fill=255)
    paper = Image.new("RGBA", (W, H), (250, 251, 254, 0))
    paper.putalpha(body.filter(ImageFilter.GaussianBlur(4)).point(lambda v: v * 235 // 255))
    im = Image.alpha_composite(im, paper)
    rim = Image.new("L", (W, H), 0)
    ImageDraw.Draw(rim).ellipse(planet, outline=200, width=3)
    rim = rim.filter(ImageFilter.GaussianBlur(1.5))
    layer = Image.new("RGBA", (W, H), (37, 99, 235, 0))
    layer.putalpha(rim.point(lambda v: v * 150 // 255))
    im = Image.alpha_composite(im, layer)
    _dither(im, 3).save(path)
    return path


if __name__ == "__main__":
    print(make_content_bg())
    print(make_title_bg())
