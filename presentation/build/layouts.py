"""Slide layouts. Each layout: fn(slide, s: Slide, lang, glossary) -> None.

Every layout draws the background, the title, its content inside
content_box(has_tip) and, when the slide has a tip, the TIP band.
In HE the geometry is mirrored horizontally (x -> SLIDE_W - x - w);
diagrams stay left to right internally.

Shapes owned by a layout are named "lay-*"; everything else on a slide
comes from a diagram builder.
"""
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Emu, Inches, Pt

from .shapes import DIAGRAMS, pill
from .text import write_paragraphs
from .theme import (ASSETS, COLORS, FONTS, MARGIN, SLIDE_H, SLIDE_W,
                    content_box, tip_box)

TITLE_PT = 36
BODY_PT = 24
SMALL_PT = 20
TIP_PT = 18
CODE_PT = 18
GAP = Inches(0.3)
TIP_GAP = Inches(0.2)  # breathing room between content and the tip band
PILL_W, PILL_H = Inches(0.9), Inches(0.4)


def _mx(x, w, lang):
    """Mirror a box horizontally for RTL."""
    return SLIDE_W - x - w if lang == "he" else x


def _t(d, lang):
    return (d or {}).get(lang, "")


def _textbox(slide, name, x, y, w, h, lang, items, glossary, size,
             bullet=False, color=None, bold=False, align=None, anchor=None):
    tb = slide.shapes.add_textbox(int(_mx(x, w, lang)), int(y), int(w), int(h))
    tb.name = name
    tf = tb.text_frame
    write_paragraphs(tf, items, lang, size, glossary, bullet=bullet,
                     color=color, bold=bold)
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    if anchor is not None:
        tf.vertical_anchor = anchor
    if align is not None:
        for p in tf.paragraphs:
            p.alignment = align
    return tb


def _rect(slide, name, x, y, w, h, lang, fill, line=None, kind=MSO_SHAPE.ROUNDED_RECTANGLE):
    sh = slide.shapes.add_shape(kind, int(_mx(x, w, lang)), int(y), int(w), int(h))
    sh.name = name
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = 0.06
    sh.fill.solid()
    sh.fill.fore_color.rgb = COLORS[fill]
    if line:
        sh.line.color.rgb = COLORS[line]
        sh.line.width = Pt(1.25)
    else:
        sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def _background(slide):
    pic = slide.shapes.add_picture(str(ASSETS / "bg.png"), 0, 0, SLIDE_W, SLIDE_H)
    pic.name = "lay-bg"


def _head_font(tb, lang):
    for p in tb.text_frame.paragraphs:
        for r in p.runs:
            r.font.name = FONTS[lang]["head"]


def _title(slide, s, lang, glossary):
    tb = _textbox(slide, "lay-title", MARGIN, MARGIN, SLIDE_W - 2 * MARGIN,
                  Inches(1.0), lang, [_t(s.title, lang)], glossary, TITLE_PT,
                  bold=True, anchor=MSO_ANCHOR.MIDDLE)
    _head_font(tb, lang)


