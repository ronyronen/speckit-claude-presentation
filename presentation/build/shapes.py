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
    oh = Inches(1.0)
    # Diamonds shrink on short areas so the connectors (and their labels)
    # keep at least 0.9in of vertical room.
    dw = Inches(3.0)
    dh = min(Inches(2.6), h - lab_h - Inches(0.1) - oh - Inches(0.9))
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
        if y1 == y2:  # horizontal: centred above the line
            mx, my = (x1 + x2) // 2, y1 - Inches(0.3)
        else:  # near the source end, beside the line on its travel side
            mx = x1 + (x2 - x1) * 3 // 10 + (Inches(0.35) if x2 >= x1 else -Inches(0.35))
            my = y1 + (y2 - y1) * 3 // 10
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


def _arrow2(slide, a, site_a, b, site_b):
    """Double-headed connector (relay in both directions)."""
    c = _arrow(slide, a, site_a, b, site_b)
    ln = c.line._get_or_add_ln()
    he = etree.Element(qn("a:headEnd"))
    he.set("type", "triangle")
    ln.insert(list(ln).index(ln.find(qn("a:tailEnd"))), he)
    return c


def _caption(slide, name, x, y, w, h, text, lang, glossary, color="muted", size=20):
    tb = slide.shapes.add_textbox(int(x), int(y), int(w), int(h))
    tb.name = name
    _text(tb, text, lang, glossary, size, COLORS[color], bold=True)
    return tb


def _polyline(slide, name, pts, color, width_pt, arrow=False):
    """Open freeform path (no fill) through pts, given in EMU."""
    fb = slide.shapes.build_freeform(int(pts[0][0]), int(pts[0][1]))
    fb.add_line_segments([(int(px), int(py)) for px, py in pts[1:]], close=False)
    sh = fb.convert_to_shape()
    sh.name = name
    sh.fill.background()
    sh.line.color.rgb = COLORS[color]
    sh.line.width = Pt(width_pt)
    sh.shadow.inherit = False
    if arrow:
        etree.SubElement(sh.line._get_or_add_ln(), qn("a:tailEnd")).set("type", "triangle")
    return sh


_SDLC = ["requirements", "design", "build", "test", "release"]
_ADLC = ["intent", "agent_builds", "check", "correct"]


