#!/usr/bin/env python3
"""Builds presentation/speckit-workshop-draft-en.pptx -- an all-English
version of the deck. Diagrams come from presentation/assets/generated_en/
(pure LTR, no bidi needed); terminal/code content cards come from
presentation/assets/generated/ since they were already English-only
content (see make_content_cards.py) regardless of which language deck
uses them. Run from the repository root:

    python3 presentation/build_deck_en.py

Hardware-dependent slides are explicitly marked PENDING and contain no
fabricated data -- they will be completed after checkpoint
09-hardware-verified.
"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ASSETS = "presentation/assets/generated"
ASSETS_EN = "presentation/assets/generated_en"
OUT = "presentation/speckit-workshop-draft-en.pptx"

NAVY = RGBColor(0x0F, 0x17, 0x2A)
BLUE = RGBColor(0x25, 0x63, 0xEB)
SLATE = RGBColor(0x33, 0x41, 0x55)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
AMBER = RGBColor(0xD9, 0x77, 0x06)
RED = RGBColor(0xB9, 0x1C, 0x1C)
GREEN = RGBColor(0x15, 0x80, 0x3D)
LIGHT_BG = RGBColor(0xF8, 0xFA, 0xFC)
SECTION_BG = RGBColor(0x1E, 0x1B, 0x4B)

FONT = "Arial"

SW, SH = Inches(13.333), Inches(7.5)


def add_slide(prs, bg=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    if bg is not None:
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = bg
    return slide


def add_title(slide, text, top=Inches(0.35), color=NAVY, size=30, height=Inches(0.9)):
    box = slide.shapes.add_textbox(Inches(0.5), top, SW - Inches(1.0), height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = True
    r.font.name = FONT
    r.font.color.rgb = color
    return box


def add_bullets(slide, items, top=Inches(1.4), left=Inches(0.6), width=None, height=Inches(4.6), size=20):
    width = width or (SW - Inches(1.2))
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(12)
        text, kwargs = (item, {}) if isinstance(item, str) else (item["text"], item)
        r = p.add_run()
        r.text = text
        r.font.size = Pt(kwargs.get("size", size))
        r.font.bold = kwargs.get("bold", False)
        r.font.italic = kwargs.get("italic", False)
        r.font.name = FONT
        r.font.color.rgb = kwargs.get("color", SLATE)
    return box


def add_note(slide, text):
    notes = slide.notes_slide
    notes.notes_text_frame.text = text


def add_pending_banner(slide, text="Pending physical hardware verification (checkpoint 09-hardware-verified)"):
    box = slide.shapes.add_textbox(Inches(0.6), SH - Inches(0.85), SW - Inches(1.2), Inches(0.55))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "⏳ " + text
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.italic = True
    r.font.name = FONT
    r.font.color.rgb = AMBER
    rect = slide.shapes.add_shape(1, Inches(0.5), SH - Inches(0.95), SW - Inches(1.0), Inches(0.7))
    rect.fill.solid()
    rect.fill.fore_color.rgb = RGBColor(0xFE, 0xF3, 0xC7)
    rect.line.color.rgb = AMBER
    rect.line.width = Pt(1.5)
    rect.shadow.inherit = False
    spTree = slide.shapes._spTree
    spTree.remove(rect._element)
    spTree.insert(2, rect._element)
    return box


def add_missing_visual_placeholder(slide, label, left, top, width, height):
    rect = slide.shapes.add_shape(1, left, top, width, height)
    rect.fill.solid()
    rect.fill.fore_color.rgb = RGBColor(0xF1, 0xF5, 0xF9)
    rect.line.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
    rect.line.width = Pt(1.5)
    rect.line.dash_style = 4
    tf = rect.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "\U0001F4F7 " + label
    r.font.size = Pt(16)
    r.font.italic = True
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = "(real screenshot missing -- see screenshot-checklist.md)"
    r2.font.size = Pt(13)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    return rect


def add_image(slide, path, left, top, width=None, height=None, en=False):
    base = ASSETS_EN if en else ASSETS
    full = os.path.join(base, path)
    return slide.shapes.add_picture(full, left, top, width=width, height=height)


def main():
    prs = Presentation()
    prs.slide_width = SW
    prs.slide_height = SH

    # ---------- Slide 1: Title ----------
    s = add_slide(prs, bg=NAVY)
    box = s.shapes.add_textbox(Inches(1), Inches(2.3), SW - Inches(2), Inches(1.6))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "From Prompt to Product"
    r.font.size = Pt(48)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = FONT
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = "Spec-Driven Development with GitHub Spec Kit"
    r2.font.size = Pt(28)
    r2.font.color.rgb = RGBColor(0xA5, 0xB4, 0xFC)
    r2.font.name = FONT

    box2 = s.shapes.add_textbox(Inches(1), Inches(4.3), SW - Inches(2), Inches(0.8))
    tf2 = box2.text_frame
    p3 = tf2.paragraphs[0]
    p3.alignment = PP_ALIGN.CENTER
    r3 = p3.add_run()
    r3.text = "A real example on the Heltec WiFi Kit V3"
    r3.font.size = Pt(20)
    r3.font.italic = True
    r3.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)
    r3.font.name = FONT
    add_note(s, ("Open with a show of hands: who has ever asked an AI coding assistant to 'just build X' from a single sentence? "
                 "Almost everyone has. This talk is about what happens next -- and about a specific, real embedded-systems example "
                 "(a temperature monitor on a Heltec ESP32 board) that we'll follow from a vague prompt all the way to tested, "
                 "working, physically-verified firmware. No prior Spec Kit, embedded, or even AI-agent experience is assumed."))

    # ---------- Slide 2: The vague prompt ----------
    s = add_slide(prs)
    add_title(s, "The Vague Prompt")
    rect = s.shapes.add_shape(1, Inches(1.0), Inches(1.7), SW - Inches(2.0), Inches(1.8))
    rect.fill.solid()
    rect.fill.fore_color.rgb = LIGHT_BG
    rect.line.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
    box = s.shapes.add_textbox(Inches(1.2), Inches(1.8), SW - Inches(2.4), Inches(2))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = ("Build an application for a Heltec WiFi Kit V3 that reads a sensor,\n"
              "shows the value on the display, and shows a warning when the value is too high.")
    r.font.size = Pt(22)
    r.font.name = "Courier New"
    r.font.color.rgb = SLATE
    box3 = s.shapes.add_textbox(Inches(1.2), Inches(4.2), SW - Inches(2.4), Inches(1))
    tf3 = box3.text_frame
    tf3.word_wrap = True
    p3 = tf3.paragraphs[0]
    p3.alignment = PP_ALIGN.CENTER
    r3 = p3.add_run()
    r3.text = "❓ Is this enough information to build the correct product?"
    r3.font.size = Pt(28)
    r3.font.bold = True
    r3.font.color.rgb = RED
    r3.font.name = FONT
    add_note(s, ("Read the prompt out loud, slowly. It sounds complete -- it has a sensor, a display, a warning. "
                 "That's the trap: it reads like a spec but it isn't one. Give the audience a real moment of silence here "
                 "before moving to slide 3, where we'll pull apart everything this single sentence quietly left undecided."))

    # ---------- Slide 3: Open questions ----------
    s = add_slide(prs)
    add_title(s, "Everything the Prompt Never Answered")
    add_bullets(s, [
        {"text": "A coding agent still has to answer every one of these -- it just answers them silently, by guessing:", "italic": True, "size": 18},
        "Which sensor is actually connected? (temperature-only? temperature + humidity? which chip?)",
        "How often should the value be sampled -- once a second, once a minute?",
        "What exactly counts as \"too high\" -- what is the numeric threshold?",
        "What happens right at the threshold -- does it flicker on and off as the value hovers there?",
        "Once the warning is showing, at what point does it clear again?",
        "What should happen if the sensor stops responding or returns garbage?",
        "What should the display show while that error is happening?",
        "What, if anything, gets written to the Serial console for debugging?",
    ], size=19)
    add_note(s, ("Each bullet is a real decision, and an unspecified prompt does not remove the decision -- it just moves it "
                 "into the model's head, where you can't see it, review it, or agree with it. Optionally show "
                 "examples/prompt-only/naive_monitor.ino here to prove these aren't hypothetical: point out which lines in "
                 "the real generated code quietly picked an answer to each question above."))

    # ---------- Slide 4: Core message ----------
    s = add_slide(prs, bg=NAVY)
    box = s.shapes.add_textbox(Inches(1), Inches(2.6), SW - Inches(2), Inches(2.2))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "The problem is usually not that the AI cannot write the code."
    r.font.size = Pt(30)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = FONT
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = "The problem is that the product behavior was not sufficiently defined."
    r2.font.size = Pt(30)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0xFC, 0xD3, 0x4D)
    r2.font.name = FONT
    add_note(s, ("This is the one sentence the audience should remember from the whole workshop -- pause for a beat after "
                 "reading it aloud. Modern AI models are already good enough at writing code; that is not the bottleneck "
                 "anymore. The bottleneck moved upstream, to deciding *what* the code should do. Spec Kit, which we introduce "
                 "shortly, is a tool for making that decision-making step explicit and structured instead of implicit and skipped."))

    # ---------- Slide 5: Prompt loop ----------
    s = add_slide(prs)
    add_title(s, "From Prompt to an Infinite Loop")
    add_image(s, "diagram-prompt-vs-spec-en.png", Inches(0.5), Inches(1.3), width=SW - Inches(1.0), en=True)
    add_note(s, ("Focus only on the TOP half of this diagram for now (we'll come back to the bottom half on the next slide). "
                 "This is the ordinary loop when you skip specification: prompt -> code -> you notice something is wrong -> "
                 "you send a follow-up prompt to fix it -> that fix reveals or breaks something else -> repeat. Every 'Fix' "
                 "box is a product decision that got made *after* code already existed and contradicted it -- which is the "
                 "most expensive possible time to make that decision, because now there's already code and possibly a user "
                 "depending on the wrong behavior."))

    # ---------- Slide 6: Spec-driven alternative ----------
    s = add_slide(prs)
    add_title(s, "The Alternative: A Spec-Driven Process")
    add_image(s, "diagram-prompt-vs-spec-en.png", Inches(0.5), Inches(1.3), width=SW - Inches(1.0), en=True)
    add_note(s, ("Now point at the BOTTOM half of the same diagram. The difference is not 'more paperwork' -- it's the same "
                 "decisions (which sensor, what threshold, what happens on error) being made once, on purpose, in a short "
                 "clarification step, before any code exists -- instead of one at a time, by accident, after code already "
                 "exists and needs to be un-written. Same total number of decisions either way; the only thing that changes "
                 "is *when* they get made, and that timing is the entire value proposition of this workshop."))

    # ---------- Slide 7: What each stage catches ----------
    s = add_slide(prs)
    add_title(s, "What Each Stage Catches")
    subtitle = s.shapes.add_textbox(Inches(0.8), Inches(1.05), SW - Inches(1.6), Inches(0.5))
    stf = subtitle.text_frame
    stf.word_wrap = True
    sp = stf.paragraphs[0]
    sp.alignment = PP_ALIGN.LEFT
    sr = sp.add_run()
    sr.text = "Every stage exists to catch one specific kind of mistake -- before it becomes code:"
    sr.font.size = Pt(18)
    sr.font.italic = True
    sr.font.name = FONT
    sr.font.color.rgb = SLATE

    rows = [
        ("constitution", "A rule gets silently broken because nobody wrote it down"),
        ("specify", "We never agreed what this does"),
        ("clarify", "We agreed on the happy path, not the edges"),
        ("plan", "We agreed on what, not how -- and how has real constraints"),
        ("tasks", "We know the plan, not the order or the dependencies"),
        ("analyze", "Two of our own documents quietly contradict each other"),
        ("implement", "(this is the only step prompt-only starts from)"),
    ]
    top = Inches(1.75)
    row_h = Inches(0.68)
    for term, desc in rows:
        box = s.shapes.add_textbox(Inches(0.8), top, SW - Inches(1.6), row_h)
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = f"{term:<13}"
        r.font.size = Pt(21)
        r.font.bold = True
        r.font.name = "Courier New"
        r.font.color.rgb = BLUE
        r2 = p.add_run()
        r2.text = f"  →  {desc}"
        r2.font.size = Pt(20)
        r2.font.name = FONT
        r2.font.italic = term == "implement"
        r2.font.color.rgb = SLATE
        top += row_h
    add_note(s, "Walk through all seven stages briefly here; the deep dive on each one comes later in the Heltec walkthrough section.")

    # ---------- Slide 8: Spec Kit definition ----------
    s = add_slide(prs)
    add_title(s, "What Is GitHub Spec Kit -- and Why Does It Exist?")
    add_bullets(s, [
        {"text": "It's an open-source toolkit published by GitHub (github.com/github/spec-kit) -- free, not a product you buy.", "bold": True},
        "Concretely, it is two things: a small command-line tool called specify, plus a set of Skills/Commands "
        "(the /speckit-... commands we've been showing) that it installs into your AI coding agent -- Claude Code, Codex, "
        "or others.",
        "Spec Kit does not write your application code itself, and it is not an AI model. It structures the *process* "
        "a human and an AI agent go through together before and while code gets written: agree on rules, write down "
        "requirements, resolve ambiguity, plan the technical approach, break work into tasks, cross-check everything "
        "for contradictions, then implement.",
        {"text": "Why GitHub built it: as AI coding agents got fast enough to generate whole features in seconds, teams "
         "found the code was rarely the bottleneck anymore -- unclear or unstated requirements were. This pattern is "
         "called \"spec-driven development,\" and Spec Kit is GitHub's tooling for it: a practical way to keep the speed "
         "of an AI agent without giving up the discipline of knowing what you're actually building.", "size": 18},
    ], size=20, top=Inches(1.25), height=Inches(4.7))
    add_missing_visual_placeholder(s, "Spec Kit website + GitHub repo", Inches(0.8), Inches(6.05), SW - Inches(1.6), Inches(1.1))
    add_note(s, ("This slide is the anchor for the whole talk -- take your time. Key points to say out loud: (1) it's from "
                 "GitHub, it's free and open-source, this is not a pitch for a paid product; (2) it doesn't replace Claude "
                 "Code or Codex -- those are the agents that actually write code, Spec Kit is the structured process layer "
                 "on top of them (this gets its own diagram two slides from now); (3) the motivating problem is exactly what "
                 "slides 2-4 just showed: fast code generation exposed how much of the real work is actually deciding what "
                 "to build. If time allows, briefly show the real Spec Kit GitHub repo and its README (screenshots #1-2 on "
                 "the checklist) so the audience sees this is a real, actively maintained project, not a one-off script."))

    # ---------- Slide 9: Installation ----------
    s = add_slide(prs)
    add_title(s, "Installation")
    box = s.shapes.add_textbox(Inches(1.2), Inches(1.5), SW - Inches(2.4), Inches(1.0))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = "uv tool install specify-cli\nspecify init --here --integration claude"
    r.font.size = Pt(20)
    r.font.name = "Courier New"
    r.font.color.rgb = SLATE
    add_image(s, "terminal-specify-init.png", Inches(1.0), Inches(2.7), width=Inches(11.3))
    add_note(s, ("The first line installs the specify CLI itself (a one-time setup, via the uv Python tool). The second line "
                 "runs it inside an existing project folder and tells it which agent to wire up -- here, Claude Code. This "
                 "creates a .specify/ folder (templates, scripts, the project constitution) and a .claude/skills/ folder with "
                 "the /speckit-... commands. The terminal output below is the real, unedited output captured from this "
                 "repository's own initialization -- nothing here is staged or simulated."))

    # ---------- Slide 10: 7-stage workflow ----------
    s = add_slide(prs)
    add_title(s, "The Workflow in Seven Stages")
    add_image(s, "diagram-speckit-workflow-en.png", Inches(0.6), Inches(1.6), width=SW - Inches(1.2), en=True)
    add_note(s, ("Don't dive into command syntax yet -- the goal here is just the mental model of the pipeline: "
                 "constitution (project-wide rules, written once) -> specify (what are we building) -> clarify (resolve "
                 "the ambiguous parts) -> plan (technical approach) -> tasks (break the plan into ordered, checkable steps) "
                 "-> analyze (automatically cross-check spec/plan/tasks for contradictions) -> implement (the agent writes "
                 "the code). Each stage produces a real file in the repo, which is the subject of the next slide. We already "
                 "previewed *why* each stage exists on slide 7 -- this slide is the order they run in."))

    # ---------- Slide 11: Real files ----------
    s = add_slide(prs)
    add_title(s, "The Output: Real Files in the Repository")
    add_bullets(s, [
        {"text": "specs/001-heltec-monitor/{spec,plan,tasks}.md", "size": 24, "color": BLUE, "bold": True},
        "Every stage writes plain Markdown files into the repository -- they are committed to git like any other source file.",
        "That's the opposite of a chat conversation, which lives in one tool, is easy to lose, and is hard for a second "
        "person (or a second AI agent) to pick up later.",
        "Practical payoff: you can close the chat, switch from Claude Code to Codex, or come back to the project a month "
        "later, open spec.md, and see exactly what was decided and why -- without reconstructing it from memory.",
    ], size=21)
    add_note(s, ("This is a good moment to actually open specs/001-heltec-monitor/spec.md in the editor if you have it up, "
                 "even just to scroll through it -- seeing a real, readable Markdown file (not code, not JSON) tends to "
                 "de-mystify the whole idea for a novice audience."))

    # ---------- Slide 12: who does what ----------
    s = add_slide(prs)
    add_title(s, "Who Does What")
    add_image(s, "diagram-tool-relationship-en.png", Inches(2.0), Inches(1.2), height=Inches(6.0), en=True)
    add_note(s, ("Say this explicitly, it's the most common point of confusion for newcomers: Spec Kit is not a coding "
                 "agent and does not write code. Claude Code or Codex are the agents that actually read the spec/plan/tasks "
                 "files and write the firmware. The IDE (VS Code, CLion/JetBrains) is just the human's workspace for "
                 "reading and editing files alongside the agent. So the stack is: IDE (human) + coding agent (does the work) "
                 "+ Spec Kit (the structured process the agent follows) -- three separate, replaceable layers, not one product."))

    # ---------- Slide 13: same repo two agents ----------
    s = add_slide(prs)
    add_title(s, "Same Repo, Two Agents")
    add_bullets(s, [
        {"text": "Claude Code  →  /speckit-specify   (.claude/skills/)", "size": 22, "color": BLUE},
        {"text": "Codex  →  $speckit-specify   (.agents/skills/)", "size": 22, "color": AMBER},
        "Same command, same underlying files, same result -- only the invocation syntax differs because each agent "
        "has its own convention for triggering a custom command.",
        "This isn't a theoretical claim -- this exact repository has both integrations installed side by side, and "
        "either agent can pick up the work where the other left off.",
    ], top=Inches(1.55), size=20)
    add_missing_visual_placeholder(s, "Claude Code + Codex session (same repo)", Inches(0.8), Inches(4.3), SW - Inches(1.6), Inches(2.1))
    add_note(s, ("Live screenshots #6-7 on the checklist would go here. If you have a live terminal available, it's worth "
                 "actually running /speckit-specify in one agent and $speckit-specify in the other against this repo to "
                 "show it's the same underlying skill, just a different trigger syntax per agent."))

    # ---------- Slide 14: VS Code briefly ----------
    s = add_slide(prs)
    add_title(s, "VS Code, Briefly")
    add_bullets(s, [
        "Two VS Code extensions do all the real work here: PlatformIO IDE (builds and flashes the firmware, manages "
        "the ESP32 toolchain) and C/C++ (syntax highlighting and navigation for the firmware source).",
        "Everything else in this workshop -- Spec Kit's commands, Claude Code, Codex -- works the same way regardless "
        "of editor.",
        "If you use JetBrains/CLion instead: same repository, same files, same Spec Kit commands, just a different "
        "terminal and a different set of keyboard shortcuts.",
    ], size=21)
    add_note(s, ("Keep this brief -- the point is that the editor is the least important choice in this whole workflow. "
                 "Don't get pulled into an extensions debate; two extensions is the whole list."))

    # ---------- Slide 15: comparison table ----------
    s = add_slide(prs)
    add_title(s, "Direct Prompting vs. Spec Kit")
    subtitle = s.shapes.add_textbox(Inches(0.8), Inches(1.05), SW - Inches(1.6), Inches(0.5))
    stf = subtitle.text_frame
    stf.word_wrap = True
    sp = stf.paragraphs[0]
    sr = sp.add_run()
    sr.text = "Same underlying agent, same target hardware -- what changes is where each of these things lives:"
    sr.font.size = Pt(18)
    sr.font.italic = True
    sr.font.name = FONT
    sr.font.color.rgb = SLATE
    rows = [
        ("Requirements", "Live in chat history", "Live as repository files"),
        ("Clarifications", "Agent assumes on its own", "Explicit clarification stage"),
        ("Traceability", "Low", "High"),
        ("Repeatability", "Low-to-medium", "High"),
    ]
    top = Inches(1.7)
    for topic, direct, spec in rows:
        box = s.shapes.add_textbox(Inches(0.8), top, SW - Inches(1.6), Inches(0.7))
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = topic
        r.font.bold = True
        r.font.size = Pt(20)
        r.font.name = "Courier New"
        r.font.color.rgb = BLUE
        r2 = p.add_run()
        r2.text = f"   —   {direct}   →   {spec}"
        r2.font.size = Pt(20)
        r2.font.name = FONT
        r2.font.color.rgb = SLATE
        top += Inches(0.85)
    add_note(s, ("Traceability here means: can you point to the exact moment and reason a requirement was decided? "
                 "Repeatability means: if you handed this same spec to a different agent, or ran the process again, "
                 "would you land on roughly the same result? Both are naturally low with a single ad-hoc prompt because "
                 "nothing was written down -- and naturally higher with Spec Kit because the requirements are files, not memory."))

    # ---------- Slide 16: alternatives ----------
    s = add_slide(prs)
    add_title(s, 'And Why Not Just "Another Framework"?')
    add_bullets(s, [
        "Spec Kit is not the only tool in this space -- it's worth knowing it's a design point on a spectrum, not "
        "the only option.",
        {"text": "OpenSpec", "bold": True, "color": BLUE},
        "covers similar territory -- write specs before code -- with its own template and command conventions.",
        {"text": "BMAD (Breakthrough Method for Agile AI-Driven Development)", "bold": True, "color": AMBER},
        "goes further: multiple defined AI roles (analyst, architect, developer, QA) handing work off to each other, "
        "which adds real structure but also real overhead for a small project.",
        {"text": "Spec Kit deliberately sits in the middle: more structure than a bare prompt, far less ceremony than "
         "a multi-role framework -- which is why it fits a small embedded-firmware example like this one.", "bold": True},
    ], size=19)
    add_note(s, ("Not a framework survey -- don't spend more than a minute here, this isn't the point of the workshop. "
                 "The only message worth landing: this is a spectrum (no process -> Spec Kit -> heavier multi-agent "
                 "frameworks), and the right amount of process depends on project size and team size."))

    # ---------- Slide 17: hardware verified ----------
    s = add_slide(prs)
    add_title(s, "The Hardware, Verified")
    add_bullets(s, [
        "The board we're actually building for: a Heltec WiFi Kit V3, which is an ESP32-S3 microcontroller with a "
        "built-in small OLED display, plus an external BME280 sensor (temperature/humidity/pressure) wired to it over I2C.",
        {"text": "The board has no built-in environmental sensor -- so \"which sensor\" from slide 3 was never a "
         "technical detail, it was a real product decision someone had to make before any code could be correct.",
         "bold": True, "color": RED},
        "One surprising, easy-to-get-wrong technical detail: on this specific board, the built-in display's I2C pins "
        "are GPIO 17/18, not the ESP32's usual default I2C pins (21/22) -- get this wrong and the display simply "
        "stays blank with no error message.",
    ], size=20)
    add_note(s, ("This slide exists to establish real hardware credibility before we compare the two build approaches -- "
                 "everything from here on is grounded in an actual physical board, not a toy example."))

    # ---------- Slide 18: Stage A ----------
    s = add_slide(prs)
    add_title(s, "Stage A: Prompt Only")
    add_bullets(s, [
        {"text": "The point of this comparison: implicit assumption vs. explicit decision -- not \"bad code vs. good code.\"", "bold": True, "size": 22, "color": BLUE},
        "To keep the comparison fair, the hardware wiring (I2C pins, the Vext power-enable sequence) is correct in "
        "both the prompt-only version and the spec-driven version -- wiring mistakes are not the story here.",
        "What genuinely differs is everything the original prompt never specified: exactly which sensor to use, the "
        "precise numeric threshold, and whether the warning needs any tolerance band (hysteresis) around that threshold.",
        {"text": "The clearest example: the prompt-only version has no hysteresis at all. That is not a coding bug -- "
         "the code does exactly what a reasonable reading of the prompt implies. It's the direct result of a "
         "requirement that was simply never stated.", "italic": True},
    ], size=19)
    add_note(s, ("Visual: examples/prompt-only/naive_monitor.ino. If you have it open, scroll to the threshold check and "
                 "point out there is exactly one comparison (value > 30) with no second condition for clearing the warning -- "
                 "that single missing 'else' branch is the whole hysteresis story, and it's coming up in detail on slide 20."))

    # ---------- Slide 19: Specify + Clarify ----------
    s = add_slide(prs)
    add_title(s, "Stage B-C: Specify + Clarify")
    add_bullets(s, [
        "specify writes down what the product should do, in plain language, without touching code yet -- essentially "
        "a first draft of spec.md.",
        "clarify then asks the human targeted questions about exactly the gaps from slide 3, recording each answer "
        "directly into the spec. Below is the real transcript:",
    ], size=19, top=Inches(1.2), height=Inches(1.5))
    add_image(s, "code-spec-clarifications.png", Inches(0.9), Inches(3.05), width=Inches(11.0))
    add_note(s, ("This is the real clarify transcript from this project, not a mockup. Point out that these are exactly "
                 "the kind of questions a careful human reviewer would ask -- the agent is just asking them earlier, "
                 "before writing any code, and recording the answers so they're never lost."))

    # ---------- Slide 20: Hysteresis ----------
    s = add_slide(prs)
    add_title(s, "Hysteresis: The Clearest Example")
    add_image(s, "diagram-hysteresis-en.png", Inches(0.6), Inches(1.3), width=SW - Inches(1.2), en=True)
    add_note(s, ("Walk through the diagram left to right: temperature crosses 30°C, WARNING turns on. Without a tolerance "
                 "band, the moment temperature drops back to 29.9°C the display would flip straight back to OK, then back "
                 "to WARNING at the next tiny fluctuation -- flickering on every crossing of a single number. The band "
                 "(here, 28-30°C) means once WARNING is on, it *stays* on anywhere inside the band, and only clears once "
                 "the temperature drops below the lower edge (28°C). This is not a programming problem to be debugged -- "
                 "it is a product decision (how much tolerance is acceptable) that had to be made before a single line "
                 "of the state machine was written, which is exactly the kind of decision the clarify stage exists to surface."))

    # ---------- Slide 21: Plan + Tasks ----------
    s = add_slide(prs)
    add_title(s, "Stage D-E: Plan + Tasks")
    add_image(s, "diagram-architecture-en.png", Inches(0.6), Inches(1.5), width=SW - Inches(1.2), en=True)
    add_note(s, ("plan turns the now-clarified requirements into a concrete technical approach: which board, which "
                 "libraries, and critically, an architecture split into three separable pieces -- a sensor adapter, "
                 "pure decision logic with zero hardware dependencies, and an OLED/Serial reporter. tasks then breaks "
                 "that plan into small, ordered, checkable steps an agent (or a human) can execute one at a time. The "
                 "architecture split shown here is what makes the next slide's automated testing possible: because the "
                 "decision logic touches no hardware, it can be tested on a laptop with no Heltec board plugged in at all. "
                 "If you want to also show the raw files, screenshots #10-11 on the checklist are plan.md and tasks.md themselves."))

    # ---------- Slide 22: Analyze catch ----------
    s = add_slide(prs)
    add_title(s, "⭐ Stage F: Analyze Finds a Real Contradiction", size=28)
    add_image(s, "diagram-analyze-catch-en.png", Inches(2.6), Inches(1.15), height=Inches(6.1), en=True)
    add_note(s, ("The most important slide in the whole talk -- do not rush through it. Walk through each of the five "
                 "boxes: (1) during clarify, we decided the warning should stay on inside the hysteresis band; "
                 "(2) but a separate success criterion (SC-004), written earlier, still described the old, simpler "
                 "on/off behavior -- nobody noticed the two now disagreed; (3) /speckit-analyze, which cross-checks "
                 "spec/plan/tasks against each other automatically, caught that contradiction; (4) the spec was corrected "
                 "on the spot; (5) implementation only began after the documents agreed with each other. This is not a "
                 "made-up example built for this talk -- it genuinely happened while building this exact project, and the "
                 "full record is preserved in specs/001-heltec-monitor/analysis-report.md. If you have a terminal, show it "
                 "live: git show b91cd94 -- specs/001-heltec-monitor/spec.md reproduces the exact diff."))

    # ---------- Slide 22b: Analyze message ----------
    s = add_slide(prs, bg=NAVY)
    box = s.shapes.add_textbox(Inches(1), Inches(2.2), SW - Inches(2), Inches(2.6))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "/speckit-analyze didn't find a syntax problem or a code bug."
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = FONT
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = "It found that our own requirements contradicted each other -- before a single line of code was written."
    r2.font.size = Pt(26)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0xFC, 0xD3, 0x4D)
    r2.font.name = FONT
    add_image(s, "code-analyze-diff.png", Inches(1.5), Inches(4.5), width=Inches(10.3))
    add_note(s, ("The strongest demonstration of Spec Kit's value in the entire talk -- if the audience remembers one "
                 "concrete moment from this workshop, it should be this one. The image below is the real diff: the old "
                 "wording of SC-004 on the left/red, the corrected wording on the right/green, showing the success "
                 "criterion updated to match the hysteresis decision from clarify. Emphasize: no code had been written yet "
                 "when this was caught -- fixing a contradiction between two Markdown documents costs a few seconds; "
                 "fixing the same contradiction after it had already become two conflicting pieces of firmware behavior "
                 "would have cost far more, and might not have been caught at all without a hardware test that exercises "
                 "that exact edge case."))

    # ---------- Slide 23: Implement ----------
    s = add_slide(prs)
    add_title(s, "Stage G: Implement")
    add_image(s, "code-monitor-logic.png", Inches(0.9), Inches(1.25), width=Inches(10.8))
    add_image(s, "terminal-pio-test.png", Inches(0.9), Inches(5.15), width=Inches(4.6))
    box = s.shapes.add_textbox(Inches(5.8), Inches(5.35), Inches(6.6), Inches(1.8))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = "monitor_logic is fully tested with zero hardware"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.name = FONT
    r.font.color.rgb = GREEN
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.LEFT
    r2 = p2.add_run()
    r2.text = "(pio test -e native, 11/11 passed)"
    r2.font.size = Pt(18)
    r2.font.name = "Courier New"
    r2.font.color.rgb = GREEN
    add_note(s, ("implement is the stage that finally writes the actual firmware code, following plan.md and tasks.md "
                 "in order. Because the decision logic (monitor_logic, shown above) was designed with zero hardware "
                 "dependencies back in the plan stage, it can be exercised by an automated test suite running natively "
                 "on a laptop -- no Heltec board, no serial cable, nothing physical required. The panel on the bottom-left "
                 "is the real, unedited output of that test run: 11 out of 11 tests passing. This is why we can already "
                 "have high confidence in the decision logic itself before ever touching real hardware -- what's still "
                 "unverified is only the physical wiring, sensor, and display, which is exactly what the next two slides "
                 "are about."))

    # ---------- Slide 24: Live demo (PENDING) ----------
    s = add_slide(prs)
    add_title(s, "Live Demo")
    add_bullets(s, [
        "Normal temperature → OK",
        "Warming above 30°C → WARNING",
        {"text": "Partial cooling (28-30°C) → stays WARNING (the single most important point)", "bold": True, "color": RED},
        "Cooling below 28°C → back to OK",
        "If there's time: disconnect the sensor → SENSOR_ERROR",
    ], top=Inches(1.5), size=20)
    add_missing_visual_placeholder(s, "Serial output + OLED photo", Inches(0.8), Inches(4.6), SW - Inches(1.6), Inches(1.7))
    add_pending_banner(s)
    add_note(s, "Everything on this slide depends on the physical hardware test, which hasn't happened yet.")

    # ---------- Slide 25: Git checkpoints ----------
    s = add_slide(prs)
    add_title(s, "Git Checkpoints")
    add_image(s, "terminal-git-log.png", Inches(0.9), Inches(1.4), width=Inches(11.5))
    add_pending_banner(s, "Tag 09-hardware-verified does not exist yet -- pending physical test")
    add_note(s, "Every stage already exists as a tag in the repository -- the demo doesn't depend on a live AI run that could fail on stage.")

    # ---------- Slide 26: Key takeaways ----------
    s = add_slide(prs, bg=NAVY)
    add_title(s, "Five Things to Remember", color=WHITE, size=32)
    add_bullets(s, [
        {"text": "•  AI coding speed does not remove the need for clear requirements", "color": WHITE, "size": 22},
        {"text": "•  Spec Kit gives a repeatable path from idea to implementation", "color": WHITE, "size": 22},
        {"text": "•  Claude Code and Codex are the agents; Spec Kit is the process and structure", "color": WHITE, "size": 22},
        {"text": "•  The spec, plan, and tasks live in the repository -- they don't disappear into a chat", "color": WHITE, "size": 22},
        {"text": "•  The best proof: not that it generates code, but that it forces answers to important questions before the wrong code gets written", "color": RGBColor(0xFC, 0xD3, 0x4D), "size": 22, "bold": True},
    ], top=Inches(1.6))
    add_note(s, "")

    # ---------- Slide 27: Links ----------
    s = add_slide(prs)
    add_title(s, "Links and Credits")
    add_bullets(s, [
        "Spec Kit: github.com/github/spec-kit",
        "Spec Kit docs: github.github.io/spec-kit",
        "Claude Code docs: docs.claude.com/en/docs/claude-code",
        "Codex docs: developers.openai.com/codex",
        "PlatformIO: platformio.org",
        "Heltec WiFi Kit 32 (V3): heltec.org/project/wifi-kit32-v3",
        {"text": "Companion repository: (to be filled in after publishing)", "italic": True},
    ], size=20)
    add_note(s, "See presentation/slide-links.md for the full list.")

    prs.save(OUT)
    print(f"saved {OUT} with {len(prs.slides.__iter__.__self__._sldIdLst)} slides")


if __name__ == "__main__":
    main()
