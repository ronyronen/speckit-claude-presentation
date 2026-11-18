# Theory-First SDD Talk (EN + HE decks): Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate two synchronized 45-minute beginner decks, `presentation/speckit-workshop.pptx` (EN) and `presentation/speckit-workshop-he.pptx` (HE). Both are built from one YAML content source by a python-pptx generator, and an 11-check validator guards them.

**Architecture:** `presentation/content/deck.yaml` holds every slide in both languages. `presentation/build/` contains a loader/validator, a theme, native diagram builders, layout functions, and a generator that writes each language's deck. A shell script renders both decks to PNG through LibreOffice so they can be checked by eye. The content (copy) is written by the PO; the code is written by the dev.

**Tech Stack:** Python 3.11, python-pptx 1.0.2, PyYAML 6.0.2, pytest 9, LibreOffice `soffice` with `pdftoppm` for render checks.

**Spec:** [docs/superpowers/specs/2026-11-18-theory-deck-design.md](../specs/2026-11-18-theory-deck-design.md) and [docs/superpowers/specs/2026-11-18-theory-deck-brief.md](../specs/2026-11-18-theory-deck-brief.md). Read both. The brief's outline table (27 timed slides + A1–A6) and its US-n acceptance criteria are authoritative.

**Owner tags:** `[dev]` is implemented by a senior-developer subagent. `[po]` content is written by the product-owner subagent. `[architect]` is the main session.

## Global Constraints

