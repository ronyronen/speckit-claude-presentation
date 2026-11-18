"""Slide layouts. Each layout: fn(slide, s: Slide, lang, glossary) -> None.

Every layout draws the background, the title, its content inside
content_box(has_tip) and, when the slide has a tip, the tip band (light-bulb
icon + text, no label).
In HE the geometry is mirrored horizontally (x -> SLIDE_W - x - w);
diagrams stay left to right internally.

Shapes owned by a layout are named "lay-*"; everything else on a slide
comes from a diagram builder.
"""
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Emu, Inches, Pt

from .shapes import DIAGRAMS
from .text import write_paragraphs
from .theme import (ASSETS, BULLET_SPACE, COLORS, FONTS, FOOTER_PT, ICON,
                    MARGIN, SLIDE_H, SLIDE_W, content_box, tip_box)

TITLE_PT = 36
BODY_PT = 24
SMALL_PT = 20
TIP_PT = 18
CODE_PT = 18
GAP = Inches(0.3)
TIP_GAP = Inches(0.2)  # breathing room between content and the tip band


# --- text height estimate (the real overflow guard; autofit is a safety net:
# PowerPoint does not apply normAutofit until the text is edited) -----------
EMU_PT = 12700
CHAR_EM = 0.55      # conservative average glyph width, in ems
LINE_EM = 1.2       # line height, in ems
BULLET_INDENT = 285750  # marL from text.write_paragraphs
FRAME_INSET_V = Inches(0.1)  # default text-frame top + bottom insets
FRAME_INSET_H = Inches(0.2)  # default text-frame left + right insets
CELL_INSET_V = Inches(0.1)   # default table-cell top + bottom margins
CELL_INSET_H = Inches(0.2)   # default table-cell left + right margins
TABLE_PT_MAX, TABLE_PT_MIN = 18, 14
BODY_PT_MIN = 14     # floor for every text body
TITLE_PT_MIN = 28    # floor for slide titles
MONO_EM = 0.6        # monospace glyph width, in ems
DIAGRAM_MIN_H = Inches(2.5)
CODE_TEXT_FRAC = 0.32  # bullet column share on code slides; the rest is code


def est_lines(text, width_emu, size_pt, bold=False, char_em=CHAR_EM):
    """Greedy word-wrap line count for text in a box width_emu wide."""
    em = size_pt * EMU_PT * (1.1 if bold else 1.0)
    cpl = max(1, int(width_emu / (em * char_em)))
    n = 0
    for para in str(text).split("\n"):
        lines, cur = 1, 0
        for word in para.split(" "):  # not NBSP: "27\u00a0°C" is one word
            if not word:
                continue
            need = len(word) if cur == 0 else cur + 1 + len(word)
            if need <= cpl:
                cur = need
            else:
                lines += 1 + (len(word) - 1) // cpl
                cur = (len(word) - 1) % cpl + 1
        n += lines
    return n


def est_height(lines, size_pt):
    return int(lines * size_pt * LINE_EM * EMU_PT)


def bullet_space(items, size_pt, space=BULLET_SPACE):
    """Total space-before of the bullet paragraphs (text.write_paragraphs)."""
    n = sum(len(str(t).split("\n")) for t in items)
    return int(n * size_pt * space * EMU_PT)


def fit_size(sid, field, items, w, h, size, bullet=False, bold=False,
             char_em=CHAR_EM, min_pt=BODY_PT_MIN, max_lines=None,
             space=BULLET_SPACE):
    """Largest font from size down to min_pt whose estimated text height fits
    a w x h text frame (and needs at most max_lines lines). Raises ValueError
    naming the slide and field when even min_pt does not fit."""
    tw = w - FRAME_INSET_H - (BULLET_INDENT if bullet else 0)
    for pt in range(size, min_pt - 1, -1):
        lines = sum(est_lines(t, tw, pt, bold, char_em) for t in items)
        extra = bullet_space(items, pt, space) if bullet else 0
        if (max_lines is None or lines <= max_lines) and \
                est_height(lines, pt) + extra + FRAME_INSET_V <= h:
            return pt
    raise ValueError(f"{sid}: {field} too long to fit at {min_pt}pt")


