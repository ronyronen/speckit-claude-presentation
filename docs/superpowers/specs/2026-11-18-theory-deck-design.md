# Technical Design: Theory-First SDD Talk (EN + HE decks)

- **Brief:** [2026-11-18-theory-deck-brief.md](2026-11-18-theory-deck-brief.md). Read it first; this design does not restate its stories, outline or fact-check register.
- **Status:** design decisions approved by the human 2026-11-18. Implementation not started (on hold per human request).
- **Reference article:** V. Dwarampudi, "Spec-Driven AI: BMAD, SpecKit, GSD & Superpowers" (Medium, Jun 2026). The PDF is local only, in `.tmp/`, and is not committed.

## 1. Architecture

```
presentation/
  content/
    deck.yaml          # single source of truth: 25 timed + 4 appendix slides, EN+HE
  build/
    build_decks.py     # python-pptx generator: YAML -> two .pptx files
    validate.py        # sync + timing checks (also run by build_decks.py)
    render_check.sh    # soffice -> pdf -> pdftoppm PNGs for visual review
    theme.py           # palette, fonts, geometry constants, RTL helpers
    shapes.py          # native diagram primitives (box, arrow, loop, rail, curve)
  assets/              # background PNG, photos, code cards extracted from current deck
  speckit-workshop.pptx      # EN output (path unchanged)
  speckit-workshop-he.pptx   # HE output (new)
```

**Flow:** `deck.yaml` → `validate.py` → `build_decks.py --lang en|he` → `.pptx` → `render_check.sh` → PNGs to review.

## 2. Content model (`deck.yaml`)

```yaml
meta: { total_budget: "45:00", article_credit: {...} }
slides:
  - id: intent-gap            # stable key, shared by both languages
    part: I
    budget: "2:30"            # m:ss; appendix slides use 0
    layout: title-bullets-diagram   # one of a small fixed set of layouts
    diagram: sdlc-vs-adlc     # optional, references shapes.py builder
    title:   { en: "...", he: "..." }
    bullets:                  # keyed: both languages must have the same keys
      - { key: static-docs, en: "...", he: "..." }
    notes:   { en: "...", he: "..." }   # generator prepends "[m:ss] [@mm:ss]"
    sources: [F6]             # links to fact-check register IDs
```

**Layouts:** a fixed set of 6 to 8, covering title, section, title-bullets, title-bullets-diagram, two-column compare, table, photo pair, and code card. Each layout is a function in `build_decks.py` that takes a `dir` flag (`ltr` or `rtl`), so the HE deck mirrors the geometry rather than only aligning text to the right.

## 3. Validation (fails the build)

These map to the US-3 and US-4 acceptance criteria:
1. Both languages have the same slide IDs, in the same order. Every slide has `title.en` and `title.he`.
2. Bullet keys and counts are identical in EN and HE.
3. The timed budgets sum to exactly 45:00. The generator computes the `[@mm:ss]` cumulative-end markers rather than taking them from authors.
4. Every timed slide has non-empty notes in both languages.
5. No slash commands or CLI syntax appear in Part I–III slide text (a regex for `/\w+-` and `$ `), per Ruling 5.
6. No star counts (`\d+k\+? stars`) appear in slide text, per N4.

## 4. Theme and RTL

- **Visual baseline:** keep the current deck's dark navy background PNG, colour palette, OK/WARNING photos and code-card look, all extracted into `assets/`. The hand-placed PNG fragments are rebuilt as native shapes.
- **EN fonts:** Plus Jakarta Sans and JetBrains Mono, as now. The fonts must be installed locally so render checks use them and not substitutes.
- **HE font:** Arial in `<a:latin>` and `<a:cs>`, so it works on venue machines. Noto Sans Hebrew is a fallback.
- **HE paragraphs:** `a:pPr rtl="1" algn="r"` and runs with `lang="he-IL"`. Use bullet dots, not numbered lists, because of the known RTL numbering bug. No literal newlines inside a single run. The old `set_rtl` helper is recovered from `git show f85a550:presentation/build_deck.py`.
- **Diagrams in HE:** labels are translated, but the direction of process flow stays left-to-right. This matches the existing HE SVGs and the convention for technical flow diagrams.

## 5. Diagrams (native shapes)

| Diagram | Slide | Phase | Primitive |
|---|---|---|---|
| Four metaphors, two layers | 13 | P1 (Must) | 2×2 grid inside a two-band layer stack: planning/governance vs execution discipline |
| Decision rule flowchart | 15 | P1 (Must) | 3 decision diamonds: long sessions? / human review each phase? / strong TDD habit? → add GSD / add Superpowers |
| SDLC vs ADLC | 3 | P2 | linear chevrons vs circular loop |
| SDD pipeline | 5 | P2 | 5 stages + 2 gate markers + feedback arc + constitution rail |
| Context rot | 8 | P2 | freeform qualitative curve, unlabeled axes |

## 6. Verification

- `validate.py` exits 0.
- `render_check.sh` produces PNGs for every slide of both decks, and a reviewer looks at them for overflow and overlap.
- One manual pass in PowerPoint on the HE deck, over the listed mixed Hebrew/English lines (US-4).
- The F7 citation URL is fetched and confirmed before it goes into the notes.

## 7. Phases (from the brief)

| Phase | Scope | Est. |
|---|---|---|
| P1 | asset extraction, generator, validator, EN content for all 25+4 slides, diagrams for slides 13 and 15, case-study DHT22 fixes | ~1.5–2 d |
| P2 | remaining 3 diagrams | ~0.5 d |
| P3 | HE content and RTL deck, PowerPoint bidi pass, README links (US-10) | ~1–1.5 d |

## 8. Decisions and trade-offs

- **The generator replaces the hand edits.** EN and HE stay in sync, and timing is checked by machine. The cost is that the current deck's hand polish is only approximated (open question 1 in the brief).
- **Diagrams are drawn in PowerPoint, not as SVG/PNG.** They match the dark theme and are translated from the same YAML. The SVG pairs in `docs/images` stay untouched.
- **Old deck.** The current EN deck is overwritten at the same path, but git keeps the previous version, and a tag `pre-theory-deck` is created first.
- **`.tmp/` stays out of the repo.** It holds the article PDF, a third-party copyrighted article, which the talk credits and links instead.
