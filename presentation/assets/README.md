# Presentation assets

## Diagrams (ready to use)

The diagrams for the slide deck live in
[`../../docs/images/`](../../docs/images/) (shared with the textbook, so
there's one source of truth instead of duplicated copies):

| File | Use it for |
|---|---|
| `diagram-prompt-vs-spec.svg` | 0–8 min: the core comparison |
| `diagram-speckit-workflow.svg` | 8–12 min: what Spec Kit is |
| `diagram-tool-relationship.svg` | 12–16 min: Spec Kit / agent / IDE |
| `diagram-architecture.svg` | 21–31 min: Heltec walkthrough, Stage D |
| `diagram-hysteresis.svg` | 21–31 min: the hysteresis teaching moment |

All are plain SVG with Hebrew labels — drag-and-drop into Google Slides
directly (Insert → Image), or open in any vector editor to restyle to
match your deck's theme.

## Screenshots (need to be captured by hand)

These were **not** generated — they need a real browser/editor/terminal
session and, for the last two, the physical board. Capturing them is a
straightforward final step before assembling the deck; each row says
exactly what to show and why.

| # | Screenshot | What to show | Where it's used |
|---|---|---|---|
| 1 | Spec Kit website | github.github.io/spec-kit landing page | 8–12 min |
| 2 | Spec Kit GitHub repo | github.com/github/spec-kit, stars/activity visible | 8–12 min |
| 3 | Installation | Terminal running `uv tool install specify-cli` | 8–12 min |
| 4 | Repo initialization | Terminal output of `specify init --here --integration claude` (this repo's own run) | 8–12 min |
| 5 | VS Code project view | This repo open, `specs/001-heltec-monitor/` expanded in the sidebar | 12–16 min |
| 6 | Claude Code in this repo | A session showing `/speckit-specify` or `/speckit-analyze` running | 12–16 min |
| 7 | Codex in this repo | A session showing `$speckit-specify` running | 12–16 min |
| 8 | `spec.md` | `specs/001-heltec-monitor/spec.md` rendered in VS Code's Markdown preview | 21–31 min |
| 9 | Clarify interaction | The `/speckit-clarify` Q&A (or this project's `AskUserQuestion` equivalent) | 21–31 min |
| 10 | `plan.md` | `specs/001-heltec-monitor/plan.md`, Constitution Check table visible | 21–31 min |
| 11 | `tasks.md` | `specs/001-heltec-monitor/tasks.md`, checked-off boxes visible | 21–31 min |
| 12 | Analyze output | This repo's `analysis-report.md`, the SC-004/FR-005 finding row | 21–31 min |
| 13 | Implementation | `firmware/src/monitor_logic.cpp` in the editor | 21–31 min |
| 14 | PlatformIO build | Terminal output of `pio run -e heltec_wifi_kit_32_V3` (SUCCESS + memory table) | 21–31 min |
| 15 | Serial output | `pio device monitor` showing `OK`/`WARNING`/`SENSOR_ERROR` lines | 31–34 min (live demo) |
| 16 | Heltec OLED | A photo of the physical board's screen showing a reading | 31–34 min (live demo) |
| 17 | Git history | `git log --oneline --all --decorate` showing all 9 checkpoint tags | 21–31 min or 34–35 min |

Save captured screenshots into this folder (or `docs/images/`) using the
same numbering as this table, so slide-links.md's references stay valid.
