# Product Brief: Theory-First SDD Talk for Beginners (EN + HE decks)

**Date:** 2026-11-18 | **Owner:** Product Owner | **Status:** Draft, round 2 (scope change from the human) applied

## Goal
Turn the existing 26-slide practical Spec Kit workshop deck into a 45-minute, theory-first talk on Spec-Driven Development (SDD) for **beginners**. The talk explains every idea through everyday intuition before naming it. It closes with three practical parts: the Heltec/DHT22 run as a short case study, the GitHub team workflow in a nutshell, and a "what's next" look at advanced practices. It ships as two decks with identical content, English and Hebrew.

## Problem
The current deck shows *how* to run Spec Kit, to an audience assumed to know the vocabulary. Beginners need the *why*: why specs beat prompts, why AI "forgets", and how the frameworks differ. They also need the everyday practices that make SDD work in a team (branches, issues, PRs, a shared `specs/` folder), plus a pointer to where to go next. The reference article (Dwarampudi, "Spec-Driven AI: BMAD, SpecKit, GSD & Superpowers", Medium, Jun 2026) supplies the theory. Several of its claims needed fact-checking (see the register below).

## Users & context
- **Primary audience:** beginners. They may have used a chat assistant, but they don't know terms like context window, TDD, PR or constitution. *(A1, set by the human)*
- **Presenter:** the repo owner, giving a live talk in English or Hebrew.
- **Setting:** a meetup or class with a projector. The hardware demo uses **photos only**; there is no live run.

## Constraints (from architect rulings)
- **Single content source (Ruling 1).** Both decks are generated from one content source. Each slide has EN and HE text, keyed bullets, a keyed Tip, notes and a time budget, built on a shared dark template that reuses the current background, palette and photos. The hand-made polish of the current deck is approximated, not preserved (Open question 1).
- **Native diagrams (Ruling 2).** Diagrams are native, dark-theme slide shapes, built from the same source. SVG pairs are optional.

## Success criteria
1. The talk runs within **45:00, including 3:00 of Q&A**, timed by the speaker-note budgets.
2. A beginner can follow every slide: each concept is introduced through an analogy or everyday example before its formal term.
3. The EN and HE decks match slide for slide, Tip for Tip, and timing for timing. This is checked automatically.
4. Every factual claim about third-party frameworks or about this repo is verified with a source in the notes, or reworded so it isn't presented as fact.

## Cross-cutting standards (Must, apply to every story)
- **Beginner tone:**
  - Every concept slide shows an intuition (an analogy or everyday example) **before** the formal term.
  - Every acronym (SDD, SDLC, ADLC, TDD, PR, CI…) is spelled out and given a one-line plain definition at its first appearance.
  - No content slide has more than 5 bullets.
- **Visual baseline:** both decks keep the dark navy background, the palette and the hardware photos. The Tip box (US-11) is a new, consistent layout element.
- **Validator (automated, must pass for both decks):**
  1. Both decks have the same slide count and order.
  2. Each slide has the same bullet keys and count, and the same Tip key (or none), in EN and HE.
  3. Timed-slide budgets sum to exactly 45:00, and the Q&A slide is 3:00.
  4. Every note starts with `[m:ss] [@mm:ss]`, where `@` is the elapsed time at the **end** of the slide.
  5. Every timed slide except Title, Resources and Q&A has a notes line starting `Analogy:`.
  6. There are at least 10 Tips in the deck and at most 1 per slide, each 20 words or fewer in each language.

## User stories, acceptance criteria, priority

**US-1 (Must):** As a beginner, I want a theory-first arc of about 24 minutes that builds intuition before vocabulary, so that I understand *why* SDD exists before I see any tool.
- [ ] The theory slides (1-13) have budgets summing to 23-25 minutes.
- [ ] The order is: intent gap (SDLC vs ADLC) → vibe coding vs SDD → SDD core idea → context engineering → context rot → four frameworks → layer summary → decision rule.
- [ ] Each theory slide has its analogy on the slide or in the notes. Examples: a spec is a recipe, not "cook something nice"; context rot is a whiteboard so full that old notes get missed.
- [ ] Theory slides may name workflow stages. They show no slash commands, CLI syntax or firmware detail.