def sdlc_adlc(slide, area, diagram, lang, glossary):
    """Left: SDLC as a staircase chevron chain. Right: ADLC as a 4-step loop."""
    x, y, w, h = area
    title_h = Inches(0.5)
    gap = Inches(0.5)
    lw = w * 11 // 20
    rw = w - lw - gap
    rx = x + lw + gap
    top = y + title_h + Inches(0.1)
    body_h = h - title_h - Inches(0.1)

    _caption(slide, "sdlc-title", x, y, lw, title_h,
             _label(diagram, "sdlc_title", lang), lang, glossary, "accent2")
    _caption(slide, "adlc-title", rx, y, rw, title_h,
             _label(diagram, "adlc_title", lang), lang, glossary, "accent2")

    n = len(_SDLC)
    cw = Inches(3.2)
    dx = (lw - cw) // (n - 1)
    ch = min(Inches(0.85), (body_h - (n - 1) * Inches(0.1)) // n)
    dy = (body_h - ch) // (n - 1)
    for i, k in enumerate(_SDLC):
        _box(slide, MSO_SHAPE.CHEVRON, x + i * dx, top + i * dy, cw, ch,
             f"sdlc-step-{k}", _label(diagram, k, lang), lang, glossary, 20,
             fill="accent" if i == 0 else "surface", bold=True)

    bw, bh = Inches(2.3), Inches(0.9)
    cx = rx + (rw - bw) // 2
    my = top + (body_h - bh) // 2
    pos = {"intent": (cx, top), "agent_builds": (rx + rw - bw, my),
           "check": (cx, top + body_h - bh), "correct": (rx, my)}
    box = {k: _box(slide, MSO_SHAPE.ROUNDED_RECTANGLE, px, py, bw, bh,
                   f"adlc-step-{k}", _label(diagram, k, lang), lang, glossary, 20,
                   bold=True)
           for k, (px, py) in pos.items()}
    for (a, sa), (b, sb) in (
            (("intent", _RIGHT), ("agent_builds", _TOP)),
            (("agent_builds", _BOTTOM), ("check", _RIGHT)),
            (("check", _LEFT), ("correct", _BOTTOM)),
            (("correct", _TOP), ("intent", _LEFT))):
        _arrow(slide, box[a], sa, box[b], sb)


_SDD = ["constitution", "specify", "plan", "tasks", "implement"]


def sdd_pipeline(slide, area, diagram, lang, glossary):
    """Five stages, two gate pills, feedback loop back to specify, rail below."""
    x, y, w, h = area
    n = len(_SDD)
    sw = Inches(1.9)
    gap = (w - n * sw) // (n - 1)
    gate_h, gate_w = Inches(0.5), Inches(1.4)
    sh_ = Inches(1.0)
    rail_h = Inches(0.6)
    fb_drop = Inches(0.35)
    sy = y + gate_h + Inches(0.2)
    stages = {}
    for i, k in enumerate(_SDD):
        stages[k] = _box(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x + i * (sw + gap), sy,
                         sw, sh_, f"stage-{k}", _label(diagram, k, lang), lang,
                         glossary, 20, fill="accent" if k == "implement" else "surface",
                         bold=True)
    for a, b in zip(_SDD, _SDD[1:]):
        _arrow(slide, stages[a], _RIGHT, stages[b], _LEFT)
    for k, after in (("clarify", "specify"), ("analyze", "tasks")):
        cx = stages[after].left + stages[after].width + gap // 2
        g = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, int(cx - gate_w // 2),
                                   int(y), int(gate_w), int(gate_h))
        g.name = f"gate-{k}"
        g.adjustments[0] = 0.5
        g.fill.solid()
        g.fill.fore_color.rgb = COLORS["tip"]
        g.line.fill.background()
        g.shadow.inherit = False
        _text(g, _label(diagram, k, lang), lang, glossary, 18, COLORS["bg"], bold=True)
    # feedback: down from implement, left under the stages, up into specify
    by = sy + sh_
    fy = by + fb_drop
    ix = stages["implement"].left + stages["implement"].width // 2
    spx = stages["specify"].left + stages["specify"].width // 2
    _polyline(slide, "feedback", [(ix, by), (ix, fy), (spx, fy), (spx, by)],
              "warn", 2.5, arrow=True)
    _caption(slide, "caption-feedback", spx, fy, ix - spx, Inches(0.45),
             _label(diagram, "feedback", lang), lang, glossary, "warn")
    rail = _box(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y + h - rail_h, w, rail_h,
                "rail", _label(diagram, "rail", lang), lang, glossary, 20,
                fill="accent", bold=True)
    return rail


def context_rot(slide, area, diagram, lang, glossary):
    """Qualitative curve: quality falls as the context fills. Words only."""
    x, y, w, h = area
    lab_h = Inches(0.5)
    pad = Inches(0.1)
    ox, oy = x + pad, y + h - lab_h - pad       # axis origin
    top, right = y + lab_h + pad, x + w - pad
    _caption(slide, "axis-y-label", x, y, Inches(4.5), lab_h,
             _label(diagram, "axis_quality", lang), lang, glossary)
    _caption(slide, "axis-x-label", right - Inches(5.5), y + h - lab_h, Inches(5.5),
             lab_h, _label(diagram, "axis_context", lang), lang, glossary)
    for nm, (x1, y1, x2, y2) in (("axis-y", (ox, oy, ox, top)),
                                 ("axis-x", (ox, oy, right, oy))):
        c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, int(x1), int(y1),
                                       int(x2), int(y2))
        c.name = nm
        c.line.color.rgb = COLORS["muted"]
        c.line.width = Pt(2.5)
        etree.SubElement(c.line._get_or_add_ln(), qn("a:tailEnd")).set("type", "triangle")
    steps = 30
    pw, ph = (right - Inches(0.3)) - (ox + Inches(0.3)), (oy - Inches(0.3)) - (top + Inches(0.3))
    pts = []
    for i in range(steps + 1):
        t = i / steps
        pts.append((ox + Inches(0.3) + t * pw, top + Inches(0.3) + ph * (0.95 * t ** 1.1)))
    split = int(steps * 0.6)
    _polyline(slide, "curve", pts[:split + 1], "ok", 5)
    _polyline(slide, "curve-rot", pts[split:], "warn", 5)
    # caption above and to the right of the amber segment, clear of the line
    cap_w = Inches(3.0)
    _, ly = pts[int(steps * 0.8)]
    _caption(slide, "rot-zone", right - cap_w, ly - Inches(0.9), cap_w, lab_h,
             _label(diagram, "rot_zone", lang), lang, glossary, "warn")


def team_roles(slide, area, diagram, lang, glossary):
    """Human above architect; PO and dev either side; every link via architect."""
    x, y, w, h = area
    bw, bh = Inches(3.0), Inches(1.3)
    gap = (w - 3 * bw) // 2
    hy = y + Inches(0.2)
    ry = y + h - bh - Inches(0.6)

    def role(k, bx, by, key, fill="surface"):
        return _box(slide, MSO_SHAPE.ROUNDED_RECTANGLE, bx, by, bw, bh,
                    f"role-{k}", _label(diagram, key, lang), lang, glossary, 24,
                    fill=fill, bold=True)

    human = role("human", x + bw + gap, hy, "human")
    arch = role("architect", x + bw + gap, ry, "architect", "accent")
    po = role("po", x, ry, "product_owner")
    dev = role("dev", x + 2 * (bw + gap), ry, "senior_dev")
    _arrow2(slide, human, _BOTTOM, arch, _TOP)
    _arrow2(slide, arch, _LEFT, po, _RIGHT)
    _arrow2(slide, arch, _RIGHT, dev, _LEFT)


DIAGRAMS = {"layers": layers, "decision": decision, "branch-flow": branch_flow,
            "sdlc-adlc": sdlc_adlc, "sdd-pipeline": sdd_pipeline,
            "context-rot": context_rot, "team-roles": team_roles}
