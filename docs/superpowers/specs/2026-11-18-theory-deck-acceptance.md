# Acceptance Report: Theory-First SDD Talk (EN + HE decks)

**Date:** 2026-11-18 | **Reviewer:** Product Owner | **Brief:** `docs/superpowers/specs/2026-11-18-theory-deck-brief.md` (round 2)
**Build under review:** 54e74fd (committed; includes the Task 10 changes: slide 23 HE label, README), plus the final-review fix wave committed on top of it.

## Evidence used
- **E1 Validator:** `python3 -m presentation.build.validate presentation/content/deck.yaml` returned rc=0 with all checks passing: 10 validator checks plus the generator-enforced timing prefix (spec check 4, asserted in `test_build.py`) (reported by the architect).
- **E2 Tests:** 143 pytest tests pass (reported by the architect).
- **E3 Content source:** I read `presentation/content/deck.yaml` directly for ids, budgets, bullets, tips and notes.
- **E4 Renders:** EN in `…/scratchpad/render/final-en/`, HE in `…/scratchpad/render/t9-he/`; 33 PNGs each. The scratchpad render paths are not durable (a reboot or cleanup can clear them); regenerate renders with `bash presentation/build/render_check.sh <pptx> <outdir>`. I viewed EN slides 9, 13, 20 and 25, and HE slides 12, 14 and 18.
- **E5 Bidi checklist:** `presentation/build/he_manual_check.md`, generated. Every box is still unchecked.
- **E6 Fact-check register:** in the brief, plus the developer's `gh api` checks and the two context-rot sources I fetched (Chroma, arXiv 2307.03172).
- **E7 Content reviews:** the independent EN review (C1–C3, I1–I6, minors), all applied; the timing pass; the HE translation pass.

Legend: ✅ met · ❌ not met · ⚠️ met with caveats, or waiting on a human action.

## Cross-cutting standards
| Criterion | Status | Evidence |
|---|---|---|
| Intuition before the formal term on concept slides | ✅ | E3: every timed concept slide has an `Analogy:` line and introduces the plain-language idea first (desk → context window, whiteboard → context rot, etc.) |
| Acronyms spelled out at first appearance | ⚠️ | SDD and AI on slide 1, SDLC on slide 3, TDD on slide 11 and PR on slide 20 are all spelled out on the slide. ADLC appears on the slide only as "(the article's term)"; its expansion is in the notes only. BMAD and GSD are expanded in the notes only. "PR #3" appears in the slide 19 diagram one slide before "PR" is spelled out; the slide 19 notes name it. |
| At most 5 bullets per content slide | ✅ | E1, check 2 |
| Visual baseline: dark navy background, palette, photos; consistent Tip box | ✅ | E4: every viewed slide uses the dark navy theme. The photos appear on slide 18 in both decks. The TIP band is identical across slides. |
| Validator items 1–6 | ✅ | E1 |

## US-1 (Must): theory arc of about 24 minutes
| Criterion | Status | Evidence |
|---|---|---|
| Slides 1–13 budgets sum to 23–25 min | ✅ | E3: 0:30+1+2:30+2:30+2:30+2+2+1:30+2+1:30+1:30+2+2:30 = 24:00 |
| Order: intent gap → vibe vs SDD → core → context eng. → context rot → frameworks → layers → decision rule | ✅ | E3: slide order and ids |
| An analogy on the slide or in the notes for each theory slide | ✅ | E1, check 5; E3 |
| Stage names allowed; no slash commands, CLI syntax or firmware detail in parts 0–III | ✅ | E1, check 7; E4 slide 9 shows stage names only |

## US-2 (Must): case study of about 8 minutes
| Criterion | Status | Evidence |
|---|---|---|
| Slides 14–18 sum to 7:30–8:30 | ✅ | E3: 1:30×4 + 2:00 = 8:00 |
| Covers board and requirement (implicit vs explicit), hysteresis, plan + 11/11 merged, analyze finding, photos at 2:00 with no live run | ✅ | E3 slides 14–18; E4 HE slide 18 shows both photos |
| DHT22 named everywhere; BME280 only as "also supported at build time" | ✅ | E3: BME280 appears only in the slide 14 notes, worded as a build-time option. E7: reviewer C-items. |
| "Which layers were used" is one line on Takeaways, not a separate slide | ✅ | E4 EN slide 25: "Heltec run: Spec Kit plus human review was enough" |