**US-2 (Must):** As a beginner, I want the Heltec run as a short case study of about 8 minutes, so that I see the theory work on something real.
- [ ] The case-study slides (14-18) have budgets summing to 7:30-8:30.
- [ ] They include, at minimum:
  - the board and the requirement, with implicit vs explicit;
  - the hysteresis decision;
  - the plan plus tested logic (11/11) on **one** merged slide;
  - what `/speckit-analyze` caught;
  - the behavior demo as OK/WARNING **photos, 2:00, no live run**.
- [ ] Every case-study slide names the **DHT22** as the sensor used. BME280 appears only as "also supported at build time".
- [ ] The "which layers this run used" mapping is one line on the Takeaways slide, not a separate slide.

**US-3 (Must):** As the presenter, I want timed speaker notes on every slide, so that I keep to 45:00.
- [ ] Every slide in both decks has written notes, replacing the current stubs. The notes start with the timing prefix, and the last timed slide (Q&A) ends at `[@45:00]` (validator items 3 and 4).

**US-4 (Must):** As a Hebrew-speaking beginner, I want a Hebrew deck identical in content to the English one.
- [ ] `presentation/speckit-workshop.pptx` stays EN. The HE deck is a separate file next to it (A3).
- [ ] The validator passes items 1 and 2 for HE vs EN.
- [ ] Hebrew text is right-to-left and right-aligned, in a font with Hebrew glyphs (Arial or Noto Sans Hebrew). Technical terms may stay in English, but each one gets a Hebrew plain-language gloss at first use.
- [ ] A listed set of mixed Hebrew/English lines, including all Tips, passes a manual review in PowerPoint for word order and punctuation.
- [ ] Every diagram and Tip box appears in both decks, in that deck's language.

**US-5 (Must):** As a beginner, I want accurate claims, so that I can trust the talk.
- [ ] Every row in the Fact-check register (F1-F15) is resolved as it says.
- [ ] No star counts on slides, no "21+ roles", no "Lex Christopherson". GSD links go to `github.com/open-gsd/gsd-core`. Article opinions are attributed to the article, and the article is credited.

**US-6 (Must):** As a beginner, I want one picture of how the frameworks fit together and a simple decision rule, so that I leave with a choice rather than a list.
- [ ] Slide 12 shows the four metaphors (team / document / context / discipline) and their two layers (planning/governance vs execution discipline). It has at most 4 boxes plus 2 labels, at 24pt or larger.
- [ ] Slide 13 is a decision rule with 2-3 plain-language questions (e.g. "Are your AI sessions long?", "Does a human check every step?", "Do you already write tests first?"), each leading to the layers it implies.
- [ ] Its notes include "when NOT to use SDD", adapted from textbook ch. 22.
- [ ] Both diagrams ship in P1.

**US-7 (Should):** As the presenter, I want the remaining diagrams drawn natively in the dark theme.
- [ ] Diagrams on slides 3, 5, 7 and 19 (branch flow) are native shapes in both decks.
- [ ] Nothing is copied from the article.
- [ ] *(Could)* A /team role diagram on slide 23.
- [ ] *(Could)* SVG pairs in `docs/images/`.

**US-8 (Should):** As the presenter, I want cut slides kept as an untimed appendix after Q&A.
- [ ] Appendix slides come after Q&A, are excluded from the 45:00 check, and their notes say "backup, not timed".

**US-10 (Could):** As a README reader, I want links to both decks.
- [ ] The README links the EN and HE decks.

