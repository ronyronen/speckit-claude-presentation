# Technical Design: Theory-First SDD Talk for Beginners (EN + HE decks)

- **Brief:** [2026-11-18-theory-deck-brief.md](2026-11-18-theory-deck-brief.md). The brief holds the stories, the 27-slide outline, the fact-check register, the negotiation log and the human decisions, and this design does not restate them.
- **Status:** design decisions approved by the human on 2026-11-18 (rounds 1 and 2). Implementation has not started and is on hold at the human's request.
- **Reference article:** V. Dwarampudi, "Spec-Driven AI: BMAD, SpecKit, GSD & Superpowers" (Medium, Jun 2026). The PDF is local only, in `.tmp/`, and is not committed.

## 1. Architecture

```
presentation/
  content/
    deck.yaml          # single source of truth: 26 timed + 8 appendix slides, EN+HE (GSD moved to backup; vibe/BMAD/Spec Kit/Superpowers diagrams and a learning-path backup added 2026-11-18)
  build/
    build_decks.py     # python-pptx generator: YAML -> two .pptx files
    validate.py        # sync, timing, tone and fact checks (also run by build_decks.py)
    render_check.sh    # soffice -> pdf -> pdftoppm PNGs for visual review
    theme.py           # palette, fonts, geometry constants (incl. tip band), RTL helpers
    shapes.py          # native diagram primitives (box, arrow, loop, rail, curve)
    icons.py           # draws assets/tip-bulb.png
  assets/              # background PNG, photos, code cards extracted from current deck
  speckit-workshop.pptx      # EN output (path unchanged)
  speckit-workshop-he.pptx   # HE output (new)
  transcript-en.md, transcript-he.md   # talk scripts, generated with the decks
```

**Build pipeline:** `deck.yaml` → `validate.py` → `build_decks.py --lang en|he` → `.pptx` → `render_check.sh` → PNGs, which a person reviews.

## 2. Content model (`deck.yaml`)

```yaml
meta: { total_budget: "45:00", qa_budget: "3:00", article_credit: {...} }
slides:
  - id: intent-gap            # stable key, shared by both languages
    part: I
    budget: "2:30"            # m:ss; appendix slides use 0
    layout: title-bullets-diagram
    diagram: { name: sdlc-vs-adlc }          # or { name: branch-flow, highlight: [issue, pr] }
    title:   { en: "...", he: "..." }
    bullets:                  # keyed, max 5; both languages must have the same keys
      - { key: static-docs, en: "...", he: "..." }
    tip:     { key: start-small, en: "...", he: "..." }   # optional, ≤20 words each
    notes:   { en: "Analogy: ...\n...", he: "Analogy: ...\n..." }  # generator prepends "[m:ss] [@mm:ss]"
    sources: [F6]             # fact-check register IDs → notes must contain a URL
```

**Layouts:** there is a fixed set of 6 to 8: title, section, title-bullets, title-bullets-diagram, two-column compare, table, photo pair, and code card. Each layout is a function that takes `dir` (`ltr` or `rtl`) and `has_tip`. When `has_tip` is true, the content area shrinks to make room for the tip band. The HE deck mirrors the geometry, not only the text alignment.

## 3. Tip box (US-11)

- **Placement:** a fixed band at the bottom of the slide, about 0.7 in tall, defined in `theme.py`.
- **Marker:** a light-bulb icon (`assets/tip-bulb.png`, drawn by `icons.py`) with no label, in both decks. It replaces the earlier "TIP" pill at the human's request on 2026-11-18. The icon and an amber stripe sit on the left in EN and on the right in HE.
- **Text:** the Tip text is RTL in HE, and each Tip is at most 20 whitespace-separated words per language.
- **Testing:** P1a renders every layout both with and without a Tip.

## 4. Validation (any failure fails the build)

1. Both languages have the same slide IDs, in the same order. Every slide has a title in both languages.
2. Bullet keys match between languages, as does the Tip key (or the absence of a Tip). No slide has more than 5 bullets.
3. Timed budgets sum to exactly 45:00, and Q&A is exactly 3:00.
4. The generator computes the notes prefix `[m:ss] [@mm:ss]`, where `@` is the elapsed time at the end of the slide. The last timed slide is `[@45:00]`.
5. Every timed slide's notes contain an `Analogy:` line. Exemptions: Title, Resources and Q&A. Part IV slides may use `Analogy: see slide N` (Ruling R2-5).
6. The deck has at least 10 Tips, at most 1 per slide, each at most 20 words per language.
7. No slash commands or CLI syntax appear in the slide text of Parts I to III.
8. No star counts appear in slide text.
9. Every slide with a `sources:` entry has at least one URL in its notes, in both languages.
10. Every `diagram.name` refers to a builder that exists in `shapes.py`.
11. HE text contains none of the forbidden Hebrew renderings of terms in `glossary_keep_en` (for example "טיפ", "בקשת משיכה", "ענף").

## 5. Theme and RTL

