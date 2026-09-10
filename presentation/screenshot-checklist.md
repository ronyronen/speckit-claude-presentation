# Screenshot & Photo Checklist

Exact captures needed, in presentation order. Save each as
`docs/images/screenshot-NN-<slug>.png` (numbering matches this list) so
`slide-links.md` and the outline can reference them by a stable name.
Nothing on this list has been fabricated or simulated — capture each one
for real before it goes in the deck.

**Status note (2026-09-10)**: `presentation/speckit-workshop-draft.pptx`
already exists as a reviewable draft. For items marked **covered by
generated card below**, the draft does *not* show a placeholder — it
shows a real, non-fabricated substitute (actual terminal output run
during this project, or actual file content), rendered as a clean
image via `presentation/assets/make_content_cards.py` and
`presentation/assets/svg_to_pptx_png.py`. These are good enough for
review and for the live talk if you don't get to the real screen
captures in time; swap in genuine screenshots later purely for visual
polish, not for correctness. Items with no such substitute show an
explicit "📷 missing" placeholder in the draft — those are the ones that
still block a fully "real" deck.

## 8–12 min: What Spec Kit is (slides 8–9)

- [ ] **01-speckit-website** — `https://github.github.io/spec-kit/` landing page — **placeholder in draft (slide 8), no substitute possible**
- [ ] **02-speckit-repo** — `https://github.com/github/spec-kit` (stars/activity visible) — **placeholder in draft (slide 8), no substitute possible**
- [x] **03-install-terminal** / **04-init-terminal** — *covered by generated card* `terminal-specify-init.png` (slide 9): real output from this repo's own `specify init --here --force --integration claude` run. Optional upgrade: a fresh screen recording of the same command for visual variety.

## 12–16 min: Claude Code / Codex / IDE (slides 12–14)

- [ ] **05-vscode-project** — this repo open in VS Code, `specs/001-heltec-monitor/` expanded in the sidebar — **placeholder in draft (not yet added as its own slide visual)**
- [ ] **06-claude-code-session** — a Claude Code session in this repo running `/speckit-specify` or `/speckit-analyze` — **placeholder in draft (slide 13)**
- [ ] **07-codex-session** — a Codex session in this repo running `$speckit-specify` — **placeholder in draft (slide 13)**

## 21–31 min: Heltec walkthrough (slides 18–23)

- [x] **08-spec-md** — *covered by generated card* `code-spec-clarifications.png` (slide 19): real content of `spec.md`'s Clarifications section. Optional upgrade: an actual VS Code Markdown-preview screenshot for visual variety.
- [x] **09-clarify-interaction** — covered by the same card (slide 19): the real Q&A text.
- [ ] **10-plan-md** — `specs/001-heltec-monitor/plan.md`, Constitution Check table visible — **not yet in draft; add if time allows**
- [ ] **11-tasks-md** — `specs/001-heltec-monitor/tasks.md`, checked-off boxes visible — **not yet in draft; add if time allows**
- [x] **12-analyze-diff** — *covered by generated card* `code-analyze-diff.png` (slide 22b): the actual `git show` diff output, verified reproducible via:
      ```bash
      git show $(git log 07-analysis-complete..08-implemented --oneline -- \
        specs/001-heltec-monitor/spec.md | tail -1 | cut -d' ' -f1) \
        -- specs/001-heltec-monitor/spec.md
      ```
      Optional upgrade: a real terminal screenshot of this exact command for visual variety — the content would be identical.
- [x] **13-monitor-logic-cpp** — *covered by generated card* `code-monitor-logic.png` (slide 23): real file content.
- [x] **14-platformio-build** — *covered by generated card* `terminal-pio-build.png` (slide 23, referenced) + `terminal-pio-test.png`: real output from this session's `pio run`/`pio test`.

## 31–34 min: Physical hardware demo (slide 24) — after your hardware session

- [ ] **15-serial-ok** — `pio device monitor` showing normal `OK` lines at room temperature
- [ ] **16-serial-warning** — same, showing a `WARNING` line after warming the sensor above 30.0°C
- [ ] **17-serial-sensor-error** — same, showing `SENSOR_ERROR` after disconnecting the sensor (if practical)
- [ ] **18-oled-ok** — photo of the physical OLED showing a temperature + "OK"
- [ ] **19-oled-warning** — photo of the physical OLED showing "WARNING"
- [ ] **20-oled-sensor-error** — photo of the physical OLED showing "SENSOR ERROR" + stale reading (if practical)

None of these can be substituted — they require the physical board.
Slide 24 in the draft shows an explicit pending banner and a "📷
missing" placeholder instead of fabricated data.

## 21–31 or 34–35 min: Git history (slide 25)

- [x] **21-git-log** — *covered by generated card* `terminal-git-log.png`: real, current output (8 tags; `09-hardware-verified` explicitly noted as not yet created — not simulated as if it existed). Re-generate via `python3 presentation/assets/make_content_cards.py` once `09-hardware-verified` is actually tagged.

---

**Still genuinely open after this pass**: 01, 02 (real screenshots, no
substitute exists), 05, 06, 07 (need a live VS Code / Claude Code /
Codex session), 10, 11 (nice-to-have, not yet added to the draft), and
15–20 (need the physical board). Everything else in the draft is real
content, not a mockup.