- **Total timing:** timed budgets sum to exactly `45:00`. Q&A is exactly `3:00`. Appendix slides have budget `0:00` and their notes start with "backup, not timed".
- **Notes prefix:** generated as `[m:ss] [@mm:ss]`, where `@` is the elapsed time at the **end** of the slide. The last timed slide is `[@45:00]`.
- **Bullets:** at most 5 per slide. Every slide is keyed, and EN and HE carry identical bullet keys.
- **Tips:**
  - At least 10 per deck, at most 1 per slide, and none on Title, Resources or Q&A.
  - Each Tip is at most 20 whitespace-separated words per language.
  - The label is the English word **"TIP" in both decks** (human decision 8; this overrides the "טיפ" wording in the brief's US-11).
  - The marker is a native pill shape, not an emoji.
- **English terms stay English in the HE deck** (human decision 9). The terms are listed in `glossary_keep_en` in deck.yaml. Each embedded English run gets `lang="en-US"`. A Hebrew plain-language gloss may follow a term at its first use.
- **Analogies:** every timed slide's notes contain a line starting `Analogy:`. Title, Resources and Q&A are exempt. Part IV slides (14–18) may use `Analogy: see slide N`.
- **Parts I–III slide text has none of:** slash commands, `$ ` shell syntax, star counts, "21+", or "Lex Christopherson". GSD links point to `github.com/open-gsd/gsd-core`.
- **Fonts:** EN uses Plus Jakarta Sans (body/headings) and JetBrains Mono (code). HE uses Arial in both `<a:latin>` and `<a:cs>`.
- **HE text:** paragraphs use `rtl="1" algn="r"`. Lists use bullet dots, never auto-numbering. A single run never contains a literal `\n`.
- **Slide size and theme:** 16:9 at 12192000×6858000 EMU, with the dark navy background PNG extracted from the current deck.
- **Sensor:** every case-study slide names the **DHT22**. BME280 appears only as "also supported at build time".
- **Untouched:** `docs/images/*.svg`, `docs/textbook.md`, and `.tmp/` (the article PDF must not be committed).
- **Issue #2 stays OPEN** until the decks ship.

## Review Focus

1. **Long Hebrew strings overflow their box** because they are longer than the EN text. Pin it with `test_layouts_fit_long_text`, which builds every layout with a 5×60-character bullet set and a 20-word tip and asserts no text frame sets `auto_size=NONE` with overflow. The overflow guard is `normAutofit`, and the task also runs a render check.
2. **A mixed Hebrew/English run renders in the wrong order** in HE. Pin it with `test_he_runs_tag_english_terms`, which asserts that every run consisting of a `glossary_keep_en` term has `lang="en-US"` and every Hebrew run has `lang="he-IL"`.
3. **Unicode in YAML,** such as Hebrew, emoji, `→` or `≤`. Pin it with `test_loader_roundtrips_unicode`.
4. **A slide with a diagram and a Tip at once** collides with the tip band. Pin it with `test_diagram_area_above_tip_band`.
5. **Budget strings in a bad format,** such as `"2:5"`, `"150"` or `"2.5"`. Pin it with `test_parse_budget_rejects_malformed`, which expects a `ValueError` naming the slide id.

---

### Task 0 [architect]: Safety tag and scaffolding

**Files:**
- Create: `presentation/build/__init__.py` (empty)
- Create: `presentation/build/tests/__init__.py` (empty)
- Create: `presentation/build/requirements.txt` (`python-pptx==1.0.2`, `PyYAML==6.0.2`, `pytest>=8`)

- [ ] **Step 1: Tag the current deck.** Run `git tag pre-theory-deck c27ac68 && git push origin pre-theory-deck`. Expected: the tag exists on the remote.
- [ ] **Step 2: Create the files above and commit** with `chore: scaffold presentation build package`.

---

### Task 1 [dev]: Content loader and validator (US-3, US-4, US-5, US-11; P1a)

**Files:**
- Create: `presentation/build/model.py`
- Create: `presentation/build/validate.py`
- Test: `presentation/build/tests/test_validate.py`
- Test fixtures: `presentation/build/tests/fixtures/valid_min.yaml`, a 3-slide deck that passes all checks once its budget is scaled with `total_budget: "3:00"`. Fixtures may override `meta.total_budget` and `meta.qa_budget`.

**Interfaces:**
- Produces:
  - `model.py`:
    - `@dataclass Bullet(key: str, en: str, he: str)`
    - `@dataclass Tip(key: str, en: str, he: str)`
    - `@dataclass Slide(id: str, part: str, budget_s: int, layout: str, title: dict[str,str], bullets: list[Bullet], tip: Tip|None, notes: dict[str,str], diagram: dict|None, sources: list[str], appendix: bool, extra: dict)`. `extra` carries layout-specific fields such as `columns`, `table` and `images`.
    - `@dataclass Deck(meta: dict, glossary_keep_en: list[str], glossary_forbidden_he: list[str], slides: list[Slide])`
    - `load_deck(path: str|Path) -> Deck`
    - `parse_budget(s: str, slide_id: str) -> int`, which takes `"m:ss"` and returns seconds, raising `ValueError(f"{slide_id}: bad budget {s!r}")`.
    - `fmt_mmss(seconds: int) -> str`
    - `timing_prefixes(deck: Deck) -> dict[str, str]`, which maps a slide id to `"[m:ss] [@mm:ss]"` for timed slides and to `"[backup, not timed]"` for appendix slides.
  - `validate.py`:
    - `validate(deck: Deck, diagram_names: set[str]) -> list[str]`, which returns error strings and an empty list when the deck is valid.
    - The CLI `python -m presentation.build.validate presentation/content/deck.yaml` exits 1 and prints the errors when there are any.

**YAML extras** (beyond the design §2): a top-level `glossary_keep_en: [...]` and `glossary_forbidden_he: ["טיפ", "בקשת משיכה", "ענף", "מאגר", ...]`, plus `appendix: true` on slides A1–A6.

- [ ] **Step 1: Write failing tests.** Write one test per check, each mutating a deep copy of the `valid_min` fixture:
  - `test_valid_fixture_passes`, where `validate(...) == []`.
  - `test_slide_missing_he_title`, where an error contains `"title.he"`.
  - `test_bullet_key_mismatch`.
  - `test_more_than_five_bullets`.
  - `test_tip_key_mismatch`.
  - `test_budget_sum_not_total`, where an error contains `"45:00"` in the real-total variant, using `meta.total_budget`.
  - `test_qa_not_3min`.
  - `test_prefixes_cumulative_end`. With budgets `["0:30","1:00","1:30"]`, the prefixes are `["[0:30] [@0:30]","[1:00] [@1:30]","[1:30] [@3:00]"]`.
  - `test_missing_analogy` (and `test_part_iv_analogy_reference_ok` for `Analogy: see slide 3`).
  - `test_tip_count_below_10` (fixture with `meta.min_tips` override = 1 for the base; the real deck defaults to 10).
  - `test_tip_over_20_words`.
  - `test_tip_on_title_forbidden`.
  - `test_cli_in_theory`. `/speckit-plan` and `$ specify` in a part I bullet each produce an error, while the same text in part IV produces none.
  - `test_star_count_in_text`, with `"300k+ stars"` and `"55,497 stars"`.
  - `test_banned_claims`, with `"21+"` and `"Lex Christopherson"`.
  - `test_sources_need_url`, where `sources: [F6]` with no `http` in notes.en or notes.he is an error.
  - `test_unknown_diagram`.
  - `test_forbidden_hebrew_term`, where `"טיפ"` in any HE field is an error.
  - `test_loader_roundtrips_unicode`.
  - `test_parse_budget_rejects_malformed`, covering `"2:5"`, `"150"`, `"2.5"` and `""`.
- [ ] **Step 2: Run the tests and confirm they fail.** Run `python3 -m pytest presentation/build/tests/test_validate.py -q`. Expected: FAIL with an ImportError.
- [ ] **Step 3: Implement `model.py` and `validate.py`.** Make the checks match design §4 items 1–11 and the Global Constraints. The CLI regex is `(^|\s)/[a-z]+-[a-z]+|\$ \w`. The star regex is `\d[\d,.]*k?\+?\s*stars`. Parts are `0, I, II, III, IV, V, VI, close` and `"theory" = {0, I, II, III}`. Exempt slides are found by id: `title`, `resources`, `qa`.
- [ ] **Step 4: Run the tests and confirm they pass.** Same command. Expected: all pass.
- [ ] **Step 5: Commit** with `feat(deck): YAML content model and 11-check validator`.

---

### Task 2 [dev]: Theme, assets and RTL text helpers (US-4; P1a)

**Files:**
- Create: `presentation/build/theme.py`
- Create: `presentation/build/text.py`
- Create: `presentation/assets/` (extracted files)
- Create: `presentation/build/extract_assets.py`, a one-off script that is committed for reproducibility.
- Test: `presentation/build/tests/test_text.py`

**Interfaces:**
- Produces:
  - `theme.py` constants:
    - `SLIDE_W=12192000`, `SLIDE_H=6858000`
    - `TIP_BAND_H=Inches(0.7)`, `MARGIN=Inches(0.5)`
    - `COLORS: dict[str, RGBColor]`, keys `bg, surface, text, muted, accent, accent2, ok, warn, tip`, with values sampled from the current deck XML.
    - `FONTS = {"en": {"body": "Plus Jakarta Sans", "head": "Plus Jakarta Sans ExtraBold", "mono": "JetBrains Mono"}, "he": {"body": "Arial", "head": "Arial", "mono": "JetBrains Mono"}}`
    - `ASSETS = Path("presentation/assets")`
    - `content_box(has_tip: bool) -> tuple[int,int,int,int]` (left, top, width, height in EMU)
    - `tip_box() -> tuple[int,int,int,int]`
  - `text.py`:
    - `write_paragraphs(tf, items: list[str], lang: str, size_pt: int, glossary: list[str], bullet: bool=True, color=None, bold=False) -> None`
    - `split_runs(text: str, glossary: list[str]) -> list[tuple[str, str]]`, which returns `(segment, "en"|"he")` pairs, with Latin-script segments and glossary terms tagged `"en"`.
    - `set_rtl(paragraph) -> None`
- Consumes: nothing from Task 1.

- [ ] **Step 1: Extract assets.** `extract_assets.py` unzips `git show pre-theory-deck:presentation/speckit-workshop.pptx` and copies the following into `presentation/assets/`:
  - the background PNG used by slide 1 → `bg.png`;
  - the OK and WARNING photos → `photo-ok.jpg`, `photo-warning.jpg` (or copy from `docs/images/hardware-dht22-*.jpg` if those are the same images);
  - the code-card PNG from slide 22 → `code-card.png`.

  Print the sampled hex colours so they can be pasted into `COLORS`. Run it and commit the assets.
- [ ] **Step 2: Write failing tests.**
  - `test_split_runs_mixed`. `split_runs("השתמשו ב-Spec Kit עם Claude", ["Spec Kit"])` returns segments with `"Spec Kit"`→`"en"` and the Hebrew parts→`"he"`.
  - `test_he_paragraph_rtl`. After `write_paragraphs(tf, ["שלום"], "he", 20, [])`, the paragraph XML contains `rtl="1"` and `algn="r"`, and the run contains `lang="he-IL"` and `<a:cs typeface="Arial"`.
  - `test_he_runs_tag_english_terms`. An English segment run has `lang="en-US"`.
  - `test_no_newline_in_run`. A string containing `\n` is split into separate paragraphs.
  - `test_en_paragraph_ltr`. There is no `rtl="1"`, and the font is Plus Jakarta Sans.
  - `test_bullets_not_numbered`. `buChar` is present and `buAutoNum` is absent.
- [ ] **Step 3: Run the tests and confirm they fail.** Run `python3 -m pytest presentation/build/tests/test_text.py -q`.
- [ ] **Step 4: Implement `theme.py` and `text.py`.** Adapt `set_rtl` from `git show f85a550:presentation/build_deck.py`.
- [ ] **Step 5: Run the tests and confirm they pass.**
- [ ] **Step 6: Commit** with `feat(deck): dark theme constants, assets, RTL-aware text writer`.

---

### Task 3 [dev]: Native diagram builders (US-6, US-7, US-12; the P1 diagrams)

**Files:**
- Create: `presentation/build/shapes.py`
- Test: `presentation/build/tests/test_shapes.py`

**Interfaces:**
- Consumes: `theme.COLORS`, `theme.FONTS`, `text.write_paragraphs`.
- Produces:
  - `DIAGRAMS: dict[str, Callable[[Slide_pptx, tuple[int,int,int,int], dict, str, list[str]], None]]`. Each builder takes a pptx slide, an area box, the YAML `diagram` dict (whose labels live under `diagram["labels"][key][lang]`), `lang` and the glossary.
  - `pill(slide, x, y, text, lang) -> Shape` (also used by the Tip box).
  - P1 keys: `"layers"` (slide 12), `"decision"` (slide 13), `"branch-flow"` (slides 19–21; it reads `diagram["highlight"]: list[str]` from `issue, feature, pr3, dev, prs, main`).
  - P2 keys are added in Task 7.
- [ ] **Step 1: Write failing tests.** Each test builds a blank `Presentation()`, adds a slide and calls the builder.
  - `test_layers_shape_budget`. At most 4 boxes plus 2 band labels, and every text run is 24pt or larger (US-6).
  - `test_decision_has_three_questions`. There are exactly 3 diamond shapes (`MSO_SHAPE.DIAMOND`).
  - `test_branch_flow_nodes_and_highlight`. There are 6 nodes labelled from YAML. With `highlight=["dev","main"]`, exactly those two nodes are filled with `COLORS["accent"]` and the others with `COLORS["surface"]`.
  - `test_branch_flow_ltr_in_he`. For `lang="he"`, the node x-order is still issue→main from left to right.
  - `test_diagram_area_respected`. Every shape lies inside the given area box.
- [ ] **Step 2: Run the tests and confirm they fail.**
- [ ] **Step 3: Implement the builders.** Use rounded rectangles, connector arrows and diamonds only, with no images.
- [ ] **Step 4: Run the tests and confirm they pass.**
- [ ] **Step 5: Commit** with `feat(deck): native layer, decision and branch-flow diagrams`.

---

### Task 4 [dev]: Layouts, generator, render check and skeleton deck (US-3, US-4, US-8, US-11; closes P1a)

**Files:**
- Create: `presentation/build/layouts.py`
- Create: `presentation/build/build_decks.py`
- Create: `presentation/build/render_check.sh`
- Create: `presentation/content/deck.yaml`. This is the **skeleton**: all 27 timed and 6 appendix slide ids, parts, budgets, layouts and diagram refs exactly as in the brief's outline table, with placeholder EN/HE text of realistic length.
- Test: `presentation/build/tests/test_build.py`

**Interfaces:**
- Consumes: `load_deck`, `validate`, `timing_prefixes` (Task 1); `theme`, `text` (Task 2); `DIAGRAMS`, `pill` (Task 3).
- Produces:
  - `layouts.LAYOUTS: dict[str, Callable[[pptx_slide, Slide, str, list[str]], None]]`, with keys `title`, `section`, `bullets`, `bullets-diagram`, `compare`, `table`, `photos`, `code`. Each one draws the background, the title, its content inside `content_box(has_tip)` (mirrored horizontally when `lang=="he"`), and a Tip band through `add_tip(slide, tip_text, lang)`. The Tip band is a pill labelled `"TIP"` plus the tip text; the pill is left in EN and right in HE.
  - `build_decks.build(deck_path: str, lang: str, out_path: str) -> None`. It runs `validate` first and raises `SystemExit` on any errors. Notes are `prefix + "\n" + notes[lang]`.
  - The CLI `python -m presentation.build.build_decks --lang en|he|both`. Defaults: EN → `presentation/speckit-workshop.pptx`, HE → `presentation/speckit-workshop-he.pptx`.
  - `render_check.sh <pptx> <outdir>` renders through `soffice -env:UserInstallation=file://$TMPDIR/lo --headless --convert-to pdf` and then `pdftoppm -r 60 -png`, and prints the PNG count.
- [ ] **Step 1: Write failing tests.**
  - `test_skeleton_validates`. `validate(load_deck("presentation/content/deck.yaml"), set(DIAGRAMS))` returns `[]`.
  - `test_build_both_langs`. Build into `tmp_path`. Each deck has 33 slides, matching ids by order.
  - `test_notes_prefix_and_end`. Slide 27's notes start with `"[3:00] [@45:00]"`, and slide 28's notes start with `"[backup, not timed]"`.
  - `test_tip_pill_label_english_in_he`. The HE deck has a pill with the text exactly `"TIP"`, and no `"טיפ"` anywhere in it.
  - `test_tip_band_mirrored`. The pill's left is less than slide width / 2 in EN and greater in HE.
  - `test_diagram_area_above_tip_band`. On every slide that has both a diagram and a tip, max(shape.bottom) of the diagram is at most the tip band's top.
  - `test_layouts_fit_long_text`. Covers every layout, using the long-text input from Review Focus 1.
  - `test_he_text_is_rtl`. Every non-code text paragraph in the HE deck has `rtl="1"`.
- [ ] **Step 2: Run the tests and confirm they fail.**
- [ ] **Step 3: Implement** `layouts.py`, `build_decks.py`, `render_check.sh` and the skeleton `deck.yaml`.
- [ ] **Step 4: Run the tests and confirm they pass.** Run `python3 -m pytest presentation/build/tests -q`. Expected: all pass.
- [ ] **Step 5: Run the render check.** Run `python3 -m presentation.build.build_decks --lang both` and `bash presentation/build/render_check.sh` on each deck into the scratchpad. Expected: 33 PNGs per deck. Look at every layout × {tip, no tip} × {EN, HE} and fix any overlap.
- [ ] **Step 6: Commit** the code, `deck.yaml` and both skeleton decks with `feat(deck): layouts, generator, render check, skeleton deck`. Report the PNG folder path to the architect for review.

---

### Task 5 [po]: EN content, beginner tone (US-1, US-2, US-5, US-6, US-11, US-12, US-13, US-8; P1b)

**Files:**
- Modify: `presentation/content/deck.yaml`. Change only the `en` values, `notes.en`, `tip`, `sources`, `diagram.labels.*.en`, `glossary_keep_en` and `glossary_forbidden_he`. Do not change ids, budgets or layouts.

**Content rules** (from the brief):
- Intuition comes first and the formal term second.
- Spell out each acronym at its first use.
- At most 5 bullets per slide.
- Include at least 10 Tips. Each starts with a verb and is 20 words or fewer.
- Write an `Analogy:` line in every timed slide's notes.
- Put the sources URLs in the notes for F1–F15 rows that are used.
- The F7 context-rot citation must be a URL you actually fetched. Otherwise the slide wording is "widely observed by practitioners".
- In the GitHub section, use issue #2, `001-heltec-monitor-dht22-sensor`, PR #3 → `dev`, and PRs #1/#4–#7 → `main`. Present it as an illustration of the ideal team flow. Do not claim a team, CI or branch protection.
- Slide 23 tells the /team story of this very brief.
- Take case-study facts from `specs/001-heltec-monitor/`, `firmware/README.md` and `docs/textbook.md`, and use the DHT22.

- [ ] **Step 1: Write the content** for all 33 slides in `en`. Leave the `he` values as the placeholders.
- [ ] **Step 2: The architect runs** `python -m presentation.build.validate presentation/content/deck.yaml`. Expected: exit 0 except for HE-only placeholder issues, if any. The PO fixes reported errors.
- [ ] **Step 3: The architect commits** with `content(deck): EN beginner-tone content`.

---

### Task 6 [dev]: Build the EN deck and fix overflow (US-1, US-2, US-3; closes P1)

**Files:**
- Modify: `presentation/build/layouts.py` (only to fix fit problems)
- Modify: `presentation/speckit-workshop.pptx` (generated)

- [ ] **Step 1: Build EN and render.** Expected: 33 PNGs.
- [ ] **Step 2: Inspect every PNG** for overflow, overlap and unreadable text, and fix the layouts. Never shorten copy yourself; report copy that is too long to the architect, who routes it to the PO.
- [ ] **Step 3: Run the full test suite.** Expected: all pass.
- [ ] **Step 4: Commit** with `build(deck): EN deck generated from content source`.

---

### Task 7 [dev]: P2 diagrams (US-7)

**Files:**
- Modify: `presentation/build/shapes.py` (add `"sdlc-adlc"`, `"sdd-pipeline"`, `"context-rot"`, and the optional `"team-roles"`)
- Modify: `presentation/content/deck.yaml` (diagram refs on slides 3, 5, 7 and 23, plus EN labels; HE labels are filled in Task 8)
- Test: `presentation/build/tests/test_shapes.py`

- [ ] **Step 1: Write failing tests.**
  - `test_sdlc_adlc_has_linear_and_loop`. One chevron chain plus one circular arrow group.
  - `test_sdd_pipeline_five_stages_two_gates_rail`. 5 stage boxes, 2 gate markers, 1 rail box spanning at least 90% of the area width, and 1 feedback connector.
  - `test_context_rot_no_numbers`. No run contains digits.
  - `test_team_roles_relay_via_architect`. 3 boxes. Every connector touches the architect box.
- [ ] **Step 2: Run the tests and confirm they fail.**
- [ ] **Step 3: Implement the builders.** Then rebuild EN, render-check slides 3, 5, 7 and 23, and confirm the full test suite passes.
- [ ] **Step 4: Commit** with `feat(deck): SDLC/ADLC, SDD pipeline, context-rot, team-roles diagrams`.

---

### Task 8 [po]: HE content (US-4)

**Files:**
- Modify: `presentation/content/deck.yaml` (only the `he` values, `notes.he` and the diagram `he` labels)

**Rules:**
- Translate meaning, not word by word.
- Every term in `glossary_keep_en`, and any word Hebrew-speaking developers normally say in English, stays in **English**: TIP, Spec Kit, PR, branch, merge, issue, prompt, agent, context window, spec, skill, constitution, TDD, and so on.
- A Hebrew plain-language gloss may follow at first use.
- Each Tip stays at 20 words or fewer.
- `Analogy:` stays as the literal English prefix.

- [ ] **Step 1: Write all `he` content.**
- [ ] **Step 2: The architect runs the validator.** Expected: exit 0 with 0 errors.
- [ ] **Step 3: The architect commits** with `content(deck): Hebrew content`.

---

### Task 9 [dev]: Build the HE deck and run the RTL render pass (US-4)

**Files:**
- Modify: `presentation/speckit-workshop-he.pptx` (generated)
- Modify: `presentation/build/layouts.py` (only to fix fit problems)
- Create: `presentation/build/he_manual_check.md`. This lists every slide's mixed Hebrew/English lines and all Tips, for the human's PowerPoint pass.

- [ ] **Step 1: Build `--lang both` and render the HE deck.** Expected: 33 PNGs. Inspect them for mirrored layout, right alignment and overflow.
- [ ] **Step 2: Generate `he_manual_check.md`** with a small script function `list_mixed_lines(deck) -> list[tuple[slide_id, text]]` in `build_decks.py`. A line counts as mixed if it has both Hebrew and Latin characters. Add the test `test_list_mixed_lines`.
- [ ] **Step 3: Run the full test suite.** Expected: all pass.
- [ ] **Step 4: Commit** with `build(deck): Hebrew RTL deck and manual bidi checklist`.

---

### Task 10 [po]: README links and acceptance report (US-10, all US)

**Files:**
- Modify: `README.md`. Replace the single deck link with links to the EN and HE decks, add one line on rebuilding (`python -m presentation.build.build_decks --lang both`), and credit the article.
- Create: `docs/superpowers/specs/2026-11-18-theory-deck-acceptance.md`

- [ ] **Step 1: Update the README.**
- [ ] **Step 2: Write the acceptance report.** Mark each AC in US-1…US-13 ✅, ❌ or ⚠️, citing evidence: the validator output, test output and PNG paths that the architect supplies.
- [ ] **Step 3: The architect commits** with `docs: link EN/HE decks; acceptance report`.

---

### Task 11 [architect]: Final review and handoff

- [ ] **Step 1: Run the whole-branch code review** following subagent-driven-development, then superpowers:verification-before-completion. This means a fresh validator run, `pytest`, and a build of both decks, all in this step.
- [ ] **Step 2: Report to the human** what needs them:
  - the PowerPoint bidi pass, using `he_manual_check.md`;
  - installing Plus Jakarta Sans on the presenting machine;
  - a timed rehearsal, with the relief valves listed in the brief;
  - closing issue #2 after the talk.
- [ ] **Step 3:** Push `dev`, then open a PR from `dev` to `main` **only after the human confirms.**