- **Visual baseline:** keep the current deck's dark navy background PNG, colour palette, OK/WARNING photos and code-card look, all extracted into `assets/`. The hand-placed PNG pieces are rebuilt as native shapes. The human has accepted that the result approximates the old look rather than copying it.
- **Fonts (both decks):** Arial, with Courier New for code. These replace Plus Jakarta Sans and JetBrains Mono (2026-11-18), because every PowerPoint machine already has them and the render checks then show the real fonts.
- **Theme details:** an accent bar beside each title, accent-coloured bullets with spacing, a rule under title and section headings, and a footer with the talk name and slide number (not on the title slide).
- **HE font:** Arial, set in both `<a:latin>` and `<a:cs>`. Noto Sans Hebrew is the fallback.
- **HE paragraph settings:**
  - Use `a:pPr rtl="1" algn="r"`, with `lang="he-IL"` on each run.
  - Use bullet dots, not numbered lists.
  - Never put a literal newline inside a run.
  - Recover the old `set_rtl` helper with `git show f85a550:presentation/build_deck.py`.
- **Diagrams in HE:** labels are translated, but process flow stays left to right.
- **English terms in HE (human decision 9):** any word or acronym that Hebrew-speaking developers normally say in English stays in English inside the HE deck. Examples: Tip, Spec Kit, BMAD, GSD, Superpowers, SDD, SDLC, ADLC, AI, agent, prompt, context window, context rot, constitution, spec, plan, tasks, TDD, Git, GitHub, main, dev, branch, issue, PR / pull request, merge, commit, skill, CLI, OLED, DHT22. `deck.yaml` keeps a `glossary_keep_en` list, and validator check 11 fails the build if a Hebrew translation of a listed term appears in HE text. Each embedded English run gets `lang="en-US"` so mixed Hebrew/English lines render the right way round.

## 6. Diagrams (native shapes)

| Diagram | Slide | Phase | Primitives |
|---|---|---|---|
| Four metaphors, two layers | 12 | P1 | 2×2 grid inside a two-band stack (planning/governance vs execution discipline) |
| Decision rule flowchart | 13 | P1 | 3 diamonds: long sessions? / human review each phase? / strong TDD habit? → add GSD / add Superpowers |
| Branch flow | 19–21 | P1 | linear chain: issue #2 → feature branch → PR #3 → dev → PRs #4–7 → main; `highlight` varies per slide |
| SDLC vs ADLC | 3 | P2 | linear chevrons vs circular loop |
| SDD pipeline | 5 | P2 | 5 stages, 2 gate markers, feedback arc, constitution rail |
| Context rot | 7 | P2 | freeform qualitative curve, unlabeled axes |
| /team roles | 23 | P2 (Could) | 3 boxes (architect, PO, dev) with relay arrows through the architect |

## 7. Verification

- `validate.py` exits 0.
- `render_check.sh` produces PNGs of every slide of both decks. Review them for overflow and overlap, with and without the tip band.
- Do one manual pass in PowerPoint on the HE deck, checking the listed lines that mix Hebrew and English.
- Before adding the F7 citation to the notes, fetch its URL and confirm it works.
- Hold a timed rehearsal. If it overruns, apply the relief valves in order: valve 0 (slide 21 drops to 1:30), then the three valves the human approved.

## 8. Phases

| Phase | Scope | Est. |
|---|---|---|
| P1a | extract assets; theme; all layouts in LTR and RTL, with and without a Tip; shapes.py primitives; validator; a placeholder skeleton deck that passes all 10 checks and renders cleanly | ~1 d |
| P1b | EN content in a beginner tone for all 27+6 slides (analogies, at least 10 Tips, GitHub section, What's next); the slide 12, 13 and 19–21 diagrams; DHT22 fixes in the case study | ~1.5–2 d |
| P2 | the remaining diagrams (slides 3, 5, 7, plus the optional /team diagram) | ~0.5–0.75 d |
| P3 | HE content and RTL deck; the PowerPoint bidi pass; README links (US-10) | ~1.5–2 d |

**Total:** about 4.5 to 5.5 working days.

## 9. Decisions and trade-offs

- **A generator instead of hand edits.** The EN and HE decks stay in sync, and timing, tone and facts are checked by machine. The cost is that the hand polish of the current deck is only approximated. The human accepted this.
- **Native diagrams instead of SVG.** They match the dark theme and are translated from the same YAML. The existing SVG pairs in `docs/images` are left untouched.
- **Repo history as an illustration, not a claim.** The GitHub section teaches the ideal team flow, using the real numbers (issue #2 and PRs #3–7). It does not claim that this repo was built by a team, or that the repo enforces CI or branch protection. Issue #2 stays open until the deck ships, because a slide uses it as a teaching example.
- **Safe overwrite of the old deck.** The current EN deck is overwritten at the same path. Before that happens, the tag `pre-theory-deck` is created.
- **`.tmp/` stays out of the repo.** The article is credited and linked, not redistributed.