## US-3 (Must): timed speaker notes
| Criterion | Status | Evidence |
|---|---|---|
| Written notes on every slide in both decks; stubs replaced | ✅ | E3: all 33 slides have `notes.en` and `notes.he` |
| Every note starts with `[m:ss] [@mm:ss]`; Q&A ends at `[@45:00]` | ✅ | E1, checks 3–4 (the generator writes the prefix) |
| Budgets sum to exactly 45:00 | ✅ | E1, check 3 |
| The notes are realistic to speak in the budget | ⚠️ | The scripts were sized at about 130 words/min, with every slide at or under 1.15× after the timing pass (E7). Behavior-photos is still roughly 1.15×. **Needs one timed rehearsal per language by the human.** |

## US-4 (Must): Hebrew deck identical in content
| Criterion | Status | Evidence |
|---|---|---|
| EN stays at `presentation/speckit-workshop.pptx`; HE is a separate file | ✅ | `presentation/speckit-workshop-he.pptx` exists |
| Same slide count, order, bullet keys and counts in EN and HE | ✅ | E1, checks 1–2; both decks render 33 slides (E4) |
| HE right-to-left and right-aligned, in a Hebrew-capable font; English terms kept, with a gloss at first use | ✅ | E4 HE slides 12, 14 and 18 are right-aligned and RTL in a sans font with Hebrew glyphs. E3: glosses for SDLC, constitution, TDD, FR and AI. E1, check 11 (forbidden Hebrew renderings) passes. |
| Mixed lines, all Tips included, pass a manual PowerPoint review | ⚠️ | E5: none of the boxes are checked yet. **Needs the human's PowerPoint pass.** The LibreOffice renders show two likely problem spots:<br>• HE slide 14, "חזרה ל-OK מתחת ל-25 °C": the line wraps between "ל-" and "25 °C".<br>• HE slide 18, captions "OK ב-24.0 °C" and "WARNING ב-26.6 °C…": the number and °C sit in an unexpected visual order. |
| Every diagram and Tip box appears in both decks, localized | ✅ | E3: every diagram label has an `he` value; E4 HE slides 12 and 18 |

## US-5 (Must): accurate claims
| Criterion | Status | Evidence |
|---|---|---|
| Fact-check register F1–F15 resolved as stated | ✅ | E6, row by row:<br>• F1: no number; generic role list.<br>• F2: no star counts on slides (E1 check 8); dated count in notes only.<br>• F3: the README's 7-step workflow, deleted code, and two-stage review.<br>• F4: links go to gsd-core.<br>• F5: Jesse Vincent named; no GSD creator on slides.<br>• F6: slide says "fresh context per task"; 200k is in the notes, cited to the README.<br>• F7: both URLs fetched and cited.<br>• F8 and F9: attributed to the article.<br>• F10: five stages plus two gates.<br>• F11: chain corrected to issue #2 → PR #3 → dev → PR #4 → main.<br>• F12: one-person project disclosed.<br>• F13: no claims of CI or branch protection.<br>• F14: /team presented as a custom local setup.<br>• F15: shared constitution presented as a practice. |
| No star counts, "21+ roles" or "Lex Christopherson" on slides; GSD → gsd-core; article opinions attributed; article credited | ✅ | E1, check 8 and banned-claims check; E3 slides 1 and 26 |
| Repo claims are verified before they go on a slide | ⚠️ | The slide 21 notes and README say every stage is "tagged in Git and on GitHub, 01-start to 09-hardware-verified". **The tags are not pushed to GitHub yet** (waiting on a GitHub account switch). The claim is true only after the human pushes them. |

## US-6 (Must): layer model and decision rule
| Criterion | Status | Evidence |
|---|---|---|
| Slide 12: four metaphors, two layers, ≤4 boxes + 2 labels, ≥24pt | ✅ | E4 HE slide 12: 4 boxes and 2 band labels. The layers diagram is drawn at 24pt (generator source). |
| Slide 13: 2–3 plain questions, each outcome naming its layer | ✅ | E4 EN slide 13: "Long sessions?", "Human review each phase?", "Strong TDD habit?", leading to Add/Skip GSD and Add/Skip Superpowers |
| Slide 13 notes include "when NOT to use SDD", adapted from textbook ch. 22 | ✅ | E3: the notes cite docs/textbook.md §22 |
| Both diagrams shipped in P1 | ✅ | Present in the build (E4) |

## US-7 (Should): native dark-theme diagrams
| Criterion | Status | Evidence |
|---|---|---|
| Diagrams on slides 3, 5, 7 and 19 are native shapes in both decks | ✅ | E3: `sdlc-adlc`, `sdd-pipeline`, `context-rot`, `branch-flow`; E1, check 10 (known diagrams); E4 EN slide 20 shows branch-flow |
| Nothing copied from the article | ✅ | All diagrams are generated shapes; no article images are in the repo |
| *(Could)* /team role diagram on slide 23 | ✅ | E3: `team-roles` diagram |
| *(Could)* SVG pairs in `docs/images/` | ❌ | Not produced. This was Could priority and was intentionally deferred (Ruling 2); nothing in the README or textbook needs them. No impact on the talk. |

