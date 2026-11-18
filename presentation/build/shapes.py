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
    _text(sh, text, lang, [], 18, COLORS["bg"], bold=True)
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


# (question, outcome, edge label key). Source article rule: skip GSD if
# sessions are short AND a human reviews each phase; skip Superpowers if the
# team already has strong TDD habits.
DECISION_EDGES = [
    ("q_long", "add_gsd", "yes"),
    ("q_review", "add_gsd", "no"),
    ("q_tdd", "add_superpowers", "no"),
]
_DECISION_CHAIN = [("q_long", "q_review", "no"), ("q_review", "q_tdd", "yes")]


def _edge_label(slide, diagram, key, lang, glossary, cx, cy):
    w, h = Inches(0.6), Inches(0.4)
    tb = slide.shapes.add_textbox(int(cx - w // 2), int(cy - h // 2), w, h)
    tb.name = f"edge-{key}"
    _text(tb, _label(diagram, key, lang), lang, glossary, 18, COLORS["muted"],
          bold=True)
    tb.text_frame.margin_left = tb.text_frame.margin_right = 0
    return tb


def decision(slide, area, diagram, lang, glossary):
    """Three diamond questions in a row (yes/no edges); outcomes below."""
    x, y, w, h = area
    gap = Inches(0.6)
    dw = (w - 2 * gap) // 3
    dh = Inches(2.4)
    oh = Inches(0.9)
    ow = Inches(2.9)
    oy = y + h - oh
    qs = {}
    for i, k in enumerate(["q_long", "q_review", "q_tdd"]):
        d = _box(slide, MSO_SHAPE.DIAMOND, x + i * (dw + gap), y, dw, dh,
                 f"q-{k}", _label(diagram, k, lang), lang, glossary, 18)
        d.text_frame.margin_left = d.text_frame.margin_right = 0
        d.text_frame.margin_top = d.text_frame.margin_bottom = 0
        qs[k] = d
    for a_, b_, lab in _DECISION_CHAIN:
        _arrow(slide, qs[a_], _RIGHT, qs[b_], _LEFT)
        _edge_label(slide, diagram, lab, lang, glossary,
                    qs[a_].left + qs[a_].width + gap // 2, y + dh // 2 - Inches(0.3))
    outs = {}
    for k, qk, cx in (("add_gsd", "q_long", x + (dw - ow) // 2),
                      ("add_superpowers", "q_tdd", x + w - dw + (dw - ow) // 2)):
        outs[k] = _box(slide, MSO_SHAPE.ROUNDED_RECTANGLE, cx, oy, ow, oh,
                       f"out-{k}", _label(diagram, k, lang), lang, glossary, 24,
                       fill="accent", bold=True)
    for q, out, lab in DECISION_EDGES:
        _arrow(slide, qs[q], _BOTTOM, outs[out], _TOP)
        qb, ot = qs[q], outs[out]
        mx = (qb.left + qb.width // 2 + ot.left + ot.width // 2) // 2
        _edge_label(slide, diagram, lab, lang, glossary,
                    mx + Inches(0.4), (qb.top + qb.height + ot.top) // 2)


_FLOW = ["issue", "feature", "pr3", "dev", "prs", "main"]


def branch_flow(slide, area, diagram, lang, glossary):
    """Six nodes zig-zagging over two rows, always left to right (also in HE)."""
    x, y, w, h = area
    highlight = set(diagram.get("highlight") or [])
    nw = Inches(3.4)
    nh = min(Inches(1.6), h // 3)
    step = (w - nw) // (len(_FLOW) - 1)
    row_y = [y, y + h - nh]
    nodes = []
    for i, k in enumerate(_FLOW):
        nodes.append(_box(
            slide, MSO_SHAPE.ROUNDED_RECTANGLE, x + i * step, row_y[i % 2], nw,
            nh, f"node-{k}", _label(diagram, k, lang), lang, glossary, 18,
            fill="accent" if k in highlight else "surface", bold=k in highlight))
    for i in range(len(nodes) - 1):
        if i % 2 == 0:
            _arrow(slide, nodes[i], _BOTTOM, nodes[i + 1], _TOP)
        else:
            _arrow(slide, nodes[i], _TOP, nodes[i + 1], _BOTTOM)


DIAGRAMS = {"layers": layers, "decision": decision, "branch-flow": branch_flow}
