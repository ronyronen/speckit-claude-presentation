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
    add_note(s, ("לפתוח בהצבעה: מי כבר ביקש פעם מסוכן AI לקוד 'סתם לבנות X' ממשפט אחד? כמעט כולם. ההרצאה הזו עוסקת "
                 "במה שקורה אחר כך -- ובדוגמה אמיתית וקונקרטית ממערכות משובצות (מוניטור טמפרטורה על לוח Heltec מבוסס "
                 "ESP32) שנעקוב אחריה מפרומפט מעורפל ועד קושחה בדוקה, עובדת, שאומתה פיזית. לא נדרש ידע קודם ב-Spec Kit, "
                 "במערכות משובצות, ואפילו לא בסוכני AI."))

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
    add_note(s, ("לקרוא את הפרומפט בקול, לאט. הוא נשמע שלם -- יש בו חיישן, מסך, אזהרה. זו בדיוק המלכודת: הוא נשמע כמו "
                 "מפרט אבל הוא לא. לתת לקהל רגע אמיתי של שקט לפני שממשיכים לשקף 3, שם נפרק את כל מה שהמשפט הזה השאיר "
                 "בשקט לא מוחלט."))

    # ---------- Slide 3: Open questions ----------
    s = add_slide(prs)
    add_title(s, "כל מה שהפרומפט לא ענה עליו")
    add_bullets(s, [
        {"text": "סוכן קידוד עדיין חייב לענות על כל אחת מהשאלות האלה -- הוא פשוט עונה עליהן בשקט, בניחוש:", "italic": True, "size": 18},
        "איזה חיישן בפועל מחובר? (טמפרטורה בלבד? טמפרטורה + לחות? איזה צ'יפ?)",
        "כל כמה זמן צריך לדגום את הערך -- פעם בשנייה? פעם בדקה?",
        "מה בדיוק נחשב \"גבוה מדי\" -- מה הסף המספרי המדויק?",
        "מה קורה בדיוק בסביבת הסף -- האם האזהרה מהבהבת כשהערך מרפרף שם?",
        "כשהאזהרה כבר מוצגת, באיזו נקודה בדיוק היא נכבית?",
        "מה צריך לקרות אם החיישן מפסיק להגיב או מחזיר ערך שגוי?",
        "מה המסך אמור להציג בזמן שהתקלה הזו קורית?",
        "מה, אם בכלל, נכתב לקונסולת ה-Serial לצורך דיבוג?",
    ], size=19)
    add_note(s, ("כל שורה כאן היא החלטה אמיתית, ופרומפט לא מפורט לא מבטל את ההחלטה -- הוא רק מעביר אותה אל תוך הראש "
                 "של המודל, איפה שאי אפשר לראות אותה, לבדוק אותה או להסכים איתה. אפשר להראות כאן את "
                 "examples/prompt-only/naive_monitor.ino כדי להוכיח שאלה לא שאלות תיאורטיות: להצביע אילו שורות בקוד "
                 "שנוצר בפועל ענו בשקט על כל אחת מהשאלות למעלה."))

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
    add_note(s, ("זה המשפט שהקהל צריך לזכור מהסדנה כולה -- לעצור רגע אחרי שקוראים אותו בקול. מודלים מודרניים כבר "
                 "טובים מספיק בכתיבת קוד; זה כבר לא צוואר הבקבוק. צוואר הבקבוק זז מעלה בזרם, לשלב ההחלטה מה בדיוק "
                 "הקוד אמור לעשות. Spec Kit, שנציג בעוד רגע, הוא כלי שהופך את שלב קבלת ההחלטות הזה למפורש ומובנה "
                 "במקום מרומז ומדולג."))

    # ---------- Slide 5: Prompt loop ----------
    s = add_slide(prs)
    add_title(s, "מ-Prompt ללולאה אינסופית")
    add_image(s, "diagram-prompt-vs-spec.png", Inches(0.5), Inches(1.3), width=SW - Inches(1.0))
    add_note(s, ("להתמקד רק בחצי העליון של הדיאגרמה כרגע (נחזור לחצי התחתון בשקף הבא). זו הלולאה הרגילה כשמדלגים על "
                 "מפרט: פרומפט -> קוד -> שמים לב שמשהו לא בסדר -- שולחים פרומפט המשך לתיקון -> התיקון חושף או שובר "
                 "משהו אחר -> חוזר חלילה. כל תיבת 'תיקון' היא החלטת מוצר שהתקבלה *אחרי* שכבר היה קוד שסותר אותה -- "
                 "וזה הזמן היקר ביותר האפשרי לקבל את ההחלטה הזו, כי כבר יש קוד ואולי משתמש שתלוי בהתנהגות הלא נכונה."))

    # ---------- Slide 6: Spec-driven alternative ----------
    s = add_slide(prs)
    add_title(s, "האלטרנטיבה: תהליך מונחה-מפרט")
    add_image(s, "diagram-prompt-vs-spec.png", Inches(0.5), Inches(1.3), width=SW - Inches(1.0))
    add_note(s, ("עכשיו להצביע על החצי התחתון של אותה דיאגרמה. ההבדל הוא לא 'יותר ניירת' -- אותן החלטות בדיוק (איזה "
                 "חיישן, מה הסף, מה קורה בתקלה) מתקבלות פעם אחת, במכוון, בשלב הבהרה קצר, לפני שיש קוד בכלל -- במקום "
                 "אחת אחת, בטעות, אחרי שכבר יש קוד שצריך לפרק. אותו מספר החלטות בסך הכול; מה שמשתנה הוא רק *מתי* הן "
                 "מתקבלות, והתזמון הזה הוא כל הצעת הערך של הסדנה הזו."))

    # ---------- Slide 7: What each stage catches ----------
    s = add_slide(prs)
    add_title(s, "מה כל שלב תופס")
    subtitle = s.shapes.add_textbox(Inches(0.8), Inches(1.05), SW - Inches(1.6), Inches(0.5))
    stf = subtitle.text_frame
    stf.word_wrap = True
    sp = stf.paragraphs[0]
    sp.alignment = PP_ALIGN.RIGHT
    set_rtl(sp)
    sr = sp.add_run()
    sr.text = "כל שלב קיים כדי לתפוס סוג ספציפי של טעות -- לפני שהיא הופכת לקוד:"
    sr.font.size = Pt(18)
    sr.font.italic = True
    sr.font.name = FONT
    sr.font.color.rgb = SLATE

    rows = [
        ("constitution", "כלל נשבר בשקט כי אף אחד לא כתב אותו"),
        ("specify", "לא סיכמנו מה זה עושה"),
        ("clarify", "סיכמנו את המסלול הראשי, לא את הקצוות"),
        ("plan", "סיכמנו מה, לא איך -- ול'איך' יש אילוצים אמיתיים"),
        ("tasks", "אנחנו יודעים את התוכנית, לא את הסדר או התלויות"),
        ("analyze", "שני מסמכים שלנו סותרים אחד את השני בשקט"),
        ("implement", "(זה השלב היחיד שממנו פרומפט-בלבד מתחיל)"),
    ]
    top = Inches(1.75)
    row_h = Inches(0.68)
    for en, he in rows:
        box = s.shapes.add_textbox(Inches(0.8), top, SW - Inches(1.6), row_h)
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT
        set_rtl(p)
        r = p.add_run()
        r.text = f"{he}    ←    "
        r.font.size = Pt(20)
        r.font.name = FONT
        r.font.italic = en == "implement"
        r.font.color.rgb = SLATE
        r2 = p.add_run()
        r2.text = en
        r2.font.size = Pt(21)
        r2.font.bold = True
        r2.font.name = "Courier New"
        r2.font.color.rgb = BLUE
        top += row_h
    add_note(s, "לעבור בקצרה על כל שבעת השלבים כאן; ההעמקה בכל אחד מהם מגיעה בהמשך, בקטע ה-Heltec.")

    # ---------- Slide 8: Spec Kit definition ----------
    s = add_slide(prs)
    add_title(s, "מה זה GitHub Spec Kit -- ולמה הוא בכלל קיים?")
    add_bullets(s, [
        {"text": "זה כלי קוד פתוח שפרסמה GitHub עצמה (github.com/github/spec-kit) -- חינמי, לא מוצר שקונים.", "bold": True},
        "בפועל, מדובר בשני דברים: כלי שורת-פקודה קטן בשם specify, ועוד סט של Skills/Commands (פקודות ה-"
        "/speckit-... שהצגנו) שהוא מתקין אצל סוכן הקידוד שלכם -- Claude Code, Codex, או אחרים.",
        "Spec Kit לא כותב את קוד האפליקציה בעצמו, והוא גם לא מודל AI. הוא מבנה את *התהליך* שאדם וסוכן AI עוברים "
        "יחד לפני ותוך כדי כתיבת הקוד: להסכים על כללים, לכתוב דרישות, לפתור אי-בהירות, לתכנן את הגישה הטכנית, "
        "לפרק לעבודה למשימות, לבדוק הכול לסתירות, ורק אז לממש.",
        {"text": "למה GitHub בנתה את זה: ככל שסוכני קידוד AI נהיו מהירים מספיק לייצר פיצ'רים שלמים תוך שניות, "
         "צוותים גילו שהקוד כבר כמעט אף פעם לא צוואר הבקבוק -- דרישות לא ברורות או לא כתובות היו. הדפוס הזה נקרא "
         "\"פיתוח מונחה-מפרט\" (spec-driven development), ו-Spec Kit הוא הכלים של GitHub בשבילו: דרך מעשית לשמור "
         "על המהירות של סוכן AI בלי לוותר על המשמעת של לדעת מה בדיוק בונים.", "size": 18},
    ], size=20, top=Inches(1.25), height=Inches(4.7))
    add_missing_visual_placeholder(s, "Spec Kit website + GitHub repo", Inches(0.8), Inches(6.05), SW - Inches(1.6), Inches(1.1))
    add_note(s, ("זהו שקף העוגן של כל ההרצאה -- לא למהר. נקודות מפתח לומר בקול: (1) זה מ-GitHub, זה חינמי וקוד "
                 "פתוח, זו לא הצעת מכירה למוצר בתשלום; (2) זה לא מחליף את Claude Code או Codex -- אלה הסוכנים שבפועל "
                 "כותבים קוד, Spec Kit הוא שכבת התהליך המובנה מעליהם (יש לזה דיאגרמה משלה עוד שני שקפים קדימה); "
                 "(3) הבעיה המניעה היא בדיוק מה ששקפים 2-4 הראו זה עתה: ייצור קוד מהיר חשף כמה מהעבודה האמיתית היא "
                 "בעצם החלטה מה לבנות. אם יש זמן, כדאי להראות בקצרה את ה-GitHub repo האמיתי של Spec Kit ואת ה-README "
                 "שלו (screenshots #1-2 בצ'קליסט) כדי שהקהל יראה שזה פרויקט אמיתי ופעיל, לא סקריפט חד-פעמי."))

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
    add_note(s, ("השורה הראשונה מתקינה את כלי ה-CLI specify עצמו (הגדרה חד-פעמית, דרך כלי ה-uv של Python). השורה "
                 "השנייה מריצה אותו בתוך תיקיית פרויקט קיימת ואומרת לה לאיזה סוכן להתחבר -- כאן, Claude Code. זה "
                 "יוצר תיקיית .specify/ (תבניות, סקריפטים, חוקת הפרויקט) ותיקיית .claude/skills/ עם פקודות ה-"
                 "/speckit-... . הפלט בטרמינל למטה הוא הפלט האמיתי, ללא עריכה, מהאתחול של הריפו הזה עצמו -- שום "
                 "דבר כאן לא מבוים או מדומה."))

    # ---------- Slide 10: 7-stage workflow ----------
    s = add_slide(prs)
    add_title(s, "תהליך העבודה בשבעה שלבים")
    add_image(s, "diagram-speckit-workflow.png", Inches(0.6), Inches(1.6), width=SW - Inches(1.2))
    add_note(s, ("לא לצלול עדיין לתחביר הפקודות -- המטרה כאן היא רק המודל המנטלי של הצינור: constitution (כללי "
                 "פרויקט כלל-ארגוניים, נכתבים פעם אחת) -> specify (מה בונים) -> clarify (פותרים את החלקים המעורפלים) "
                 "-> plan (הגישה הטכנית) -> tasks (פירוק התוכנית לצעדים מסודרים וניתנים לבדיקה) -> analyze (בדיקה "
                 "אוטומטית של spec/plan/tasks לסתירות) -> implement (הסוכן כותב את הקוד). כל שלב מייצר קובץ אמיתי "
                 "ברפוזיטורי, שזה הנושא של השקף הבא. כבר הצגנו בקצרה *למה* כל שלב קיים בשקף 7 -- זה השקף שמראה את "
                 "הסדר שבו הם רצים."))

    # ---------- Slide 11: Real files ----------
    s = add_slide(prs)
    add_title(s, "התוצר: קבצים אמיתיים ברפוזיטורי")
    add_bullets(s, [
        {"text": "specs/001-heltec-monitor/{spec,plan,tasks}.md", "size": 24, "color": BLUE, "bold": True},
        "כל שלב כותב קבצי Markdown רגילים לתוך הרפוזיטורי -- הם נשמרים ב-git כמו כל קובץ מקור אחר.",
        "זה ההפך משיחת צ'אט, שחיה בכלי אחד, קל לאבד אותה, וקשה לאדם נוסף (או סוכן AI נוסף) להמשיך ממנה.",
        "התועלת המעשית: אפשר לסגור את הצ'אט, לעבור מ-Claude Code ל-Codex, או לחזור לפרויקט אחרי חודש, לפתוח את "
        "spec.md, ולראות בדיוק מה הוחלט ולמה -- בלי לשחזר את זה מהזיכרון.",
    ], size=21)
    add_note(s, ("זה רגע טוב לפתוח בפועל את specs/001-heltec-monitor/spec.md בעורך, ולו רק לגלול בו -- לראות קובץ "
                 "Markdown אמיתי וקריא (לא קוד, לא JSON) בדרך כלל מפשיט את כל הרעיון לקהל שאין לו רקע קודם."))

    # ---------- Slide 12: who does what ----------
    s = add_slide(prs)
    add_title(s, "מי עושה מה")
    add_image(s, "diagram-tool-relationship.png", Inches(2.0), Inches(1.2), height=Inches(6.0))
    add_note(s, ("חשוב לומר את זה במפורש, זו נקודת הבלבול הנפוצה ביותר למתחילים: Spec Kit הוא לא סוכן קידוד והוא "
                 "לא כותב קוד. Claude Code או Codex הם הסוכנים שבפועל קוראים את קבצי spec/plan/tasks וכותבים את "
                 "הקושחה. ה-IDE (VS Code, CLion/JetBrains) הוא רק סביבת העבודה של האדם לקריאה ועריכה של קבצים לצד "
                 "הסוכן. כלומר המבנה הוא: IDE (אדם) + סוכן קידוד (מבצע את העבודה) + Spec Kit (התהליך המובנה שהסוכן "
                 "פועל לפיו) -- שלוש שכבות נפרדות, כל אחת ניתנת להחלפה, לא מוצר אחד."))

    # ---------- Slide 13: same repo two agents ----------
    s = add_slide(prs)
    add_title(s, "אותו ריפו, שני סוכנים")
    add_bullets(s, [
        {"text": "Claude Code  ←  /speckit-specify   (.claude/skills/)", "size": 22, "color": BLUE},
        {"text": "Codex  ←  $speckit-specify   (.agents/skills/)", "size": 22, "color": AMBER},
        "אותה פקודה, אותם קבצים בבסיס, אותה תוצאה -- רק תחביר ההפעלה שונה, כי לכל סוכן יש מוסכמה משלו להפעלת "
        "פקודה מותאמת אישית.",
        "זו לא טענה תיאורטית -- הריפו הזה בדיוק מותקן עם שני האינטגרציות במקביל, וכל סוכן יכול להמשיך בדיוק "
        "מהמקום שהשני עצר בו.",
    ], top=Inches(1.55), size=20)
    add_missing_visual_placeholder(s, "Claude Code + Codex session (same repo)", Inches(0.8), Inches(4.3), SW - Inches(1.6), Inches(2.1))
    add_note(s, ("כאן נכנסים screenshots #6-7 מהצ'קליסט. אם יש טרמינל חי זמין, שווה להריץ בפועל /speckit-specify "
                 "בסוכן אחד ו-$speckit-specify בשני נגד הריפו הזה, כדי להראות שזה אותו skill בבסיס, רק תחביר הפעלה "
                 "שונה לכל סוכן."))

    # ---------- Slide 14: VS Code briefly ----------
    s = add_slide(prs)
    add_title(s, "VS Code בקצרה")
    add_bullets(s, [
        "שני extensions עושים כאן את כל העבודה בפועל: PlatformIO IDE (בונה ומעלה את הקושחה, מנהל את שרשרת "
        "הכלים של ESP32) ו-C/C++ (הדגשת תחביר וניווט לקוד המקור של הקושחה).",
        "כל השאר בסדנה הזו -- הפקודות של Spec Kit, Claude Code, Codex -- עובד אותו דבר בלי קשר לעורך.",
        "אם משתמשים ב-JetBrains/CLion במקום: אותו רפוזיטורי, אותם קבצים, אותן פקודות Spec Kit, רק טרמינל שונה "
        "וסט קיצורי מקלדת שונה.",
    ], size=21)
    add_note(s, ("לשמור על זה קצר -- הנקודה היא שהעורך הוא הבחירה הכי פחות חשובה בכל התהליך הזה. לא כדאי להיגרר "
                 "לוויכוח על extensions -- שניים זו כל הרשימה."))

    # ---------- Slide 15: comparison table ----------
    s = add_slide(prs)
    add_title(s, "פרומפט ישיר מול Spec Kit")
    subtitle = s.shapes.add_textbox(Inches(0.8), Inches(1.05), SW - Inches(1.6), Inches(0.5))
    stf = subtitle.text_frame
    stf.word_wrap = True
    sp = stf.paragraphs[0]
    sp.alignment = PP_ALIGN.RIGHT
    set_rtl(sp)
    sr = sp.add_run()
    sr.text = "אותו סוכן בבסיס, אותה חומרת יעד -- מה שמשתנה הוא איפה כל אחד מהדברים הבאים חי:"
    sr.font.size = Pt(18)
    sr.font.italic = True
    sr.font.name = FONT
    sr.font.color.rgb = SLATE
    rows = [
        ("Requirements", "בשיחת צ'אט", "כקבצים ברפוזיטורי"),
        ("Clarifications", "הסוכן מניח לבד", "שלב הבהרה מפורש"),
        ("Traceability", "נמוכה", "גבוהה"),
        ("Repeatability", "נמוכה-בינונית", "גבוהה"),
    ]
    top = Inches(1.7)
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
    add_note(s, ("traceability פירושו: אפשר להצביע על הרגע והסיבה המדויקים שדרישה הוחלטה? repeatability פירושו: "
                 "אם נותנים את אותו המפרט לסוכן אחר, או מריצים את התהליך שוב, האם מגיעים לתוצאה דומה? שניהם נמוכים "
                 "באופן טבעי בפרומפט אד-הוק בודד כי שום דבר לא נכתב, וגבוהים יותר באופן טבעי עם Spec Kit כי הדרישות "
                 "הן קבצים, לא זיכרון."))

    # ---------- Slide 16: alternatives ----------
    s = add_slide(prs)
    add_title(s, "ולמה לא רק \"עוד framework\"?")
    add_bullets(s, [
        "Spec Kit הוא לא הכלי היחיד בתחום הזה -- שווה לדעת שזו נקודה אחת על ספקטרום, לא האופציה היחידה.",
        {"text": "OpenSpec", "bold": True, "color": BLUE},
        "מכסה טריטוריה דומה -- לכתוב מפרט לפני קוד -- עם תבנית ומוסכמות פקודות משלו.",
        {"text": "BMAD (Breakthrough Method for Agile AI-Driven Development)", "bold": True, "color": AMBER},
        "הולך צעד נוסף: מספר תפקידי AI מוגדרים (אנליסט, ארכיטקט, מפתח, QA) שמעבירים עבודה זה לזה, מה שמוסיף מבנה "
        "אמיתי אבל גם overhead אמיתי לפרויקט קטן.",
        {"text": "Spec Kit יושב בכוונה באמצע: יותר מבנה מפרומפט חשוף, הרבה פחות טקס מ-framework מרובה-תפקידים -- "
         "וזו הסיבה שהוא מתאים לדוגמת קושחה משובצת קטנה כמו זו.", "bold": True},
    ], size=19)
    add_note(s, ("לא סקירת frameworks -- לא להשקיע כאן יותר מדקה, זו לא המטרה של הסדנה. המסר היחיד ששווה להעביר: "
                 "זה ספקטרום (בלי תהליך -> Spec Kit -> frameworks כבדים יותר), וכמות התהליך הנכונה תלויה בגודל "
                 "הפרויקט והצוות."))

    # ---------- Slide 17: hardware verified ----------
    s = add_slide(prs)
    add_title(s, "החומרה, מאומתת")
    add_bullets(s, [
        "הלוח שאנחנו בונים עבורו בפועל: Heltec WiFi Kit V3, שהוא מיקרו-בקר ESP32-S3 עם מסך OLED קטן מובנה, "
        "ועוד חיישן BME280 חיצוני (טמפרטורה/לחות/לחץ אוויר) מחווט אליו ב-I2C.",
        {"text": "ללוח אין חיישן סביבתי מובנה -- כך ש\"איזה חיישן\" משקף 3 מעולם לא היה פרט טכני, אלא החלטת מוצר "
         "אמיתית שמישהו היה חייב לקבל לפני שהקוד יכול היה להיות נכון.", "bold": True, "color": RED},
        "פרט טכני מפתיע אחד שקל לטעות בו: על הלוח הספציפי הזה, פיני ה-I2C של המסך המובנה הם GPIO 17/18, לא פיני "
        "ה-I2C המקובלים של ESP32 (21/22) -- לטעות בזה גורם למסך להישאר ריק לגמרי בלי שום הודעת שגיאה.",
    ], size=20)
    add_note(s, ("השקף הזה קיים כדי לבסס אמינות חומרה אמיתית לפני שמשווים בין שתי גישות הבנייה -- מכאן והלאה הכול "
                 "מבוסס על לוח פיזי אמיתי, לא דוגמת צעצוע."))

    # ---------- Slide 18: Stage A ----------
    s = add_slide(prs)
    add_title(s, "Stage A: פרומפט בלבד")
    add_bullets(s, [
        {"text": "המסר של ההשוואה הזו: הנחה משתמעת מול החלטה מפורשת -- לא \"קוד גרוע מול קוד טוב\".", "bold": True, "size": 22, "color": BLUE},
        "כדי לשמור על ההשוואה הוגנת, חיווט החומרה (פיני I2C, רצף הפעלת Vext) נכון בשתי הגרסאות -- גם בגרסת "
        "הפרומפט-בלבד וגם בגרסה המונחית-מפרט; טעויות חיווט הן לא הסיפור כאן.",
        "מה שבאמת שונה זה כל מה שהפרומפט המקורי מעולם לא פירט: איזה חיישן בדיוק להשתמש, מה הסף המספרי המדויק, "
        "והאם האזהרה צריכה רצועת סבילות (היסטרזיס) סביב הסף הזה.",
        {"text": "הדוגמה הכי ברורה: לגרסת הפרומפט-בלבד אין בכלל היסטרזיס. זה לא באג בתכנות -- הקוד עושה בדיוק "
         "מה שקריאה סבירה של הפרומפט מרמזת. זו התוצאה הישירה של דרישה שפשוט מעולם לא נוסחה.", "italic": True},
    ], size=19)
    add_note(s, ("ויזואל: examples/prompt-only/naive_monitor.ino. אם הוא פתוח, כדאי לגלול לבדיקת הסף ולהצביע שיש "
                 "בדיוק השוואה אחת (value > 30) בלי תנאי שני לכיבוי האזהרה -- ה'ענף else' החסר הזה הוא כל סיפור "
                 "ההיסטרזיס, שמגיע בפירוט בשקף 20."))

    # ---------- Slide 19: Specify + Clarify ----------
    s = add_slide(prs)
    add_title(s, "Stage B-C: Specify + Clarify")
    add_bullets(s, [
        "specify כותב מה המוצר אמור לעשות, בשפה פשוטה, בלי לגעת עדיין בקוד -- למעשה טיוטה ראשונה של spec.md.",
        "clarify לאחר מכן שואל את האדם שאלות ממוקדות בדיוק על הפערים שראינו בשקף 3, מקליט כל תשובה ישירות "
        "לתוך המפרט. למטה התמליל האמיתי:",
    ], size=19, top=Inches(1.2), height=Inches(1.5))
    add_image(s, "code-spec-clarifications.png", Inches(0.9), Inches(3.05), width=Inches(11.0))
    add_note(s, ("זה התמליל האמיתי של clarify מהפרויקט הזה, לא הדמיה. שווה להצביע שאלה בדיוק סוג השאלות שמבקר "
                 "אנושי זהיר היה שואל -- הסוכן פשוט שואל אותן מוקדם יותר, לפני כתיבת קוד, ומתעד את התשובות כדי "
                 "שלעולם לא יאבדו."))

    # ---------- Slide 20: Hysteresis ----------
    s = add_slide(prs)
    add_title(s, "היסטרזיס: הדוגמה הכי ברורה")
    add_image(s, "diagram-hysteresis.png", Inches(0.6), Inches(1.3), width=SW - Inches(1.2))
    add_note(s, ("לעבור על הדיאגרמה משמאל לימין: הטמפרטורה חוצה את ה-30°C, ה-WARNING נדלק. בלי רצועת סבילות, "
                 "ברגע שהטמפרטורה יורדת חזרה ל-29.9°C המסך היה קופץ מיד חזרה ל-OK, ואז חזרה ל-WARNING בתנודה "
                 "הקטנה הבאה -- הבהוב על כל חצייה של מספר בודד. הרצועה (כאן, 28-30°C) אומרת שברגע שה-WARNING דלוק, "
                 "הוא *נשאר* דלוק בכל מקום בתוך הרצועה, ונכבה רק כשהטמפרטורה יורדת מתחת לקצה התחתון (28°C). זו לא "
                 "בעיית תכנות לניפוי -- זו החלטת מוצר (כמה סבילות מקובלת) שהיתה חייבת להתקבל לפני שנכתבה שורה אחת "
                 "של מכונת המצבים, ובדיוק זה סוג ההחלטה ששלב ה-clarify קיים כדי לחשוף."))

    # ---------- Slide 21: Plan + Tasks ----------
    s = add_slide(prs)
    add_title(s, "Stage D-E: Plan + Tasks")
    add_image(s, "diagram-architecture.png", Inches(0.6), Inches(1.5), width=SW - Inches(1.2))
    add_note(s, ("plan הופך את הדרישות שכבר הובהרו לגישה טכנית קונקרטית: איזה לוח, אילו ספריות, ובאופן קריטי, "
                 "ארכיטקטורה שמפוצלת לשלושה חלקים נפרדים -- מתאם חיישן, לוגיקת החלטה טהורה ללא שום תלות בחומרה, "
                 "ורכיב דיווח למסך OLED ול-Serial. tasks לאחר מכן מפרק את התוכנית לצעדים קטנים, מסודרים, וניתנים "
                 "לבדיקה, שסוכן (או אדם) יכול לבצע אחד אחד. הפיצול הארכיטקטוני שמוצג כאן הוא מה שמאפשר את הבדיקה "
                 "האוטומטית בשקף הבא: מכיוון שלוגיקת ההחלטה לא נוגעת בחומרה בכלל, אפשר לבדוק אותה על מחשב נייד "
                 "בלי לוח Heltec מחובר בכלל. אם רוצים להראות גם את הקבצים עצמם, screenshots #10-11 בצ'קליסט הם "
                 "plan.md ו-tasks.md עצמם."))

    # ---------- Slide 22: Analyze catch ----------
    s = add_slide(prs)
    add_title(s, "⭐ Stage F: Analyze מוצא סתירה אמיתית", size=28)
    add_image(s, "diagram-analyze-catch.png", Inches(2.6), Inches(1.15), height=Inches(6.1))
    add_note(s, ("השקף החשוב ביותר בכל ההרצאה -- לא להעביר במהירות. לעבור על כל אחת מחמש התיבות: (1) בשלב "
                 "clarify, הוחלט שהאזהרה צריכה להישאר דלוקה בתוך רצועת ההיסטרזיס; (2) אבל קריטריון הצלחה נפרד "
                 "(SC-004), שנכתב קודם, עדיין תיאר את ההתנהגות הפשוטה יותר של דלוק/כבוי -- אף אחד לא שם לב "
                 "שהשניים כבר לא תואמים; (3) /speckit-analyze, שבודק אוטומטית spec/plan/tasks אחד מול השני, תפס "
                 "את הסתירה הזו; (4) המפרט תוקן במקום; (5) המימוש התחיל רק אחרי שהמסמכים הסכימו ביניהם. זו לא "
                 "דוגמה מומצאת לצורך ההרצאה -- זה קרה ממש בבניית הפרויקט הזה, והתיעוד המלא שמור ב-"
                 "specs/001-heltec-monitor/analysis-report.md. אם יש טרמינל, אפשר להראות live: "
                 "git show b91cd94 -- specs/001-heltec-monitor/spec.md משחזר את ה-diff המדויק."))

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
    add_note(s, ("ההוכחה הכי חזקה לערך של Spec Kit בכל ההרצאה -- אם הקהל זוכר רגע קונקרטי אחד מהסדנה, שיהיה זה. "
                 "התמונה למטה היא ה-diff האמיתי: הניסוח הישן של SC-004 משמאל/אדום, הניסוח המתוקן מימין/ירוק, "
                 "מראה את קריטריון ההצלחה מעודכן כדי להתאים להחלטת ההיסטרזיס מ-clarify. חשוב להדגיש: לא נכתב "
                 "שום קוד עדיין כשזה נתפס -- לתקן סתירה בין שני מסמכי Markdown עולה כמה שניות; לתקן את אותה "
                 "סתירה אחרי שכבר הפכה לשתי התנהגויות קושחה סותרות היה עולה הרבה יותר, ואולי בכלל לא היה נתפס "
                 "בלי בדיקת חומרה שמפעילה בדיוק את מקרה הקצה הזה."))

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
    add_note(s, ("implement הוא השלב שסוף-סוף כותב את קוד הקושחה בפועל, לפי plan.md ו-tasks.md, בסדר. מכיוון "
                 "שלוגיקת ההחלטה (monitor_logic, מוצגת למעלה) תוכננה ללא שום תלות בחומרה עוד בשלב plan, אפשר "
                 "להריץ עליה חבילת בדיקות אוטומטית ישירות על מחשב נייד -- בלי לוח Heltec, בלי כבל סריאלי, בלי "
                 "שום דבר פיזי. הפאנל בפינה השמאלית-תחתונה הוא הפלט האמיתי, ללא עריכה, של הרצת הבדיקות הזו: "
                 "11 מתוך 11 עברו. זו הסיבה שכבר יש לנו ביטחון גבוה בלוגיקת ההחלטה עצמה עוד לפני שנגענו בחומרה "
                 "אמיתית -- מה שעדיין לא מאומת זה רק החיווט הפיזי, החיישן והמסך, ובדיוק זה הנושא של שני השקפים "
                 "הבאים."))

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