def add_tip(slide, tip_text, lang, glossary=()):
    """Bottom TIP band: pill labelled "TIP" (left in EN, right in HE) + text."""
    x, y, w, h = tip_box()
    _rect(slide, "lay-tip-band", x, y, w, h, lang, "surface", line="tip")
    pad = Inches(0.15)
    p = pill(slide, _mx(x + pad, PILL_W, lang), y + (h - PILL_H) // 2, "TIP", lang)
    p.name = "lay-tip-pill"
    tx = x + pad + PILL_W + pad
    _textbox(slide, "lay-tip-text", tx, y, x + w - tx - pad, h, lang, [tip_text],
             list(glossary), TIP_PT, anchor=MSO_ANCHOR.MIDDLE)


def _frame(slide, s, lang, glossary, title=True):
    """Background, title, tip band. Returns the (unmirrored) content box."""
    _background(slide)
    if title:
        _title(slide, s, lang, glossary)
    x, y, w, h = content_box(s.tip is not None)
    if s.tip:
        add_tip(slide, getattr(s.tip, lang), lang, glossary)
        h -= TIP_GAP
    return x, y, w, h


def _bullets(s, lang):
    return [getattr(b, lang) for b in s.bullets]


def _bullet_box(slide, box, s, lang, glossary, size=BODY_PT):
    if not s.bullets:
        return
    x, y, w, h = box
    _textbox(slide, "lay-body", x, y, w, h, lang, _bullets(s, lang), glossary,
             size, bullet=True)


# --- layouts ---------------------------------------------------------------

def _centered(slide, s, lang, glossary, title_pt, sub_color):
    x, y, w, h = _frame(slide, s, lang, glossary, title=False)
    title_h = Inches(1.6)
    ty = y + (h - title_h) // 2 - Inches(0.6)
    tb = _textbox(slide, "lay-title", x, ty, w, title_h, lang, [_t(s.title, lang)],
                  glossary, title_pt, bold=True, align=PP_ALIGN.CENTER,
                  anchor=MSO_ANCHOR.BOTTOM)
    _head_font(tb, lang)
    if s.bullets:
        sy = ty + title_h + Inches(0.2)
        _textbox(slide, "lay-body", x, sy, w, y + h - sy, lang, _bullets(s, lang),
                 glossary, SMALL_PT, color=COLORS[sub_color], align=PP_ALIGN.CENTER)


def title(slide, s, lang, glossary):
    _centered(slide, s, lang, glossary, 48, "muted")


def section(slide, s, lang, glossary):
    _centered(slide, s, lang, glossary, 44, "accent2")


def bullets(slide, s, lang, glossary):
    box = _frame(slide, s, lang, glossary)
    _bullet_box(slide, box, s, lang, glossary)


def bullets_diagram(slide, s, lang, glossary):
    """Short bullet strip on top, diagram below in the rest of the content box."""
    x, y, w, h = _frame(slide, s, lang, glossary)
    strip = min(len(s.bullets), 2) * Inches(0.5)
    if s.bullets:
        _bullet_box(slide, (x, y, w, strip), s, lang, glossary, SMALL_PT)
        y, h = y + strip + Inches(0.15), h - strip - Inches(0.15)
    if s.diagram:
        DIAGRAMS[s.diagram["name"]](slide, (x, y, w, h), s.diagram, lang, glossary)


def _columns(x, w, n):
    cw = (w - (n - 1) * GAP) // n
    return [(x + i * (cw + GAP), cw) for i in range(n)]


def compare(slide, s, lang, glossary):
    """Two cards, columns[0] on the reading-start side (left EN, right HE)."""
    x, y, w, h = _frame(slide, s, lang, glossary)
    cols = s.extra.get("columns") or []
    head_h = Inches(0.7)
    pad = Inches(0.2)
    for i, ((cx, cw), col) in enumerate(zip(_columns(x, w, len(cols) or 1), cols)):
        _rect(slide, f"lay-col{i}-card", cx, y, cw, h, lang, "surface", line="accent")
        _textbox(slide, f"lay-col{i}-head", cx + pad, y + pad // 2, cw - 2 * pad,
                 head_h, lang, [_t(col.get("heading"), lang)], glossary, BODY_PT,
                 bold=True, color=COLORS["accent2"], anchor=MSO_ANCHOR.MIDDLE)
        items = [_t(it, lang) for it in col.get("items") or []]
        if items:
            _textbox(slide, f"lay-col{i}-body", cx + pad, y + head_h, cw - 2 * pad,
                     h - head_h - pad, lang, items, glossary, SMALL_PT, bullet=True)


def table(slide, s, lang, glossary):
    """Native table; column order reversed in HE."""
    x, y, w, h = _frame(slide, s, lang, glossary)
    spec = s.extra.get("table") or {}
    header = spec.get("header") or []
    rows = [header] + list(spec.get("rows") or [])
    if not header:
        return
    order = list(range(len(header)))
    if lang == "he":
        order.reverse()
    row_h = min(Inches(0.75), h // len(rows))
    gf = slide.shapes.add_table(len(rows), len(header), int(x), int(y), int(w),
                                int(row_h * len(rows)))
    gf.name = "lay-table"
    tbl = gf.table
    for c in range(len(header)):
        tbl.columns[c].width = Emu(w // len(header))
    for r, row in enumerate(rows):
        tbl.rows[r].height = Emu(row_h)
        for c, src in enumerate(order):
            cell = tbl.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLORS["accent"] if r == 0 else COLORS["surface"]
            write_paragraphs(cell.text_frame, [_t(row[src], lang)], lang, 18, glossary,
                             bullet=False, bold=r == 0,
                             color=COLORS["bg"] if r == 0 else COLORS["text"])
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE


def photos(slide, s, lang, glossary):
    """Two photos side by side with captions; images[0] on the reading-start side."""
    from PIL import Image
    x, y, w, h = _frame(slide, s, lang, glossary)
    imgs = s.extra.get("images") or []
    cap_h = Inches(0.6)
    for i, ((cx, cw), img) in enumerate(zip(_columns(x, w, len(imgs) or 1), imgs)):
        path = ASSETS / img["file"]
        iw, ih = Image.open(path).size
        bh = h - cap_h
        scale = min(cw / iw, bh / ih)
        pw, ph = int(iw * scale), int(ih * scale)
        px = cx + (cw - pw) // 2
        pic = slide.shapes.add_picture(str(path), int(_mx(px, pw, lang)), int(y), pw, ph)
        pic.name = f"lay-photo{i}"
        _textbox(slide, f"lay-caption{i}", cx, y + ph, cw, cap_h, lang,
                 [_t(img.get("caption"), lang)], glossary, SMALL_PT,
                 color=COLORS["muted"], align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE)


def code(slide, s, lang, glossary):
    """Bullets on the reading-start side, a dark code card on the other side.
    Code is always LTR (mono font, no RTL)."""
    x, y, w, h = _frame(slide, s, lang, glossary)
    text_w = int(w * 0.38) if s.bullets else 0
    if s.bullets:
        _bullet_box(slide, (x, y, text_w, h), s, lang, glossary, SMALL_PT)
    cx = x + text_w + (GAP if s.bullets else 0)
    cw = x + w - cx
    _rect(slide, "lay-code-card", cx, y, cw, h, lang, "bg", line="accent")
    pad = Inches(0.25)
    tb = slide.shapes.add_textbox(int(_mx(cx + pad, cw - 2 * pad, lang)), int(y + pad),
                                  int(cw - 2 * pad), int(h - 2 * pad))
    tb.name = "lay-code"
    tf = tb.text_frame
    write_paragraphs(tf, [s.extra.get("code", "")], "en", CODE_PT, [], bullet=False,
                     color=COLORS["ok"])
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    for p in tf.paragraphs:
        for r in p.runs:
            r.font.name = FONTS["en"]["mono"]


LAYOUTS = {
    "title": title,
    "section": section,
    "bullets": bullets,
    "bullets-diagram": bullets_diagram,
    "compare": compare,
    "table": table,
    "photos": photos,
    "code": code,
}
