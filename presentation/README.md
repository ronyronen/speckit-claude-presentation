# Presentation source material

- [`presentation-outline.md`](presentation-outline.md) — full slide-by-slide Hebrew outline
- [`slide-links.md`](slide-links.md) — reference links for the deck
- [`screenshot-checklist.md`](screenshot-checklist.md) — exact captures still needed, and what's already covered by real generated content
- [`speckit-workshop-draft.pptx`](speckit-workshop-draft.pptx) — reviewable draft deck built from the above (see below)
- [`assets/`](assets/) — diagrams, generated content cards, and the build scripts

## Building/updating the draft deck

```bash
# 1. Regenerate diagram PNGs from docs/images/diagram-*.svg (bidi-corrected for pptx embedding)
python3 presentation/assets/svg_to_pptx_png.py

# 2. Regenerate terminal/code content cards from real captured output
python3 presentation/assets/make_content_cards.py

# 3. Build the pptx
python3 presentation/build_deck.py
```

Re-run all three after editing a diagram SVG, updating a content card's
captured text, or changing `presentation/build_deck.py`. The source SVGs
under `docs/images/` are kept in normal (logical) Hebrew order — correct
for browsers/GitHub — and are only bidi-reordered in-memory for the
cairosvg-based PNG conversion step, which does not implement the Unicode
Bidi Algorithm.

To visually review the deck without PowerPoint/Keynote:

```bash
soffice --headless --convert-to pdf --outdir /tmp/deck_review presentation/speckit-workshop-draft.pptx
pdftoppm -png -r 110 /tmp/deck_review/speckit-workshop-draft.pdf /tmp/deck_review/slide
```

(requires `brew install --cask libreoffice` and `brew install poppler`).
