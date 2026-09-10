#!/usr/bin/env python3
"""Converts docs/images/diagram-*-en.svg (pure English/LTR) to PNG for
the English deck. No bidi handling needed -- unlike the Hebrew diagrams
(see svg_to_pptx_png.py), these render correctly in cairosvg as-is.
"""
import glob
import os

os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib")
import cairosvg  # noqa: E402

OUT_DIR = "presentation/assets/generated_en"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for svg_path in sorted(glob.glob("docs/images/diagram-*-en.svg")):
        base = os.path.splitext(os.path.basename(svg_path))[0]
        out_path = os.path.join(OUT_DIR, f"{base}.png")
        cairosvg.svg2png(url=svg_path, write_to=out_path, scale=2.5)
        print(f"{svg_path} -> {out_path}")


if __name__ == "__main__":
    main()