**US-11 (Must): Tips.** As a beginner, I want short, practical Tips I can act on tomorrow, so that the talk turns into habits.
- [ ] A visible Tip box with a light-bulb icon and the label "Tip" / "טיפ" appears on at least 10 timed slides, at most 1 per slide. There are none on Title, Resources or Q&A.
- [ ] Each Tip is 20 words or fewer in each language, starts with an action verb, and is something a beginner can do without new tools. Example: "Before asking the AI to code, write three sentences: who it's for, what it does, how you'll know it works."
- [ ] Tips have keys and match one to one between EN and HE (validator item 6).
- [ ] The notes may expand a Tip, but the slide text stands on its own.
- [ ] The icon renders the same in both decks on the presenting machine, checked in the manual pass.

**US-12 (Must): GitHub workflow in a nutshell.** As a beginner joining a team, I want to know how a shared repo keeps work safe and visible, so that I can contribute without breaking things or duplicating work.
- [ ] There is a 3-slide section (19-21) totaling 5:00. It comes after the case study, with this repo as the worked example.
- [ ] Slide 19 covers `main` vs `dev`: `main` is always working ("the published book"), `dev` is where work happens ("the draft"). Work merges to `main` only after tests pass and it is verified.
- [ ] Slide 20 covers issues and pull requests: issues track enhancements and bugs ("the team to-do board"). Changes land only through PRs, never by pushing directly to `main` ("a reviewed change request").
- [ ] Slide 21 covers the team, a shared repo with more than one developer and a shared `specs/` folder. It shows `specs/001-heltec-monitor/` as "the team's shared notebook: everyone can see what everyone else is building and why".
- [ ] Any claim about this repo's own history (PR numbers, branch names, contributors, CI) passes F11-F13 before it appears on a slide.
- [ ] The section introduces no new tools beyond git/GitHub, and the Heltec arc is not changed.

**US-13 (Must, kept thin): Advanced / What's next.** As a beginner, I want a short map of where to go after the basics, so that I know what to learn next without being overwhelmed.
- [ ] There is a 3-slide section (22-24) at 1:00 each, framed explicitly as "what's next, not what to do on day one".
- [ ] Slide 22, Skills: reusable agent instructions ("a recipe card you hand the AI").
- [ ] Slide 23, Teams of skills: several role-playing agents with a coordinator. The meta example is that this brief was produced by a /team run, with an architect, a product owner and a senior developer negotiating scope.
- [ ] Slide 24, Shared constitution across projects and teams ("house rules that every project inherits").
- [ ] The section makes no claims of built-in product features that F14-F15 haven't verified.
- [ ] *(Could)* Deeper material goes in the appendix.

## Proposed slide outline (45:00)

