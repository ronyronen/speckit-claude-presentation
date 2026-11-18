"""Theme constants: a light paper-and-blueprint look (see backgrounds.py)."""
from pathlib import Path

from pptx.dml.color import RGBColor
from pptx.util import Inches

SLIDE_W = 12192000
SLIDE_H = 6858000
TIP_BAND_H = Inches(0.7)
MARGIN = Inches(0.5)

COLORS = {
    # Light "paper and blueprint" theme: off-white stage, ink-dark text,
    # saturated accents that stay readable on white and on a projector.
    "bg": RGBColor(0xF7, 0xF9, 0xFC),       # stage; also text on accent fills
    "surface": RGBColor(0xFF, 0xFF, 0xFF),  # cards and diagram boxes
    "text": RGBColor(0x0F, 0x17, 0x2A),     # slate 900
    "muted": RGBColor(0x64, 0x74, 0x8B),    # slate 500
    "accent": RGBColor(0x25, 0x63, 0xEB),   # blue 600
    "accent2": RGBColor(0x02, 0x84, 0xC7),  # sky 600
    "ok": RGBColor(0x05, 0x96, 0x69),       # emerald 600
    "warn": RGBColor(0xD9, 0x77, 0x06),     # amber 600
    "tip": RGBColor(0x7C, 0x3A, 0xED),      # violet 600 (gate pills)
    "bulb": RGBColor(0xF5, 0x9E, 0x0B),     # tip icon + tip stripe
    "tip_band": RGBColor(0xFF, 0xF7, 0xE6),  # warm paper behind the tip
    "tip_text": RGBColor(0x78, 0x35, 0x0F),  # amber 900 on the tip band
    "code_bg": RGBColor(0x0F, 0x17, 0x2A),  # code cards stay dark
    "code_text": RGBColor(0x86, 0xEF, 0xAC),
}

FONTS = {
    # Fonts every PowerPoint machine (Mac and Windows) already has, so the
    # deck looks the same on the presenting laptop as in the render checks.
    "en": {"body": "Arial", "head": "Arial", "mono": "Courier New"},
    "he": {"body": "Arial", "head": "Arial", "mono": "Courier New"},
}

# Tip light-bulb icon (assets/tip-bulb.png, drawn by icons.py): square side.
ICON = Inches(0.5)
FOOTER_PT = 14
BULLET_SPACE = 0.4  # space before each bullet paragraph, in ems of the font size

# Resolved relative to this file so it works from any cwd.
ASSETS = Path(__file__).resolve().parents[1] / "assets"


def content_box(has_tip: bool):
    """(left, top, width, height) in EMU of the area below the title."""
    top = MARGIN + Inches(1.0)
    bottom_reserved = MARGIN + (TIP_BAND_H if has_tip else 0)
    return (MARGIN, top, SLIDE_W - 2 * MARGIN, SLIDE_H - top - bottom_reserved)


def tip_box():
    """(left, top, width, height) in EMU of the bottom TIP band."""
    return (MARGIN, SLIDE_H - MARGIN - TIP_BAND_H, SLIDE_W - 2 * MARGIN, TIP_BAND_H)