## US-8 (Should): untimed appendix
| Criterion | Status | Evidence |
|---|---|---|
| A1–A6 come after Q&A, budget 0:00, notes start "backup, not timed" | ✅ | E1, check 3 (appendix rules); E3 |

## US-10 (Could): README links both decks
| Criterion | Status | Evidence |
|---|---|---|
| README links the EN and HE decks | ✅ | README "Slide decks" section and "Learn more" (Task 10, uncommitted) |

## US-11 (Must): Tips
| Criterion | Status | Evidence |
|---|---|---|
| Visible Tip box on ≥10 timed slides, ≤1 per slide, none on Title/Resources/Q&A | ⚠️ | E1, check 6: 17 tips on timed slides. **Caveat:** the box shows a "TIP" pill label in both decks with no light-bulb icon, rather than "Tip"/"טיפ". This follows the later human decisions 8–9 (TIP stays in English; טיפ is forbidden). The criterion text predates those decisions. |
| ≤20 words, starts with an action verb, doable without new tools | ✅ | E1, check 6 (word count). E3: each EN tip starts with a verb (List, Explore, Fix, Point, Start, Borrow, Write, Ask, Photograph, Keep, Review, Turn); each HE tip starts with a plural imperative. |
| Keyed one-to-one EN/HE | ✅ | E1, check 2 |
| Notes may expand a Tip; the slide text stands alone | ✅ | E3 |
| The icon/label renders the same in both decks | ✅ | E4: identical TIP pill in EN slides 13, 20 and 25 and HE slide 18 (mirrored in HE, as designed) |

## US-12 (Must): GitHub workflow in a nutshell
| Criterion | Status | Evidence |
|---|---|---|
| 3 slides (19–21), 5:00, after the case study, this repo as the example | ✅ | E3: 1:30 + 1:30 + 2:00 |
| Slide 19: main = published, dev = draft; merge after tests pass | ✅ | E3 slide 19 bullets |
| Slide 20: issues = to-do card; changes land via PRs only | ✅ | E4 EN slide 20 |
| Slide 21: shared repo, `specs/` as the team notebook, with `specs/001-heltec-monitor/` as the example | ✅ | E3 slide 21 bullets and notes |
| Repo-history claims pass F11–F13 | ✅ | E6/E7: PR #4 chain corrected; one-person project, no CI, unlocked main all disclosed. (The tags push is tracked under US-5.) |
| No new tools beyond git/GitHub; Heltec arc unchanged | ✅ | E3 |

## US-13 (Must, thin): what's next
| Criterion | Status | Evidence |
|---|---|---|
| 3 slides (22–24) at 1:00 each | ✅ | E3 |
| Framed explicitly as "what's next, not day one" | ✅ | Fixed in the fix wave: the slide 22 notes (EN + HE) now open with "What's next, not day one: once the basics feel normal, these three ideas are where teams go." |
| Slide 22 Skills (recipe card) · 23 /team meta example · 24 shared constitution (house rules) | ✅ | E3 slides 22–24 |
| No unverified built-in feature claims (F14–F15) | ✅ | E3: "custom setup … not a product you can download"; "team practice rather than a built-in feature" |

## Summary
- **❌ (1):** US-7 Could item, SVG pairs. Deferred by design; no impact.
- **⚠️ (6):**
  1. Acronyms: ADLC, BMAD and GSD are expanded only in the notes; "PR #3" appears on slide 19 before PR is defined.
  2. US-3: realistic speaking time is unproven until a timed rehearsal (human).
  3. US-4: the manual PowerPoint bidi pass is not done (human). Check HE slide 14 "ל-25 °C" wrapping and the HE slide 18 °C captions first.
  4. US-5: the "tagged on GitHub" claim depends on the tags push (human, after the account switch).
  5. US-11: the Tip label is "TIP" with no light bulb, per later human decisions. Accept as superseded.
  6. US-13: "what's next, not day one" framing. ✅ Resolved in the fix wave (opening line added to the slide 22 notes, EN + HE).

  Items 2–4 are the three that stay ⚠️ until the human acts. Items 1, 5 and 6 are copy-level caveats.
- **Recommendation:** accept for delivery once the human completes the bidi pass, the rehearsal and the tags push. The two optional copy fixes (US-13 framing line, ADLC on-slide expansion) are now in the fix wave.
