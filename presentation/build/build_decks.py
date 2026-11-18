"""Generate the EN and HE decks from presentation/content/deck.yaml.

    python3 -m presentation.build.build_decks --lang en|he|both
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pptx import Presentation

from .layouts import LAYOUTS
from .model import load_deck, timing_prefixes
from .shapes import DIAGRAMS
from .text import set_rtl
from .theme import SLIDE_H, SLIDE_W
from .validate import validate

PRES = Path(__file__).resolve().parents[1]
DECK = PRES / "content" / "deck.yaml"
OUT = {"en": PRES / "speckit-workshop.pptx", "he": PRES / "speckit-workshop-he.pptx"}
BLANK = 6


def new_presentation():
    prs = Presentation()
    prs.slide_width, prs.slide_height = SLIDE_W, SLIDE_H
    return prs


def _notes(slide, text, lang):
    tf = slide.notes_slide.notes_text_frame
    tf.text = text
    if lang == "he":
        for p in tf.paragraphs:
            set_rtl(p)


def build(deck_path: str, lang: str, out_path: str) -> None:
    deck = load_deck(deck_path)
    errs = validate(deck, set(DIAGRAMS))
    if errs:
        raise SystemExit("deck.yaml is invalid:\n" + "\n".join(errs))
    prefixes = timing_prefixes(deck)
    prs = new_presentation()
    for s in deck.slides:
        if s.layout not in LAYOUTS:
            raise SystemExit(f"{s.id}: unknown layout {s.layout!r}")
        slide = prs.slides.add_slide(prs.slide_layouts[BLANK])
        slide._element.cSld.set("name", s.id)
        LAYOUTS[s.layout](slide, s, lang, deck.glossary_keep_en)
        _notes(slide, prefixes[s.id] + "\n" + s.notes.get(lang, ""), lang)
    prs.save(out_path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lang", choices=["en", "he", "both"], default="both")
    ap.add_argument("--deck", default=str(DECK))
    args = ap.parse_args(argv)
    for lang in (["en", "he"] if args.lang == "both" else [args.lang]):
        build(args.deck, lang, str(OUT[lang]))
        print(f"wrote {OUT[lang]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
