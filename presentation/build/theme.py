"""Dark theme constants. Colours sampled from the pre-theory-deck pptx
(see extract_assets.py output)."""
from pathlib import Path

from pptx.dml.color import RGBColor
from pptx.util import Inches

SLIDE_W = 12192000
SLIDE_H = 6858000
TIP_BAND_H = Inches(0.7)
MARGIN = Inches(0.5)

COLORS = {
    "bg": RGBColor(0x08, 0x0D, 0x1A),       # bg.png corner
    "surface": RGBColor(0x1E, 0x29, 0x3B),  # bg.png centre / card fill
    "text": RGBColor(0xF1, 0xF5, 0xF9),     # most frequent srgbClr
    "muted": RGBColor(0x94, 0xA3, 0xB8),
    "accent": RGBColor(0x60, 0xA5, 0xFA),
    "accent2": RGBColor(0x38, 0xBD, 0xF8),
    "ok": RGBColor(0x34, 0xD3, 0x99),
    "warn": RGBColor(0xFB, 0xBF, 0x24),
    "tip": RGBColor(0xC4, 0xB5, 0xFD),
}

FONTS = {
    "en": {"body": "Plus Jakarta Sans", "head": "Plus Jakarta Sans ExtraBold",
           "mono": "JetBrains Mono"},
    "he": {"body": "Arial", "head": "Arial", "mono": "JetBrains Mono"},
}

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