| # | Slide | Source | Min | Ends @ |
|---|---|---|---|---|
| **Part 0: Hook** | | | | |
| 1 | Title + article credit | S1 | 0.5 | 0:30 |
| 2 | One prompt, many hidden questions | S2+S3 | 1.0 | 1:30 |
| **Part I: Why SDD** | | | | |
| 3 | Intent gap: SDLC vs ADLC | NEW + diagram | 2.5 | 4:00 |
| 4 | Vibe coding vs SDD | S4+S5+S13 | 2.5 | 6:30 |
| 5 | SDD core idea: spec as source of truth, stages + gates, feedback loop, constitution | NEW + diagram | 2.5 | 9:00 |
| **Part II: Why the AI "forgets"** | | | | |
| 6 | Context engineering | NEW | 2.0 | 11:00 |
| 7 | Context rot | NEW + diagram | 2.0 | 13:00 |
| **Part III: The landscape** | | | | |
| 8 | BMAD: the agile team | NEW | 1.5 | 14:30 |
| 9 | Spec Kit: the living spec (absorbs the old "each stage catches a mistake") | S7+S9+S10 (+S6) | 2.0 | 16:30 |
| 10 | GSD: fresh context per task | NEW | 1.5 | 18:00 |
| 11 | Superpowers: enforced discipline | NEW | 1.5 | 19:30 |
| 12 | Four metaphors, two layers | NEW + diagram | 2.0 | 21:30 |
| 13 | Decision rule | NEW + diagram | 2.5 | 24:00 |
| **Part IV: Case study (Heltec + DHT22)** | | | | |
| 14 | Board and requirement; implicit vs explicit | S15+S16 | 1.5 | 25:30 |
| 15 | Specify: hysteresis decided, not guessed | S17+S18 | 1.5 | 27:00 |
| 16 | Plan + tested logic (11/11) | S19+S22 | 1.5 | 28:30 |
| 17 | What `/speckit-analyze` caught | S20+S21 | 1.5 | 30:00 |
| 18 | Behavior: OK/WARNING photos | S23 + photos | 2.0 | 32:00 |
| **Part V: GitHub workflow in a nutshell** | | | | |
| 19 | `main` vs `dev` | NEW + diagram | 1.5 | 33:30 |
| 20 | Issues and pull requests | NEW | 1.5 | 35:00 |
| 21 | Shared repo, shared `specs/`: this repo as example | NEW (+S24 tags in notes) | 2.0 | 37:00 |
| **Part VI: What's next** | | | | |
| 22 | Skills | NEW | 1.0 | 38:00 |
| 23 | Teams of skills: the /team meta example | NEW | 1.0 | 39:00 |
| 24 | Shared constitution across projects | NEW | 1.0 | 40:00 |
| **Close** | | | | |
| 25 | Takeaways (+ one line: which layers the Heltec run used) | S25 | 1.5 | 41:30 |
| 26 | Resources | S26 | 0.5 | 42:00 |
| 27 | Q&A | NEW | 3.0 | 45:00 |
| A1-A6 | Appendix (untimed): each stage catches a mistake (S6), overlap and gaps, `specify init` (S8), tool relationship (S11), VS Code extensions (S12), git checkpoints (S24) | backup | 0 | |

**Subtotals:**

| Part | Minutes |
|---|---|
| Theory (1-13) | 24:00 |
| Case study | 8:00 |
| GitHub | 5:00 |
| What's next | 3:00 |
| Close | 2:00 |
| Q&A | 3:00 |
| **Total** | **45:00** |

**Kept / merged / cut summary.**
- **Merged:** S2+S3, S4+S5+S13, S7+S9+S10 (+S6 content), S15+S16, S17+S18, **S19+S22**, S20+S21.
- **Rewritten:** S25, S26.
- **Moved to the appendix:** S6, overlap and gaps, S8, S11, S12, S24.
- **Removed:** the separate "back to the model" slide, folded into Takeaways.

## Density risk (honest assessment)
With 27 timed slides in 42 minutes of speaking, the pace averages about 1:33 per slide. Ten slides are 1:30 or less, for an audience that needs analogies first. That is tight. To keep it credible I have already:
- moved two slides to the appendix (S6 and overlap/gaps);
- cut each framework to 1:30 (Spec Kit keeps 2:00 as the bridge to the case study);
- kept "What's next" deliberately thin.

If a timed rehearsal overruns, these are the relief valves, in order:
1. Merge slides 22-24 into a single "What's next" slide (2:00), freeing 1:00.
2. Merge GSD and Superpowers into one "execution helpers" slide (2:00), freeing 1:00.
3. Move slide 6 (context engineering) into the notes of slide 7, freeing 2:00.

Any freed time goes to the beginner-heavy slides 3-5.

## New diagrams (native, dark theme, both decks)
| Diagram | Slide | Priority |
|---|---|---|
| SDLC vs ADLC | 3 | Should, P2 |
| SDD pipeline | 5 | Should, P2 |
| Context-rot curve (no numbers) | 7 | Should, P2 |
| Four metaphors, two layers | 12 | Must, P1 |
| Decision rule | 13 | Must, P1 |
| Branch flow: issue #2 → feature branch → PR #3 → `dev` → PRs #4–7 → `main` (one diagram, highlight varies on 19/20/21) | 19–21 | Must, P1 (Ruling R2-2) |
| /team roles | 23 | Could |

