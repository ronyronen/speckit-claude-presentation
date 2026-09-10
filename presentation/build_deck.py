#!/usr/bin/env python3
"""Builds presentation/speckit-workshop-draft.pptx from
presentation-outline.md's content, using real repository artifacts
(diagrams, terminal/code captures) generated into
presentation/assets/generated/. Run from the repository root:

    python3 presentation/build_deck.py

Hardware-dependent slides are explicitly marked PENDING and contain no
fabricated data -- they will be completed after checkpoint
09-hardware-verified.
"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt, Emu

ASSETS = "presentation/assets/generated"
OUT = "presentation/speckit-workshop-draft.pptx"

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


def set_rtl(paragraph):
    """Mark a paragraph right-to-left at the XML level (belt-and-braces;
    PowerPoint/LibreOffice already bidi-render Hebrew correctly, but this
    keeps cursor/selection behavior correct if edited later)."""
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set("rtl", "1")


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
    p.alignment = PP_ALIGN.RIGHT
    set_rtl(p)
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
        p.alignment = PP_ALIGN.RIGHT
        set_rtl(p)
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


def add_pending_banner(slide, text="ממתין לאימות חומרה פיזי (checkpoint 09-hardware-verified)"):
    box = slide.shapes.add_textbox(Inches(0.6), SH - Inches(0.85), SW - Inches(1.2), Inches(0.55))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_rtl(p)
    r = p.add_run()
    r.text = "⏳ " + text
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.italic = True
    r.font.name = FONT
    r.font.color.rgb = AMBER
    fill = box.fill if hasattr(box, "fill") else None
    # background rectangle behind the banner
    rect = slide.shapes.add_shape(1, Inches(0.5), SH - Inches(0.95), SW - Inches(1.0), Inches(0.7))
    rect.fill.solid()
    rect.fill.fore_color.rgb = RGBColor(0xFE, 0xF3, 0xC7)
    rect.line.color.rgb = AMBER
    rect.line.width = Pt(1.5)
    rect.shadow.inherit = False
    # move rect behind text by reordering: send rect to just above background (index it before box)
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
    rect.line.dash_style = 4  # dashed if supported
    tf = rect.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_rtl(p)
    r = p.add_run()
    r.text = "\U0001F4F7 " + label
    r.font.size = Pt(16)
    r.font.italic = True
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    set_rtl(p2)
    r2 = p2.add_run()
    r2.text = "(מסך אמיתי / צילום מסך חסר -- ראו screenshot-checklist.md)"
    r2.font.size = Pt(13)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    return rect


def add_image(slide, path, left, top, width=None, height=None):
    full = os.path.join(ASSETS, path) if not path.startswith(ASSETS) else path
    return slide.shapes.add_picture(full, left, top, width=width, height=height)


def add_source_note(slide, text, top=None):
    top = top or (SH - Inches(0.5))
    box = slide.shapes.add_textbox(Inches(0.5), top, SW - Inches(1.0), Inches(0.4))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    r.font.size = Pt(12)
    r.font.italic = True
    r.font.name = "Courier New"
    r.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)


def section_slide(prs, number_range, title_he, subtitle=None):
    slide = add_slide(prs, bg=SECTION_BG)
    box = slide.shapes.add_textbox(Inches(1), Inches(2.6), SW - Inches(2), Inches(1.2))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_rtl(p)
    r = p.add_run()
    r.text = title_he
    r.font.size = Pt(40)
    r.font.bold = True
    r.font.name = FONT
    r.font.color.rgb = WHITE

    box2 = slide.shapes.add_textbox(Inches(1), Inches(3.9), SW - Inches(2), Inches(0.8))
    tf2 = box2.text_frame
    p2 = tf2.paragraphs[0]
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = number_range
    r2.font.size = Pt(22)
    r2.font.name = "Courier New"
    r2.font.color.rgb = RGBColor(0xA5, 0xB4, 0xFC)

    if subtitle:
        box3 = slide.shapes.add_textbox(Inches(1.5), Inches(4.8), SW - Inches(3), Inches(1.0))
        tf3 = box3.text_frame
        tf3.word_wrap = True
        p3 = tf3.paragraphs[0]
        p3.alignment = PP_ALIGN.CENTER
        set_rtl(p3)
        r3 = p3.add_run()
        r3.text = subtitle
        r3.font.size = Pt(18)
        r3.font.italic = True
        r3.font.name = FONT
        r3.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)
    return slide


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
    set_rtl(p)
    r = p.add_run()
    r.text = "מ-Prompt ועד מוצר"
    r.font.size = Pt(48)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = FONT
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    set_rtl(p2)
    r2 = p2.add_run()
    r2.text = "Spec-Driven Development עם GitHub Spec Kit"
    r2.font.size = Pt(28)
    r2.font.color.rgb = RGBColor(0xA5, 0xB4, 0xFC)
    r2.font.name = FONT

    box2 = s.shapes.add_textbox(Inches(1), Inches(4.3), SW - Inches(2), Inches(0.8))
    tf2 = box2.text_frame
    p3 = tf2.paragraphs[0]
    p3.alignment = PP_ALIGN.CENTER
    set_rtl(p3)
    r3 = p3.add_run()
    r3.text = "דוגמה אמיתית על Heltec WiFi Kit V3"
    r3.font.size = Pt(20)
    r3.font.italic = True
    r3.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)
    r3.font.name = FONT
    add_note(s, "לפתוח בשאלה לקהל: מי כבר ביקש מ-AI לכתוב קוד ישירות מפרומפט?")

    # ---------- Slide 2: The vague prompt ----------
    s = add_slide(prs)
    add_title(s, "הפרומפט המעורפל")
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
    rect = s.shapes.add_shape(1, Inches(1.0), Inches(1.7), SW - Inches(2.0), Inches(1.8))
    rect.fill.solid()
    rect.fill.fore_color.rgb = LIGHT_BG
    rect.line.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
    spTree = s.shapes._spTree
    spTree.remove(rect._element)
    spTree.insert(2, rect._element)
    box3 = s.shapes.add_textbox(Inches(1.2), Inches(4.2), SW - Inches(2.4), Inches(1))
    tf3 = box3.text_frame
    tf3.word_wrap = True
    p3 = tf3.paragraphs[0]
    p3.alignment = PP_ALIGN.CENTER
    set_rtl(p3)
    r3 = p3.add_run()
    r3.text = "❓ האם יש כאן מספיק מידע כדי לבנות את המוצר הנכון?"
    r3.font.size = Pt(28)
    r3.font.bold = True
    r3.font.color.rgb = RED
    r3.font.name = FONT
    add_note(s, "שאלה פתוחה לקהל -- לתת רגע לחשוב לפני שממשיכים.")

    # ---------- Slide 3: Open questions ----------
    s = add_slide(prs)
    add_title(s, "כל מה שהפרומפט לא ענה עליו")
    add_bullets(s, [
        "איזה חיישן?",
        "כל כמה זמן דוגמים?",
        "מה זה בדיוק \"גבוה מדי\"?",
        "מה קורה בדיוק בסף?",
        "מתי האזהרה נכבית?",
        "מה קורה כשהחיישן נכשל?",
        "מה מוצג במסך בזמן תקלה?",
        "מה נכתב ל-Serial?",
    ], size=22)
    add_note(s, "אפשר להראות כאן את examples/prompt-only/naive_monitor.ino בקצרה.")

    # ---------- Slide 4: Core message ----------
    s = add_slide(prs, bg=NAVY)
    box = s.shapes.add_textbox(Inches(1), Inches(2.6), SW - Inches(2), Inches(2.2))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_rtl(p)
    r = p.add_run()
    r.text = "הבעיה היא בדרך כלל לא שה-AI לא יודע לכתוב קוד."
    r.font.size = Pt(30)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = FONT
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    set_rtl(p2)
    r2 = p2.add_run()
    r2.text = "הבעיה היא שהתנהגות המוצר לא הוגדרה מספיק."
    r2.font.size = Pt(30)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0xFC, 0xD3, 0x4D)
    r2.font.name = FONT
    add_note(s, "זה המשפט שהקהל צריך לזכור מהסדנה כולה. לעצור רגע אחרי השקף הזה.")

    # ---------- Slide 5: Prompt loop ----------
    s = add_slide(prs)
    add_title(s, "מ-Prompt ללולאה אינסופית")
    add_image(s, "diagram-prompt-vs-spec.png", Inches(0.5), Inches(1.3), width=SW - Inches(1.0))
    add_note(s, "להתמקד בחצי העליון של הדיאגרמה כרגע. כל 'תיקון' הוא החלטת מוצר שמתקבלת אחרי שכבר יש קוד שסותר אותה.")

    # ---------- Slide 6: Spec-driven alternative ----------
    s = add_slide(prs)
    add_title(s, "האלטרנטיבה: תהליך מונחה-מפרט")
    add_image(s, "diagram-prompt-vs-spec.png", Inches(0.5), Inches(1.3), width=SW - Inches(1.0))
    add_note(s, "עכשיו להתמקד בחצי התחתון. ההבדל הוא לא 'יותר בירוקרטיה' -- זה להזיז את ההחלטות למקום שבו הן זולות לקבל.")

    # ---------- Slide 7: What each stage catches ----------
    s = add_slide(prs)
    add_title(s, "מה כל שלב תופס")
    rows = [
        ("Specification", "לא סיכמנו מה זה עושה"),
        ("Clarify", "סיכמנו את המסלול הראשי, לא את הקצוות"),
        ("Plan", "סיכמנו מה, לא איך"),
        ("Analyze", "שני מסמכים שלנו סותרים אחד את השני"),
    ]
    top = Inches(1.6)
    for en, he in rows:
        box = s.shapes.add_textbox(Inches(0.8), top, SW - Inches(1.6), Inches(0.8))
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT
        set_rtl(p)
        r = p.add_run()
        r.text = f"{he}    ←    "
        r.font.size = Pt(24)
        r.font.name = FONT
        r.font.color.rgb = SLATE
        r2 = p.add_run()
        r2.text = en
        r2.font.size = Pt(24)
        r2.font.bold = True
        r2.font.name = "Courier New"
        r2.font.color.rgb = BLUE
        top += Inches(1.0)

    # ---------- Slide 8: Spec Kit definition ----------
    s = add_slide(prs)
    add_title(s, "מה זה GitHub Spec Kit")
    add_bullets(s, [
        "Spec Kit = כלי CLI (specify) + סט Skills/Commands לסוכן קידוד",
        "לא כותב קוד בעצמו -- מבנה את *התהליך* שמוביל לכתיבת הקוד",
    ], size=24)
    add_missing_visual_placeholder(s, "Spec Kit website + GitHub repo", Inches(0.8), Inches(3.2), SW - Inches(1.6), Inches(2.8))
    add_note(s, "screenshots #1-2 מהצ'קליסט.")

    # ---------- Slide 9: Installation ----------
    s = add_slide(prs)
    add_title(s, "התקנה")
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
    add_note(s, "זו התוצאה האמיתית מהאתחול של הריפו הזה עצמו.")

    # ---------- Slide 10: 7-stage workflow ----------
    s = add_slide(prs)
    add_title(s, "תהליך העבודה בשבעה שלבים")
    add_image(s, "diagram-speckit-workflow.png", Inches(0.6), Inches(1.6), width=SW - Inches(1.2))
    add_note(s, "לא לצלול לתחביר הפקודות -- המטרה היא המודל המנטלי.")

    # ---------- Slide 11: Real files ----------
    s = add_slide(prs)
    add_title(s, "התוצר: קבצים אמיתיים ברפוזיטורי")
    add_bullets(s, [
        {"text": "specs/001-heltec-monitor/{spec,plan,tasks}.md", "size": 24, "color": BLUE, "bold": True},
        "לא שיחת צ'אט שנעלמת",
        "זה מה שמאפשר להחליף סוכן, לחזור אחרי חודש, ולראות בדיוק למה התקבלה כל החלטה",
    ], size=22)
    add_note(s, "")

    # ---------- Slide 12: who does what ----------
    s = add_slide(prs)
    add_title(s, "מי עושה מה")
    add_image(s, "diagram-tool-relationship.png", Inches(2.0), Inches(1.2), height=Inches(6.0))
    add_note(s, "'Spec Kit הוא לא סוכן הקידוד. Claude Code או Codex מבצעים את העבודה. ה-IDE הוא סביבת העבודה האנושית.'")

    # ---------- Slide 13: same repo two agents ----------
    s = add_slide(prs)
    add_title(s, "אותו ריפו, שני סוכנים")
    add_bullets(s, [
        {"text": "Claude Code  ←  /speckit-specify   (.claude/skills/)", "size": 22, "color": BLUE},
        {"text": "Codex  ←  $speckit-specify   (.agents/skills/)", "size": 22, "color": AMBER},
        "זה לא תיאוריה -- הריפו הזה מותקן עם שני האינטגרציות במקביל",
    ], top=Inches(1.6))
    add_missing_visual_placeholder(s, "Claude Code + Codex session (same repo)", Inches(0.8), Inches(4.0), SW - Inches(1.6), Inches(2.4))
    add_note(s, "screenshots #6-7.")

    # ---------- Slide 14: VS Code briefly ----------
    s = add_slide(prs)
    add_title(s, "VS Code בקצרה")
    add_bullets(s, [
        "Extensions: PlatformIO IDE, C/C++ -- כל אחד עם סיבה, לא רשימה ארוכה",
        "JetBrains/CLion: אותם קבצים, טרמינל אחר",
    ], size=24)
    add_note(s, "")

    # ---------- Slide 15: comparison table ----------
    s = add_slide(prs)
    add_title(s, "פרומפט ישיר מול Spec Kit")
    rows = [
        ("Requirements", "בשיחת צ'אט", "כקבצים ברפוזיטורי"),
        ("Clarifications", "הסוכן מניח לבד", "שלב הבהרה מפורש"),
        ("Traceability", "נמוכה", "גבוהה"),
        ("Repeatability", "נמוכה-בינונית", "גבוהה"),
    ]
    top = Inches(1.7)
    headers = ["Spec Kit", "פרומפט ישיר", ""]
    hbox = s.shapes.add_textbox(Inches(0.8), Inches(1.2), SW - Inches(1.6), Inches(0.5))
    htf = hbox.text_frame
    hp = htf.paragraphs[0]
    hp.alignment = PP_ALIGN.RIGHT
    set_rtl(hp)
    hr = hp.add_run()
    hr.text = "נושא".ljust(2) + "        פרומפט ישיר              Spec Kit"
    hr.font.bold = True
    hr.font.size = Pt(18)
    hr.font.color.rgb = NAVY
    for topic, direct, spec in rows:
        box = s.shapes.add_textbox(Inches(0.8), top, SW - Inches(1.6), Inches(0.7))
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT
        set_rtl(p)
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
    add_note(s, "")

    # ---------- Slide 16: alternatives ----------
    s = add_slide(prs)
    add_title(s, "ולמה לא רק \"עוד framework\"?")
    add_bullets(s, [
        "OpenSpec -- טריטוריה דומה, template/command set שונה",
        "BMAD -- יותר roles ו-handoffs, יותר overhead",
        "Spec Kit נמצא בין פרומפט חופשי לתהליכי multi-agent כבדים",
    ], size=22)
    add_note(s, "לא סקירת frameworks -- זו לא המטרה של הסדנה.")

    # ---------- Slide 17: hardware verified ----------
    s = add_slide(prs)
    add_title(s, "החומרה, מאומתת")
    add_bullets(s, [
        "Heltec WiFi Kit V3 (ESP32-S3), OLED מובנה, BME280 חיצוני",
        {"text": "אין חיישן סביבתי מובנה בלוח -- זו כבר החלטת מוצר", "bold": True, "color": RED},
        "פרט טכני מפתיע: פיני ה-I2C של המסך הם 17/18, לא ברירת המחדל של ESP32 (21/22)",
    ], size=22)
    add_note(s, "")

    # ---------- Slide 18: Stage A ----------
    s = add_slide(prs)
    add_title(s, "Stage A: פרומפט בלבד")
    add_bullets(s, [
        {"text": "המסר: הנחה משתמעת מול החלטה מפורשת", "bold": True, "size": 24, "color": BLUE},
        "חיווט החומרה (I2C, Vext) נכון בשתי הגרסאות",
        "מה שחסר: איזה חיישן, מה הסף המדויק, האם צריך היסטרזיס",
        {"text": "דוגמה מרכזית: אין היסטרזיס -- לא \"באג\", תוצאה של דרישה שמעולם לא נוסחה", "italic": True},
    ], size=20)
    add_note(s, "ויזואל: examples/prompt-only/naive_monitor.ino")

    # ---------- Slide 19: Specify + Clarify ----------
    s = add_slide(prs)
    add_title(s, "Stage B-C: Specify + Clarify")
    add_bullets(s, [
        "4 השאלות שנשאלו בפועל:",
        "קצב דגימה • גבולות סף מדויקים • debounce לתקלה • תוכן המסך בזמן תקלה",
    ], size=22)
    add_image(s, "code-spec-clarifications.png", Inches(0.9), Inches(3.0), width=Inches(11.5))
    add_note(s, "")

    # ---------- Slide 20: Hysteresis ----------
    s = add_slide(prs)
    add_title(s, "היסטרזיס: הדוגמה הכי ברורה")
    add_image(s, "diagram-hysteresis.png", Inches(0.6), Inches(1.3), width=SW - Inches(1.2))
    add_note(s, "זו לא בעיית תכנות. זו החלטת מוצר שהיתה חייבת להתקבל *לפני* כתיבת קוד.")

    # ---------- Slide 21: Plan + Tasks ----------
    s = add_slide(prs)
    add_title(s, "Stage D-E: Plan + Tasks")
    add_image(s, "diagram-architecture.png", Inches(0.6), Inches(1.5), width=SW - Inches(1.2))
    add_note(s, "screenshots #10-11 (plan.md, tasks.md) אם רוצים להראות גם את הקבצים עצמם.")

    # ---------- Slide 22: Analyze catch ----------
    s = add_slide(prs)
    add_title(s, "⭐ Stage F: Analyze מוצא סתירה אמיתית", size=28)
    add_image(s, "diagram-analyze-catch.png", Inches(2.6), Inches(1.15), height=Inches(6.1))
    add_note(s, ("שקף חשוב ביותר -- לא להעביר במהירות. זו לא דוגמה מומצאת לצורך ההרצאה -- "
                 "זה קרה ממש בבניית הפרויקט הזה. אפשר להראות live: git show b91cd94 -- specs/001-heltec-monitor/spec.md"))

    # ---------- Slide 22b: Analyze message ----------
    s = add_slide(prs, bg=NAVY)
    box = s.shapes.add_textbox(Inches(1), Inches(2.2), SW - Inches(2), Inches(2.6))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_rtl(p)
    r = p.add_run()
    r.text = "/speckit-analyze לא מצא בעיית תחביר ולא באג בקוד."
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = FONT
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    set_rtl(p2)
    r2 = p2.add_run()
    r2.text = "הוא מצא שהדרישות שלנו עצמן סתרו זו את זו -- לפני שנכתבה שורת קוד אחת."
    r2.font.size = Pt(28)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(0xFC, 0xD3, 0x4D)
    r2.font.name = FONT
    add_image(s, "code-analyze-diff.png", Inches(1.5), Inches(4.5), width=Inches(10.3))
    add_note(s, "ההוכחה הכי חזקה לערך של Spec Kit בכל ההרצאה.")

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
    p.alignment = PP_ALIGN.RIGHT
    set_rtl(p)
    r = p.add_run()
    r.text = "monitor_logic נבדק לגמרי בלי חומרה"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.name = FONT
    r.font.color.rgb = GREEN
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.RIGHT
    set_rtl(p2)
    r2 = p2.add_run()
    r2.text = "(pio test -e native, 11/11 עברו)"
    r2.font.size = Pt(18)
    r2.font.name = "Courier New"
    r2.font.color.rgb = GREEN
    add_note(s, "")

    # ---------- Slide 24: Live demo (PENDING) ----------
    s = add_slide(prs)
    add_title(s, "הדגמה חיה")
    add_bullets(s, [
        "טמפרטורה רגילה → OK",
        "חימום מעל 30°C → WARNING",
        {"text": "קירור חלקי (28-30°C) ← נשאר WARNING (הנקודה החשובה ביותר)", "bold": True, "color": RED},
        "קירור מתחת ל-28°C → חזרה ל-OK",
        "אם יש זמן: ניתוק החיישן → SENSOR_ERROR",
    ], top=Inches(1.5), size=20)
    add_missing_visual_placeholder(s, "Serial output + OLED photo", Inches(0.8), Inches(4.6), SW - Inches(1.6), Inches(1.7))
    add_pending_banner(s)
    add_note(s, "כל התוכן כאן תלוי בבדיקת החומרה הפיזית שטרם בוצעה.")

    # ---------- Slide 25: Git checkpoints ----------
    s = add_slide(prs)
    add_title(s, "Git checkpoints")
    add_image(s, "terminal-git-log.png", Inches(0.9), Inches(1.4), width=Inches(11.5))
    add_pending_banner(s, "תג 09-hardware-verified עדיין לא נוצר -- ממתין לבדיקה פיזית")
    add_note(s, "כל שלב כבר קיים כ-tag ברפוזיטורי -- ההדגמה לא תלויה בהרצת AI חיה שעלולה להיכשל על הבמה.")

    # ---------- Slide 26: Key takeaways ----------
    s = add_slide(prs, bg=NAVY)
    add_title(s, "חמש נקודות לזכור", color=WHITE, size=32)
    add_bullets(s, [
        {"text": "•  מהירות הקידוד של ה-AI לא מבטלת את הצורך בדרישות ברורות", "color": WHITE, "size": 22},
        {"text": "•  Spec Kit נותן מסלול חוזר מרעיון למימוש", "color": WHITE, "size": 22},
        {"text": "•  Claude Code ו-Codex הם הסוכנים; Spec Kit הוא התהליך והמבנה", "color": WHITE, "size": 22},
        {"text": "•  המפרט, התוכנית והמשימות חיים ברפוזיטורי -- לא נעלמים בתוך צ'אט", "color": WHITE, "size": 22},
        {"text": "•  ההוכחה הכי טובה: לא שהוא מייצר קוד, אלא שהוא מכריח לענות על שאלות לפני שנכתב הקוד הלא נכון", "color": RGBColor(0xFC, 0xD3, 0x4D), "size": 22, "bold": True},
    ], top=Inches(1.6))
    add_note(s, "")

    # ---------- Slide 27: Links ----------
    s = add_slide(prs)
    add_title(s, "קישורים ותודות")
    add_bullets(s, [
        "Spec Kit: github.com/github/spec-kit",
        "Spec Kit docs: github.github.io/spec-kit",
        "Claude Code docs: docs.claude.com/en/docs/claude-code",
        "Codex docs: developers.openai.com/codex",
        "PlatformIO: platformio.org",
        "Heltec WiFi Kit 32 (V3): heltec.org/project/wifi-kit32-v3",
        {"text": "הריפו הנלווה: (למלא לאחר פרסום)", "italic": True},
    ], size=20)
    add_note(s, "ראו presentation/slide-links.md לרשימה המלאה.")

    prs.save(OUT)
    print(f"saved {OUT} with {len(prs.slides.__iter__.__self__._sldIdLst)} slides")


if __name__ == "__main__":
    main()
