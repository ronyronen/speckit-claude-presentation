# Screenshot & Photo Checklist

Exact captures needed, in presentation order. Save each as
`docs/images/screenshot-NN-<slug>.png` (numbering matches this list) so
`slide-links.md` and the outline can reference them by a stable name.
Nothing on this list has been fabricated or simulated — capture each one
for real before it goes in the deck.

## 8–12 min: What Spec Kit is (slides 8–9)

- [ ] **01-speckit-website** — `https://github.github.io/spec-kit/` landing page
- [ ] **02-speckit-repo** — `https://github.com/github/spec-kit` (stars/activity visible)
- [ ] **03-install-terminal** — terminal running `uv tool install specify-cli`
- [ ] **04-init-terminal** — terminal running `specify init --here --integration claude` (re-run in a scratch directory, or use this repo's own recorded output in `docs/textbook.md` Chapter 5 if a live re-run isn't convenient)

## 12–16 min: Claude Code / Codex / IDE (slides 12–14)

- [ ] **05-vscode-project** — this repo open in VS Code, `specs/001-heltec-monitor/` expanded in the sidebar
- [ ] **06-claude-code-session** — a Claude Code session in this repo running `/speckit-specify` or `/speckit-analyze`
- [ ] **07-codex-session** — a Codex session in this repo running `$speckit-specify`

## 21–31 min: Heltec walkthrough (slides 18–23)

- [ ] **08-spec-md** — `specs/001-heltec-monitor/spec.md` in VS Code's Markdown preview
- [ ] **09-clarify-interaction** — the `/speckit-clarify` Q&A (or a screenshot of this project's actual clarification session)
- [ ] **10-plan-md** — `specs/001-heltec-monitor/plan.md`, Constitution Check table visible
- [ ] **11-tasks-md** — `specs/001-heltec-monitor/tasks.md`, checked-off boxes visible
- [ ] **12-analyze-diff** — the real fix, not a screenshot of prose. Run:
      ```bash
      git show $(git log 07-analysis-complete..08-implemented --oneline -- \
        specs/001-heltec-monitor/spec.md | tail -1 | cut -d' ' -f1) \
        -- specs/001-heltec-monitor/spec.md
      ```
      and screenshot the diff (SC-004/SC-002 before → after). This is
      slide 22 — the most important screenshot in the deck.
- [ ] **13-monitor-logic-cpp** — `firmware/src/monitor_logic.cpp` in the editor
- [ ] **14-platformio-build** — terminal output of `pio run -e heltec_wifi_kit_32_V3` (SUCCESS + memory table)

## 31–34 min: Physical hardware demo (slide 24) — after your hardware session

- [ ] **15-serial-ok** — `pio device monitor` showing normal `OK` lines at room temperature
- [ ] **16-serial-warning** — same, showing a `WARNING` line after warming the sensor above 30.0°C
- [ ] **17-serial-sensor-error** — same, showing `SENSOR_ERROR` after disconnecting the sensor (if practical)
- [ ] **18-oled-ok** — photo of the physical OLED showing a temperature + "OK"
- [ ] **19-oled-warning** — photo of the physical OLED showing "WARNING"
- [ ] **20-oled-sensor-error** — photo of the physical OLED showing "SENSOR ERROR" + stale reading (if practical)

## 21–31 or 34–35 min: Git history (slide 25)

- [ ] **21-git-log** — terminal output of `git log --oneline --all --decorate` showing all 9 checkpoint tags (only 8 will show until `09-hardware-verified` is tagged — capture this one *after* that tag exists)

---

Once `09-hardware-verified` is tagged (after your hardware session),
items 15–21 become capturable together in one sitting. Everything above
that — 01 through 14 — has no hardware dependency and can be captured
any time.