def _mx(x, w, lang):
    """Mirror a box horizontally for RTL."""
    return SLIDE_W - x - w if lang == "he" else x


def _t(d, lang):
    return (d or {}).get(lang, "")


def _textbox(slide, name, x, y, w, h, lang, items, glossary, size,
             bullet=False, color=None, bold=False, align=None, anchor=None,
             fit=None, min_pt=BODY_PT_MIN, max_lines=None, space=BULLET_SPACE):
    """fit=(slide id, field name) steps size down until the text fits."""
    if fit:
        size = fit_size(*fit, items, w, h, size, bullet=bullet, bold=bold,
                        min_pt=min_pt, max_lines=max_lines, space=space)
    tb = slide.shapes.add_textbox(int(_mx(x, w, lang)), int(y), int(w), int(h))
    tb.name = name
    tf = tb.text_frame
    write_paragraphs(tf, items, lang, size, glossary, bullet=bullet,
                     color=color, bold=bold, space=space)
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


def _background(slide, name="bg.png"):
    pic = slide.shapes.add_picture(str(ASSETS / name), 0, 0, SLIDE_W, SLIDE_H)
    pic.name = "lay-bg"


def _head_font(tb, lang):
    for p in tb.text_frame.paragraphs:
        for r in p.runs:
            r.font.name = FONTS[lang]["head"]


TITLE_GAP = Inches(0.1)  # between the title frame and the content
BAR_W = Inches(0.08)     # accent bar on the reading-start side of the title
BAR_GAP = Inches(0.15)


def _title(slide, s, lang, glossary):
    th = content_box(False)[1] - MARGIN - TITLE_GAP
    bar_h = Inches(0.6)
    _rect(slide, "lay-title-bar", MARGIN, MARGIN + (th - bar_h) // 2, BAR_W, bar_h,
          lang, "accent", kind=MSO_SHAPE.RECTANGLE)
    tx = MARGIN + BAR_W + BAR_GAP
    tb = _textbox(slide, "lay-title", tx, MARGIN, SLIDE_W - MARGIN - tx,
                  th, lang, [_t(s.title, lang)], glossary, TITLE_PT,
                  bold=True, anchor=MSO_ANCHOR.MIDDLE, fit=(s.id, "title"),
                  min_pt=TITLE_PT_MIN, max_lines=1)
    _head_font(tb, lang)