## Fact-check register
| # | Claim | Finding | Resolution |
|---|---|---|---|
| F1 | BMAD has "21+ roles" | Unverifiable | "Multiple specialized roles (Analyst, PM, Architect, Dev, QA…)" |
| F2 | Superpowers got "170k stars in 3 months" | False: 319,587 stars; repo created 2025-10-09 | No counts on slides. Notes may say "300k+ (Nov 2026)". |
| F3 | Superpowers' 7 steps, deleting pre-test code, 2-stage review | Verified (README) | Use, citing the README |
| F4 | The GSD repo | Original repo archived → `open-gsd/gsd-core` | Link gsd-core only; the notes mention the move |
| F5 | The creators | Jesse Vincent verified; "Lex Christopherson" not verified (original credits "TÂCHES") | No GSD creator named on the slide |
| F6 | "200k tokens per task" | gsd-core README claim only | Slide: "fresh context per task"; notes cite the README |
| F7 | Context rot "measurable" | Candidates: Chroma "Context Rot" (2025), Liu et al., "Lost in the Middle" (TACL 2024) | Verified citation in the notes, or "widely observed by practitioners" |
| F8 | "ADLC" | Not a standard term | Attribute to the article |
| F9 | "Converging on all four" | Opinion | Attribute to the article |
| F10 | A five-stage pipeline | Spec Kit also has Clarify and Analyze | Five stages + two gates |
| F11 | PRs #3, #6, #7 merged dev→main | **Conflict:** the git log shows PR #3 merged from `001-heltec-monitor-dht22-sensor`, not `dev` | Verify each PR's source branch. Show only verified numbers and branches, or describe the flow without PR numbers. |
| F12 | "A shared repo with more than one developer" | This repo may have a single contributor | If single, present the multi-developer flow as "how it works in a team", not as this repo's history |
| F13 | "Merge only after tests pass" | Not verified whether this repo has CI | Present it as the team rule. Claim the repo enforces it only if CI or branch protection exists. |
| F14 | Skills and /team as a reusable mechanism | Needs to name what is actually used (agent skills; the /team run that made this brief) | Describe only what was actually used. Don't call /team a public product unless it is. |
| F15 | Sharing a constitution across projects | The Spec Kit constitution is per-project; sharing it is a practice, not a verified feature | Present it as a practice (e.g. a team template). No feature claim. |

## Delivery phasing
- **P1:** content source, generator, EN deck, validator, US-11 Tips, and the slide 12/13 diagrams.
- **P2:** the remaining diagrams.
- **P3:** the HE deck and US-10.

The work is not done until P3 ships. **The 3-4 day estimate needs a re-estimate from the developer** for the new scope (US-11/12/13, beginner rewrite of all notes, analogy lines).

## Out of scope
- New firmware or hardware runs, and BME280 re-verification.
- A live hardware demo.
- Live demos of BMAD, GSD, Superpowers, skills or /team.
- Teaching git commands or a GitHub UI walkthrough. The section is concepts only.
- Setting up CI or branch protection on this repo.
- Pixel-exact preservation of the old polish.
- Changes to the textbook.
- Video or a PDF export.
- Languages other than EN and HE.

## Assumptions (please correct)
- **A1 (set by the human):** The audience is beginners. Intuition comes first, then the formal term.
- **A2 (set by the human):** Q&A is 3:00 inside the 45:00.
- **A3:** The HE deck file is `presentation/speckit-workshop-he.pptx`.
- **A4:** Speaker notes, including the `Analogy:` lines, are written in each deck's own language.
- **A5:** The talk's stance is neutral: "pick layers using the decision rule".
- **A7:** Tips are visible on the slide (my reading of "Tip notes"). See Open question 2.

