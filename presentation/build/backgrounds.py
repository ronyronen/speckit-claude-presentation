"""Draw the slide backgrounds (PNG, 16:9) into presentation/assets.

    python3 -m presentation.build.backgrounds

bg.png        content slides: deep navy with a faint blueprint grid (the
              spec as a blueprint) and a soft blue glow in one corner.
bg-title.png  title and section slides: near-black with a glowing horizon
              of blue, violet and cyan light, keynote style.
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
    im = _vertical((7, 11, 22), (11, 19, 36)).convert("RGBA")
    # grid strongest towards the bottom-right, almost gone behind the title
    mask = _radial_mask((W * 0.35, H * 0.25, W * 1.45, H * 1.6), 260, base=40)
    im = _grid(im, 48, 240, 22, 50, mask)
    im = _glow(im, (W * 0.62, H * 0.55, W * 1.25, H * 1.45), BLUE, 70, 220)
    im = _glow(im, (-W * 0.25, -H * 0.45, W * 0.35, H * 0.35), VIOLET, 38, 220)
    _dither(im).save(path)
    return path


def make_title_bg(path=ASSETS / "bg-title.png"):
    im = Image.new("RGBA", (W, H), (3, 5, 11, 255))
    mask = _radial_mask((-W * 0.1, -H * 0.6, W * 1.1, H * 0.75), 200, base=0)
    im = _grid(im, 60, 300, 10, 24, mask)
    # light rising behind a dark "planet" whose edge is the horizon
    planet = (-W * 0.3, H * 0.80, W * 1.3, H * 2.2)
    im = _glow(im, (W * 0.0, H * 0.62, W * 0.55, H * 1.05), VIOLET, 200, 120)
    im = _glow(im, (W * 0.45, H * 0.62, W * 1.0, H * 1.05), CYAN, 180, 120)
    im = _glow(im, (W * 0.2, H * 0.60, W * 0.8, H * 1.0), BLUE, 230, 110)
    body = Image.new("L", (W, H), 0)
    ImageDraw.Draw(body).ellipse(planet, fill=255)
    dark = Image.new("RGBA", (W, H), (4, 7, 16, 0))
    dark.putalpha(body.filter(ImageFilter.GaussianBlur(3)))
    im = Image.alpha_composite(im, dark)
    # faint inner light just under the rim
    im = _glow(im, (W * 0.25, H * 0.82, W * 0.75, H * 1.1), BLUE, 60, 60)
    rim = Image.new("L", (W, H), 0)
    ImageDraw.Draw(rim).ellipse(planet, outline=230, width=3)
    rim = rim.filter(ImageFilter.GaussianBlur(1.5))
    layer = Image.new("RGBA", (W, H), (210, 230, 255, 0))
    layer.putalpha(rim)
    im = Image.alpha_composite(im, layer)
    # darken the top so the type sits on black
    im = _glow(im, (-W * 0.2, -H * 0.9, W * 1.2, H * 0.55), (3, 5, 11), 160, 120)
    _dither(im, 5).save(path)
    return path


if __name__ == "__main__":
    print(make_content_bg())
    print(make_title_bg())