def add_tip(slide, tip_text, lang, glossary=(), sid="tip"):
    """Bottom tip band: amber stripe + light-bulb icon on the reading-start
    side (left in EN, right in HE), then the tip text. No "TIP" label."""
    x, y, w, h = tip_box()
    _rect(slide, "lay-tip-band", x, y, w, h, lang, "tip_band")
    stripe = Inches(0.07)
    _rect(slide, "lay-tip-stripe", x, y, stripe, h, lang, "bulb",
          kind=MSO_SHAPE.RECTANGLE)
    pad = Inches(0.18)
    ix = x + stripe + pad
    icon = slide.shapes.add_picture(str(ASSETS / "tip-bulb.png"),
                                    int(_mx(ix, ICON, lang)), int(y + (h - ICON) // 2),
                                    ICON, ICON)
    icon.name = "lay-tip-icon"
    tx = ix + ICON + pad
    _textbox(slide, "lay-tip-text", tx, y, x + w - tx - pad, h, lang, [tip_text],
             list(glossary), TIP_PT, color=COLORS["tip_text"],
             anchor=MSO_ANCHOR.MIDDLE, fit=(sid, "tip"))


def add_footer(slide, number, label, lang, glossary=()):
    """Talk name on the reading-start side, slide number on the other, in the
    bottom margin (below the tip band)."""
    y, h = SLIDE_H - MARGIN + Inches(0.08), MARGIN - Inches(0.12)
    w = (SLIDE_W - 2 * MARGIN) // 2
    _textbox(slide, "lay-footer-label", MARGIN, y, w, h, lang, [label], list(glossary),
             FOOTER_PT, color=COLORS["muted"], anchor=MSO_ANCHOR.MIDDLE)
    _textbox(slide, "lay-footer-num", MARGIN + w, y, w, h, lang, [str(number)], [],
             FOOTER_PT, color=COLORS["muted"], anchor=MSO_ANCHOR.MIDDLE,
             align=PP_ALIGN.LEFT if lang == "he" else PP_ALIGN.RIGHT)


def _frame(slide, s, lang, glossary, title=True, bg="bg.png"):
    """Background, title, tip band. Returns the (unmirrored) content box."""
    _background(slide, bg)
    if title:
        _title(slide, s, lang, glossary)
    x, y, w, h = content_box(s.tip is not None)
    if s.tip:
        add_tip(slide, getattr(s.tip, lang), lang, glossary, s.id)
        h -= TIP_GAP
    return x, y, w, h


def _bullets(s, lang):
    return [getattr(b, lang) for b in s.bullets]


def _bullet_box(slide, box, s, lang, glossary, size=BODY_PT, space=BULLET_SPACE):
    if not s.bullets:
        return
    x, y, w, h = box
    _textbox(slide, "lay-body", x, y, w, h, lang, _bullets(s, lang), glossary,
             size, bullet=True, fit=(s.id, "bullets"), space=space)


# --- layouts ---------------------------------------------------------------

def _centered(slide, s, lang, glossary, title_pt, sub_color):
    x, y, w, h = _frame(slide, s, lang, glossary, title=False, bg=TITLE_BG)
    title_h = Inches(1.6)
    ty = y + (h - title_h) // 2 - Inches(1.2)
    tb = _textbox(slide, "lay-title", x, ty, w, title_h, lang, [_t(s.title, lang)],
                  glossary, title_pt, bold=True, align=PP_ALIGN.CENTER,
                  anchor=MSO_ANCHOR.BOTTOM, fit=(s.id, "title"), min_pt=TITLE_PT_MIN)
    _head_font(tb, lang)
    rule_w = Inches(1.6)
    _rect(slide, "lay-title-rule", x + (w - rule_w) // 2, ty + title_h + Inches(0.1),
          rule_w, Inches(0.06), lang, "accent", kind=MSO_SHAPE.RECTANGLE)
    if s.bullets:
        sy = ty + title_h + Inches(0.35)
        _textbox(slide, "lay-body", x, sy, w, y + h - sy, lang, _bullets(s, lang),
                 glossary, SMALL_PT, color=COLORS[sub_color], align=PP_ALIGN.CENTER,
                 fit=(s.id, "bullets"))


TITLE_BG = "bg-title.png"
HERO_PT, HERO_PT_MIN = 66, 40
# keynote-style gradient for the accent words of the opening title
HERO_GRADIENT = ("0284C7", "4F46E5", "9333EA")


def _gradient_text(tb, stops=HERO_GRADIENT):
    """Replace each run's solid fill with a left-to-right linear gradient."""
    from lxml import etree
    from pptx.oxml.ns import qn
    for p in tb.text_frame.paragraphs:
        for r in p.runs:
            rpr = r._r.get_or_add_rPr()
            old = rpr.find(qn("a:solidFill"))
            grad = etree.Element(qn("a:gradFill"), rotWithShape="1")
            lst = etree.SubElement(grad, qn("a:gsLst"))
            for i, c in enumerate(stops):
                gs = etree.SubElement(lst, qn("a:gs"), pos=str(i * 100000 // (len(stops) - 1)))
                etree.SubElement(gs, qn("a:srgbClr"), val=c)
            etree.SubElement(grad, qn("a:lin"), ang="0", scaled="0")
            if old is not None:
                old.addprevious(grad)
                rpr.remove(old)
            else:
                rpr.insert(0, grad)


def _tracking(tb, hundredths_pt):
    for p in tb.text_frame.paragraphs:
        for r in p.runs:
            r._r.get_or_add_rPr().set("spc", str(hundredths_pt))


def title(slide, s, lang, glossary):
    """Opening slide, keynote style: dark stage with a horizon of light, a small
    tracked eyebrow, a huge title whose accent words glow in a gradient on
    their own line, a one-line promise, and the credit at the bottom."""
    _background(slide, TITLE_BG)
    x, w = MARGIN, SLIDE_W - 2 * MARGIN
    full = _t(s.title, lang)
    accent = _t(s.extra.get("accent"), lang)
    head, tail = (full[: -len(accent)].rstrip(), accent) \
        if accent and full.endswith(accent) else (full, "")
    line_h = Inches(1.15)
    y = Inches(1.2)
    eyebrow = _t(s.extra.get("eyebrow"), lang)
    if eyebrow:
        eb = _textbox(slide, "lay-eyebrow", x, y, w, Inches(0.5), lang, [eyebrow],
                      glossary, 18, bold=True, color=COLORS["accent2"],
                      align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                      fit=(s.id, "eyebrow"), max_lines=1)
        if lang == "en":  # letter-spacing suits Latin caps, not Hebrew
            _tracking(eb, 300)
    y += Inches(0.6)
    tb = _textbox(slide, "lay-title", x, y, w, line_h, lang, [head], glossary, HERO_PT,
                  bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                  fit=(s.id, "title"), min_pt=TITLE_PT_MIN)
    _head_font(tb, lang)
    y += line_h
    if tail:
        tb2 = _textbox(slide, "lay-title-accent", x, y, w, line_h, lang, [tail], glossary,
                       HERO_PT, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                       fit=(s.id, "title"), min_pt=TITLE_PT_MIN)
        _head_font(tb2, lang)
        _gradient_text(tb2)
        y += line_h
    bottom = SLIDE_H - MARGIN
    if s.tip:
        add_tip(slide, getattr(s.tip, lang), lang, glossary, s.id)
        bottom = tip_box()[1] - TIP_GAP
    items = _bullets(s, lang)
    sub_h = Inches(0.6)
    if items:
        _textbox(slide, "lay-body", x, y + Inches(0.15), w, sub_h, lang, [items[0]],
                 glossary, 24, color=COLORS["text"], align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, fit=(s.id, "subtitle"))
    if len(items) > 1:
        cy = y + Inches(0.15) + sub_h + Inches(0.2)
        _textbox(slide, "lay-credit", x, cy, w, bottom - cy, lang, items[1:], glossary, 14,
                 color=COLORS["muted"], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM,
                 fit=(s.id, "credit"))


def section(slide, s, lang, glossary):
    _centered(slide, s, lang, glossary, 44, "accent2")


def bullets(slide, s, lang, glossary):
    box = _frame(slide, s, lang, glossary)
    _bullet_box(slide, box, s, lang, glossary)


def bullets_diagram(slide, s, lang, glossary):
    """Short bullet strip on top, diagram below in the rest of the content box."""
    x, y, w, h = _frame(slide, s, lang, glossary)
    if s.bullets:
        tw = w - FRAME_INSET_H - BULLET_INDENT
        lines = sum(est_lines(t, tw, SMALL_PT) for t in _bullets(s, lang))
        strip = est_height(lines, SMALL_PT) + FRAME_INSET_V
        # no bullet spacing here: the diagram needs the height
        _bullet_box(slide, (x, y, w, strip), s, lang, glossary, SMALL_PT, space=0)
        y, h = y + strip + Inches(0.15), h - strip - Inches(0.15)
        if s.diagram and h < DIAGRAM_MIN_H:
            raise ValueError(f"{s.id}: bullets leave {h / 914400:.2f}in for the "
                             f"diagram (min {DIAGRAM_MIN_H / 914400:.1f}in)")
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
                 bold=True, color=COLORS["accent2"], anchor=MSO_ANCHOR.MIDDLE,
                 fit=(s.id, f"columns[{i}].heading"))
        items = [_t(it, lang) for it in col.get("items") or []]
        if items:
            _textbox(slide, f"lay-col{i}-body", cx + pad, y + head_h, cw - 2 * pad,
                     h - head_h - pad, lang, items, glossary, SMALL_PT, bullet=True,
                     fit=(s.id, f"columns[{i}].items"))


def _table_fit(s, rows, col_w, max_h, lang):
    """Largest font (18pt down to 14pt) whose estimated table height fits
    max_h. Returns (row heights, size); raises ValueError if nothing fits."""
    tw = col_w - CELL_INSET_H
    for size in range(TABLE_PT_MAX, TABLE_PT_MIN - 1, -1):
        est = [max(est_height(est_lines(_t(c, lang), tw, size, bold=r == 0), size)
                   for c in row) + CELL_INSET_V for r, row in enumerate(rows)]
        if sum(est) <= max_h:
            pad = min(Inches(0.6), max_h // len(rows))
            roomy = [max(e, pad) for e in est]
            return (roomy if sum(roomy) <= max_h else est), size
    raise ValueError(f"{s.id}: table text too long to fit at {TABLE_PT_MIN}pt; "
                     "shorten the cells or split the table")


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
    heights, size = _table_fit(s, rows, w // len(header), h, lang)
    gf = slide.shapes.add_table(len(rows), len(header), int(x), int(y), int(w),
                                int(sum(heights)))
    gf.name = "lay-table"
    tbl = gf.table
    for c in range(len(header)):
        tbl.columns[c].width = Emu(w // len(header))
    for r, row in enumerate(rows):
        tbl.rows[r].height = Emu(heights[r])
        for c, src in enumerate(order):
            cell = tbl.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLORS["accent"] if r == 0 else COLORS["surface"]
            write_paragraphs(cell.text_frame, [_t(row[src], lang)], lang, size, glossary,
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
                 anchor=MSO_ANCHOR.MIDDLE, fit=(s.id, f"images[{i}].caption"))


def code(slide, s, lang, glossary):
    """Bullets on the reading-start side, a dark code card on the other side.
    Code is always LTR (mono font, no RTL)."""
    x, y, w, h = _frame(slide, s, lang, glossary)
    text_w = int(w * CODE_TEXT_FRAC) if s.bullets else 0
    if s.bullets:
        _bullet_box(slide, (x, y, text_w, h), s, lang, glossary, SMALL_PT)
    cx = x + text_w + (GAP if s.bullets else 0)
    cw = x + w - cx
    _rect(slide, "lay-code-card", cx, y, cw, h, lang, "code_bg", line="accent")
    pad = Inches(0.25)
    src = s.extra.get("code", "")
    fit = (s.id, "code", [src], cw - 2 * pad, h - 2 * pad, CODE_PT)
    try:  # prefer a size at which no source line wraps
        size = fit_size(*fit, char_em=MONO_EM, max_lines=len(src.split("\n")))
    except ValueError:
        size = fit_size(*fit, char_em=MONO_EM)
    tb = slide.shapes.add_textbox(int(_mx(cx + pad, cw - 2 * pad, lang)), int(y + pad),
                                  int(cw - 2 * pad), int(h - 2 * pad))
    tb.name = "lay-code"
    tf = tb.text_frame
    write_paragraphs(tf, [src], "en", size, [], bullet=False,
                     color=COLORS["code_text"])
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    for p in tf.paragraphs:
        for r in p.runs:
            r.font.name = FONTS["en"]["mono"]


LAYOUTS = {
    "title": title,
    "divider": title,  # part dividers share the keynote cover
    "section": section,
    "bullets": bullets,
    "bullets-diagram": bullets_diagram,
    "compare": compare,
    "table": table,
    "photos": photos,
    "code": code,
}
