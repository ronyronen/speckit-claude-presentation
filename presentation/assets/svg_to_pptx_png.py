#!/usr/bin/env python3
"""Converts docs/images/diagram-*.svg to PNG for embedding in the pptx.

Does NOT modify the source SVGs. The source files are kept in normal
(logical) Unicode order because that is what renders correctly when a
browser opens/embeds them directly (GitHub's inline SVG rendering,
docs/textbook.md's <img> reference, etc. -- real browsers apply the
Unicode Bidi Algorithm to SVG <text> content).

cairosvg, however, does NOT implement the Unicode Bidi Algorithm -- it
draws each <text> element's characters in raw logical order, which comes
out mirrored/garbled for Hebrew. So for this one conversion step only, we
work on an in-memory copy with each <text> element's content pre-ordered
via python-bidi's get_display(), and discard that copy immediately after
rendering to PNG.
"""
import glob
import os
import re
import sys

from bidi.algorithm import get_display

os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib")
import cairosvg  # noqa: E402

TEXT_RE = re.compile(r"(<text\b[^>]*>)(.*?)(</text>)", re.DOTALL)


def bidi_fix(svg_source: str) -> str:
    def repl(m: re.Match) -> str:
        open_tag, text, close_tag = m.group(1), m.group(2), m.group(3)
        return f"{open_tag}{get_display(text)}{close_tag}"

    return TEXT_RE.sub(repl, svg_source)


def convert(svg_path: str, out_dir: str, scale: float = 2.5) -> str:
    with open(svg_path, encoding="utf-8") as f:
        source = f.read()
    fixed = bidi_fix(source)
    base = os.path.splitext(os.path.basename(svg_path))[0]
    out_path = os.path.join(out_dir, f"{base}.png")
    cairosvg.svg2png(bytestring=fixed.encode("utf-8"), write_to=out_path, scale=scale)
    return out_path


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "presentation/assets/generated"
    os.makedirs(out_dir, exist_ok=True)
    for svg_path in sorted(glob.glob("docs/images/diagram-*.svg")):
        out = convert(svg_path, out_dir)
        print(f"{svg_path} -> {out}")
