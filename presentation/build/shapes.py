"""Native diagram builders (rounded rectangles, diamonds, connectors only).

Builder signature: builder(slide, area, diagram, lang, glossary) -> None
where area = (left, top, width, height) in EMU. Labels come from
diagram["labels"][key][lang]; a missing label falls back to the key.
"""
from lxml import etree
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

from .text import write_paragraphs
from .theme import COLORS

_TOP, _LEFT, _BOTTOM, _RIGHT = 0, 1, 2, 3  # connection sites


def _label(diagram, key, lang):
    return diagram.get("labels", {}).get(key, {}).get(lang) or key


def _text(shape, text, lang, glossary, size, color, bold=False):
    tf = shape.text_frame
    write_paragraphs(tf, [text], lang, size, glossary, bullet=False,
                     color=color, bold=bold)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for m in ("margin_left", "margin_right"):
        setattr(tf, m, Inches(0.08))
    for p in tf.paragraphs:
        p.alignment = PP_ALIGN.CENTER


def _box(slide, kind, x, y, w, h, name, text, lang, glossary, size,
         fill="surface", bold=False):
    sh = slide.shapes.add_shape(kind, int(x), int(y), int(w), int(h))
    sh.name = name
    sh.fill.solid()
    sh.fill.fore_color.rgb = COLORS[fill]
    sh.line.color.rgb = COLORS["accent"]
    sh.line.width = Pt(1.5)
    sh.shadow.inherit = False
    on_light = fill in ("accent", "tip")
    _text(sh, text, lang, glossary, size,
          COLORS["bg"] if on_light else COLORS["text"], bold)
    return sh


def _arrow(slide, a, site_a, b, site_b):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, 0, 0, 0, 0)
    c.begin_connect(a, site_a)
    c.end_connect(b, site_b)
    c.line.color.rgb = COLORS["muted"]
    c.line.width = Pt(2.5)
    ln = c.line._get_or_add_ln()
    etree.SubElement(ln, qn("a:tailEnd")).set("type", "triangle")
    return c


def pill(slide, x, y, text, lang):
    """Small rounded 'pill' badge (used for the TIP label)."""
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, int(x), int(y),
                                Inches(0.9), Inches(0.4))
    sh.adjustments[0] = 0.5
    sh.fill.solid()
    sh.fill.fore_color.rgb = COLORS["tip"]
    sh.line.fill.background()
    sh.shadow.inherit = False
    _text(sh, text, lang, [], 14, COLORS["bg"], bold=True)
    return sh


def layers(slide, area, diagram, lang, glossary):
    """Two bands (planning/governance, execution discipline), two boxes each."""
    x, y, w, h = area
    gap = Inches(0.3)
    label_h = Inches(0.6)
    box_h = (h - 2 * label_h - 3 * gap) // 2
    bw = (w - gap) // 2
    bands = [("band_plan", ["bmad", "speckit"]), ("band_exec", ["gsd", "superpowers"])]
    cy = y
    for band, keys in bands:
        tb = slide.shapes.add_textbox(x, cy, w, label_h)
        tb.name = f"band-{band}"
        _text(tb, _label(diagram, band, lang), lang, glossary, 24,
              COLORS["muted"], bold=True)
        cy += label_h
        for i, k in enumerate(keys):
            _box(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x + i * (bw + gap), cy,
                 bw, box_h, f"box-{k}", _label(diagram, k, lang), lang,
                 glossary, 24, bold=True)
        cy += box_h + gap


def decision(slide, area, diagram, lang, glossary):
    """Three diamond questions in a row; outcomes below."""
    x, y, w, h = area
    gap = Inches(0.5)
    dw = (w - 2 * gap) // 3
    dh = int(h * 0.5)
    oh = int(h * 0.25)
    ow = int(dw * 0.8)
    oy = y + h - oh
    qs = []
    for i, k in enumerate(["q_long", "q_review", "q_tdd"]):
        qs.append(_box(slide, MSO_SHAPE.DIAMOND, x + i * (dw + gap), y, dw, dh,
                       f"q-{k}", _label(diagram, k, lang), lang, glossary, 14))
        if i:
            _arrow(slide, qs[i - 1], _RIGHT, qs[i], _LEFT)
    gsd = _box(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x + (dw - ow) // 2, oy, ow, oh,
               "out-gsd", _label(diagram, "add_gsd", lang), lang, glossary, 24,
               fill="accent", bold=True)
    sp = _box(slide, MSO_SHAPE.ROUNDED_RECTANGLE,
              x + 2 * (dw + gap) + (dw - ow) // 2, oy, ow, oh, "out-superpowers",
              _label(diagram, "add_superpowers", lang), lang, glossary, 24,
              fill="accent", bold=True)
    _arrow(slide, qs[0], _BOTTOM, gsd, _TOP)
    _arrow(slide, qs[1], _BOTTOM, sp, _TOP)
    _arrow(slide, qs[2], _BOTTOM, sp, _TOP)


_FLOW = ["issue", "feature", "pr3", "dev", "prs", "main"]


def branch_flow(slide, area, diagram, lang, glossary):
    """Six nodes zig-zagging over two rows, always left to right (also in HE)."""
    x, y, w, h = area
    highlight = set(diagram.get("highlight") or [])
    nw = Inches(2.9)
    nh = min(Inches(1.3), h // 3)
    step = (w - nw) // (len(_FLOW) - 1)
    row_y = [y + (h // 2 - nh) // 2, y + h // 2 + (h // 2 - nh) // 2]
    nodes = []
    for i, k in enumerate(_FLOW):
        nodes.append(_box(
            slide, MSO_SHAPE.ROUNDED_RECTANGLE, x + i * step, row_y[i % 2], nw,
            nh, f"node-{k}", _label(diagram, k, lang), lang, glossary, 16,
            fill="accent" if k in highlight else "surface", bold=k in highlight))
    for i in range(len(nodes) - 1):
        if i % 2 == 0:
            _arrow(slide, nodes[i], _BOTTOM, nodes[i + 1], _TOP)
        else:
            _arrow(slide, nodes[i], _TOP, nodes[i + 1], _BOTTOM)


DIAGRAMS = {"layers": layers, "decision": decision, "branch-flow": branch_flow}