## Open questions (blocking)
1. **For the human:** Is it acceptable that the generated decks only approximate the hand-made polish of the current deck?
2. **For the human:** By "Tip notes", did you mean a visible Tip box on the slide (as briefed), or tips only in the speaker notes? Notes-only would remove one layout element and ease density.
3. **For the human:** The GitHub example: PR #3 came from a feature branch, not `dev`, and the repo may have a single developer. Should slide 21 show this repo exactly as it is, or present the ideal team flow with the repo as an illustration?
4. **For the human:** If rehearsal overruns, do you accept the relief-valve order (What's next → GSD/Superpowers → context engineering)?
5. **For the human:** Should cut slides go into an untimed appendix, or be deleted?
6. **For the human:** Neutral stance (A5): agree?

## Negotiation log

**Round 1 (2026-11-18): developer feasibility review and architect rulings**

| # | Point | PO position | Outcome |
|---|---|---|---|
| N1 | There is no generator; the deck is hand-polished | Ruling 1 | Accepted. Constraint plus Open question 1; the visual baseline is held. |
| N2 | Native diagrams | Ruling 2 | Accepted; SVG pairs moved to Could. |
| N3 | S18 is hysteresis; S15/S19 say BME280 | Accept | Outline remapped; DHT22 AC added. |
| N4 | Star counts | Counter: none on slides | Dated counts allowed in notes only. |
| N5 | F1, F3-F7 | Accept | Register updated. |
| N6 | Diagrams in P2 | Hold: slides 12/13 ship in P1 | Phasing updated. |
| N7 | 3-4 day estimate | Accept | Superseded by N24. |
| N8 | Ruling 3: `@` = end-of-slide time | Accept | US-3 updated. |
| N9 | Ruling 4: bullet keys, bidi manual pass, HE font | Accept | US-4 updated. |
| N10 | Ruling 5: CLI in theory | Stage names OK; no slash commands | US-1 updated. |
| N11 | Ruling 6: "adapted from" ch. 22 | Accept | US-6 updated. |
| N12 | Ruling 7: merge metaphors and layers | Accept | Now slide 12. |
| N13 | Ruling 8: photos by default, optional live | Accept | Superseded by N18 (no live run). |

**Round 2 (2026-11-18): scope change from the human**

| # | Point | PO position | Outcome |
|---|---|---|---|
| N14 | The audience is beginners; intuition before the term | Accept (human decision) | A1 rewritten; beginner-tone standard; US-1 analogy ACs; validator item 5. |
| N15 | Tips | Accept the visible Tip box reading, at most 1 per slide, at least 10 in total, 20 words or fewer | New US-11 (Must); validator item 6. Open question 2 asks whether notes-only was meant. |
| N16 | GitHub workflow section | Accept as Must, 5:00 / 3 slides, this repo as the example | New US-12. F11-F13 added: PR #3's source branch conflicts with the "dev→main" description. |
| N17 | Advanced / What's next | Accept as Must but thin, 3 x 1:00, framed as "next steps" | New US-13; F14-F15 added. |
| N18 | Case study 13:00 → 8:00 | Accept. Merge plan + tested logic; photos 2:00, no live run | Fold "back to the model" into Takeaways. US-2 rewritten. |
| N19 | Part III 13:00 → about 10:00 | Accept, with a counter: frameworks 1:30 each except Spec Kit at 2:00 (the bridge to the case study) | Part III is 10:30. |
| N20 | Making room | Proposal: move S6 and overlap/gaps to the appendix; S6's point lives on slide 9 and in the case study | Theory is 24:00. Outline sums to 45:00. |
| N21 | Density risk | Flagged honestly; three relief valves in a set order | Open question 4. |
| N22 | Validator constraints | Accept the "Analogy:" line and Tip counting; added Tip key matching and word limits | Six validator items listed. |
| N23 | Facts about this repo | Hold: no repo-history claim appears on a slide unless verified | F11-F15. |
| N24 | Effort | The scope grew | The developer must re-estimate before P1 starts. |

**Architect notes on round 2 (2026-11-18)**

- Open questions 1, 5 and 6 from round 2 were already answered by the human. See "Human decisions" above: generate both decks, untimed appendix, neutral stance.
- F11 resolved (checked against the git log and GitHub). The repo shows the full intended flow:
  - Issue #2: "Switch sensor from BME280 to DHT22". It is still OPEN even though the work is merged, which makes a teaching point: close the issue from the PR with "Fixes #2".
  - That issue was worked on feature branch `001-heltec-monitor-dht22-sensor`.
  - The feature branch merged into `dev` through PR #3.
  - `dev` then merged into `main` through PRs #1, #4, #5, #6 and #7.

  So slide 21 can show `issue → feature branch → PR → dev → PR → main` with real numbers.
- F12: commits come from two git identities (ronyronen and ronyrsim), probably one person. Ruling: present multi-developer collaboration as the target practice, with this repo as the illustration. Do not claim this repo had a team. — Why: honesty. — Cost if wrong: none.

**Human decisions, round 2 (2026-11-18)**

5. Tips go in a visible 💡 Tip box on the slide, as US-11 describes.
6. The GitHub section teaches the ideal team flow and uses this repo's real issue and PR numbers to illustrate it. It does not claim the repo had a team. Issue #2 being still open becomes a Tip: "Close issues from PRs with 'Fixes #2'".
7. The overrun relief valves follow the PO's order: (1) collapse What's next into 1 slide, (2) merge GSD and Superpowers, (3) fold context engineering into context rot.

**Round 2: developer feasibility and architect rulings (2026-11-18)**

The developer's re-estimate is **4.5–5.5 working days**:

| Phase | Estimate |
|---|---|
| P1 | 2.5–3 d, split into P1a (template, layouts with and without a Tip, validator, skeleton deck) and P1b (content) |
| P2 | 0.5–0.75 d |
| P3 | 1.5–2 d |

F13 is confirmed: `main` has no branch protection and the repo has no CI. "Merge only after tests pass" is therefore taught as a team rule, not shown as something this repo enforces.

- Ruling R2-1: Accept the P1a/P1b split. — Why: layout overflow surfaces before content is written. — Cost if wrong: about 0.25 d of scaffolding overhead.
- Ruling R2-2: The branch-flow diagram moves to P1 as a single linear chain built from box and arrow primitives, with a `highlight` parameter. It is reused on slides 19–21. There is no two-lane gitflow picture. — Why: a beginner GitHub section needs a visual, and the chain uses real issue and PR numbers. — Cost if wrong: about 45 minutes.
- Ruling R2-3: The Tip marker is a native pill shape labelled "TIP" / "טיפ", not an emoji, placed in a fixed bottom band, with the label side mirrored in HE. — Why: LibreOffice did not render emoji, and a native pill renders the same in both decks by construction. — Cost if wrong: only cosmetic.
- Ruling R2-4: The validator is the union of the brief's checks and the design's checks, plus "5 bullets or fewer" and "every F-ID slide has a URL in its notes", for 10 checks in total. — Why: cheap, and each check enforces an AC. — Cost if wrong: none.
- Ruling R2-5: Part IV slides (14–18) satisfy the Analogy rule with `Analogy: see slide N`. — Why: forced analogies on slides about real artifacts read as contrived. — Cost if wrong: novices get slightly less scaffolding in the case study, which reuses analogies from earlier slides.
- Ruling R2-6: Add relief valve 0, ahead of the human-approved order: slide 21 reuses the diagram and drops to 1:30, freeing 0:30. — Why: it cuts no content, so the approved order is unchanged. — Cost if wrong: none.
- Ruling R2-7: Do not close issue #2 until the deck ships. — Why: slide 20/21 uses it as a live teaching example.

**Human decisions, round 3 (2026-11-18)**

8. The Tip label reads "TIP" in English in both decks.
9. In the HE deck, any word or acronym normally said in English stays in English: framework names, acronyms, Git/GitHub vocabulary, and AI terms such as prompt, agent, context and spec. This replaces any earlier "טיפ" wording.
10. The human approved the brief and design and said to proceed with implementation ("go").
