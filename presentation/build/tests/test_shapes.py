import pytest
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

from presentation.build.shapes import DIAGRAMS, pill
from presentation.build.theme import COLORS, content_box

KEYS = ["issue", "feature", "pr3", "dev", "prs", "main"]
AREA = content_box(False)


def _slide():
    prs = Presentation()
    return prs.slides.add_slide(prs.slide_layouts[6])


def _labels(keys):
    return {k: {"en": f"EN {k}", "he": f"HE {k}"} for k in keys}


def _build(name, lang="en", highlight=None, keys=()):
    s = _slide()
    d = {"name": name, "highlight": highlight or [], "labels": _labels(keys)}
    DIAGRAMS[name](s, AREA, d, lang, [])
    return s


def _nodes(s):
    return {sh.name: sh for sh in s.shapes if sh.name.startswith("node-")}


def test_registry_has_p1_keys():
    assert {"layers", "decision", "branch-flow"} <= set(DIAGRAMS)


def test_layers_shape_budget():
    s = _build("layers", keys=["bmad", "speckit", "gsd", "superpowers", "band_plan", "band_exec"])
    texty = [sh for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    boxes = [sh for sh in texty if sh.shape_type == 1]  # AUTO_SHAPE
    assert len(boxes) <= 4
    assert len(texty) <= 6
    sizes = [r.font.size.pt for sh in texty for p in sh.text_frame.paragraphs for r in p.runs]
    assert sizes and min(sizes) >= 24


def test_decision_has_three_questions():
    s = _build("decision", keys=["q_long", "q_review", "q_tdd", "add_gsd", "add_superpowers"])
    d = [sh for sh in s.shapes if sh.shape_type == 1 and sh.auto_shape_type == MSO_SHAPE.DIAMOND]
    assert len(d) == 3


def test_branch_flow_nodes_and_highlight():
    s = _build("branch-flow", highlight=["dev", "main"], keys=KEYS)
    nodes = _nodes(s)
    assert list(nodes) == [f"node-{k}" for k in KEYS]
    for k in KEYS:
        n = nodes[f"node-{k}"]
        assert n.text_frame.text == f"EN {k}"
        want = COLORS["accent"] if k in ("dev", "main") else COLORS["surface"]
        assert n.fill.fore_color.rgb == want


@pytest.mark.parametrize("lang", ["en", "he"])
def test_branch_flow_ltr(lang):
    s = _build("branch-flow", lang=lang, keys=KEYS)
    xs = [_nodes(s)[f"node-{k}"].left for k in KEYS]
    assert xs == sorted(xs) and len(set(xs)) == 6
    assert _nodes(s)["node-issue"].text_frame.text == f"{lang.upper()} issue"


def test_missing_label_falls_back_to_key():
    s = _slide()
    DIAGRAMS["branch-flow"](s, AREA, {"name": "branch-flow", "highlight": []}, "en", [])
    assert _nodes(s)["node-dev"].text_frame.text == "dev"


@pytest.mark.parametrize("name", ["layers", "decision", "branch-flow"])
@pytest.mark.parametrize("lang", ["en", "he"])
def test_diagram_area_respected(name, lang):
    s = _build(name, lang=lang, keys=KEYS)
    l, t, w, h = AREA
    assert len(s.shapes) > 0
    for sh in s.shapes:
        assert sh.left >= l and sh.top >= t, sh.name
        assert sh.left + sh.width <= l + w and sh.top + sh.height <= t + h, sh.name


def test_pill():
    s = _slide()
    p = pill(s, Inches(1), Inches(1), "TIP", "he")
    assert p.text_frame.text == "TIP"
    assert p.fill.fore_color.rgb == COLORS["tip"]
