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


# Two independent tracks (GSD and Superpowers are separate layers).
# (source, destination, label key). Article rule: skip GSD if sessions are
# short AND a human reviews each phase; skip Superpowers with strong TDD.
DECISION_EDGES = [
    ("q_long", "add_gsd", "yes"),
    ("q_long", "q_review", "no"),
    ("q_review", "add_gsd", "no"),
    ("q_review", "skip_gsd", "yes"),
    ("q_tdd", "add_superpowers", "no"),
    ("q_tdd", "skip_superpowers", "yes"),
]
# Connection sites (source site, destination site) per edge.
_EDGE_SITES = {
    ("q_long", "add_gsd"): (_BOTTOM, _TOP),
    ("q_long", "q_review"): (_RIGHT, _LEFT),
    ("q_review", "add_gsd"): (_BOTTOM, _TOP),
    ("q_review", "skip_gsd"): (_RIGHT, _TOP),
    ("q_tdd", "add_superpowers"): (_BOTTOM, _TOP),
    ("q_tdd", "skip_superpowers"): (_BOTTOM, _TOP),
}


def _site_xy(sh, site):
    return {_TOP: (sh.left + sh.width // 2, sh.top),
            _BOTTOM: (sh.left + sh.width // 2, sh.top + sh.height),
            _LEFT: (sh.left, sh.top + sh.height // 2),
            _RIGHT: (sh.left + sh.width, sh.top + sh.height // 2)}[site]


def _edge_label(slide, diagram, key, lang, glossary, cx, cy):
    w, h = Inches(0.6), Inches(0.4)
    tb = slide.shapes.add_textbox(int(cx - w // 2), int(cy - h // 2), w, h)
    tb.name = f"edge-{key}"
    _text(tb, _label(diagram, key, lang), lang, glossary, 18, COLORS["muted"],
          bold=True)
    tb.text_frame.margin_left = tb.text_frame.margin_right = 0
    return tb


def decision(slide, area, diagram, lang, glossary):
    """Left track: GSD (Q1, Q2). Right track: Superpowers (Q3). Independent."""
    x, y, w, h = area
    track_gap = Inches(0.5)
    lw = Inches(7.4)
    rw = w - lw - track_gap
    rx = x + lw + track_gap
    lab_h = Inches(0.5)
    dw, dh = Inches(3.0), Inches(2.6)
    oh = Inches(1.0)
    oy = y + h - oh
    dy = y + lab_h + Inches(0.1)

    for key, tx, tw in (("track_context", x, lw), ("track_discipline", rx, rw)):
        tb = slide.shapes.add_textbox(int(tx), int(y), int(tw), int(lab_h))
        tb.name = f"track-{key}"
        _text(tb, _label(diagram, key, lang), lang, glossary, 18,
              COLORS["accent2"], bold=True)

    def diamond(k, dx):
        d = _box(slide, MSO_SHAPE.DIAMOND, dx, dy, dw, dh, f"q-{k}",
                 _label(diagram, k, lang), lang, glossary, 18)
        tf = d.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0.05)
        return d

    def outcome(k, ox, ow, fill):
        return _box(slide, MSO_SHAPE.ROUNDED_RECTANGLE, ox, oy, ow, oh,
                    f"out-{k}", _label(diagram, k, lang), lang, glossary, 18,
                    fill=fill, bold=True)

    shapes = {
        "q_long": diamond("q_long", x),
        "q_review": diamond("q_review", x + dw + Inches(0.7)),
        "q_tdd": diamond("q_tdd", rx + (rw - dw) // 2),
        "add_gsd": outcome("add_gsd", x + Inches(1.6), Inches(2.4), "accent"),
        "skip_gsd": outcome("skip_gsd", x + lw - Inches(2.4), Inches(2.4), "surface"),
        "add_superpowers": outcome("add_superpowers", rx, (rw - Inches(0.15)) // 2, "accent"),
        "skip_superpowers": outcome("skip_superpowers", rx + (rw + Inches(0.15)) // 2,
                                    (rw - Inches(0.15)) // 2, "surface"),
    }
    for src, dst, lab in DECISION_EDGES:
        ss, ds = _EDGE_SITES[(src, dst)]
        _arrow(slide, shapes[src], ss, shapes[dst], ds)
        (x1, y1), (x2, y2) = _site_xy(shapes[src], ss), _site_xy(shapes[dst], ds)
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2
        if y1 == y2:
            my -= Inches(0.3)
        else:
            mx += Inches(0.4) if x2 >= x1 else -Inches(0.4)
        _edge_label(slide, diagram, lab, lang, glossary, mx, my)


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
