import pytest
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

from presentation.build.shapes import DECISION_EDGES, DIAGRAMS, pill
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


def _all_runs(s):
    return [r for sh in s.shapes if sh.has_text_frame
            for p in sh.text_frame.paragraphs for r in p.runs]


ALLKEYS = KEYS + ["band_plan", "band_exec", "bmad", "speckit", "gsd", "superpowers",
                  "q_long", "q_review", "q_tdd", "add_gsd", "add_superpowers",
                  "yes", "no"]


@pytest.mark.parametrize("name", ["layers", "decision", "branch-flow"])
@pytest.mark.parametrize("lang", ["en", "he"])
def test_min_font_18(name, lang):
    s = _build(name, lang=lang, keys=ALLKEYS)
    runs = _all_runs(s)
    assert runs and min(r.font.size.pt for r in runs) >= 18


def test_pill_font_18():
    s = _slide()
    pill(s, 0, 0, "TIP", "en")
    assert min(r.font.size.pt for r in _all_runs(s)) >= 18


def _connectors(s):
    names = {sh.shape_id: sh.name for sh in s.shapes}
    out = []
    for sh in s.shapes:
        st = sh._element.xpath(".//a:stCxn/@id")
        en = sh._element.xpath(".//a:endCxn/@id")
        if st and en:
            out.append((names[int(st[0])], names[int(en[0])]))
    return out


def _pref(k):
    return ("q-" if k.startswith("q_") else "out-") + k


def test_decision_two_independent_tracks():
    s = _build("decision", keys=ALLKEYS + ["track_context", "track_discipline",
                                           "skip_gsd", "skip_superpowers"])
    got = _connectors(s)
    assert sorted(got) == sorted((_pref(a), _pref(b)) for a, b, _ in DECISION_EDGES)
    gsd = {"q-q_long", "q-q_review", "out-add_gsd", "out-skip_gsd"}
    sp = {"q-q_tdd", "out-add_superpowers", "out-skip_superpowers"}
    for a, b in got:  # no connector crosses tracks
        assert ({a, b} <= gsd) or ({a, b} <= sp)
    # Q3 unreachable from Q1/Q2 (and vice versa): graph components are disjoint
    reach = {"q-q_long"}
    for _ in got:
        reach |= {b for a, b in got if a in reach}
    assert "q-q_tdd" not in reach and "out-add_superpowers" not in reach
    # every question has both a yes and a no outgoing edge
    for q in ("q_long", "q_review", "q_tdd"):
        assert {l for a, _, l in DECISION_EDGES if a == q} == {"yes", "no"}
    # article rule
    assert ("q_long", "add_gsd", "yes") in DECISION_EDGES
    assert ("q_review", "add_gsd", "no") in DECISION_EDGES
    assert ("q_review", "skip_gsd", "yes") in DECISION_EDGES
    assert ("q_tdd", "add_superpowers", "no") in DECISION_EDGES
    assert ("q_tdd", "skip_superpowers", "yes") in DECISION_EDGES
    labels = sorted(sh.text_frame.text for sh in s.shapes if sh.name.startswith("edge-"))
    assert labels == ["EN no"] * 3 + ["EN yes"] * 3
    tracks = {sh.text_frame.text for sh in s.shapes if sh.name.startswith("track-")}
    assert tracks == {"EN track_context", "EN track_discipline"}


def test_decision_missing_labels_fall_back():
    s = _slide()
    DIAGRAMS["decision"](s, AREA, {"name": "decision"}, "he", [])
    assert any(sh.text_frame.text == "skip_gsd" for sh in s.shapes if sh.has_text_frame)


# ---- P2 diagrams (Task 7 part A) ----
P2 = ["sdlc-adlc", "sdd-pipeline", "context-rot", "team-roles"]
P2KEYS = ["sdlc_title", "adlc_title", "requirements", "design", "build", "test", "release",
          "intent", "agent_builds", "check", "correct",
          "constitution", "specify", "plan", "tasks", "implement", "clarify", "analyze",
          "feedback", "rail", "axis_quality", "axis_context", "rot_zone",
          "architect", "product_owner", "senior_dev", "human"]


def _by(s, prefix):
    return [sh for sh in s.shapes if sh.name.startswith(prefix)]


def test_registry_has_p2_keys():
    assert set(P2) <= set(DIAGRAMS)


def test_sdlc_adlc_has_linear_and_loop():
    s = _build("sdlc-adlc", keys=P2KEYS)
    chev = _by(s, "sdlc-step-")
    assert len(chev) == 5
    assert all(c.auto_shape_type == MSO_SHAPE.CHEVRON for c in chev)
    xs = [c.left for c in chev]
    assert xs == sorted(xs)
    steps = {sh.name for sh in _by(s, "adlc-step-")}
    assert len(steps) == 4
    edges = [(a, b) for a, b in _connectors(s) if a in steps and b in steps]
    assert len(edges) == 4
    nxt = dict(edges)
    assert set(nxt) == steps and set(nxt.values()) == steps
    cur, seen = next(iter(steps)), set()
    while cur not in seen:  # one single cycle through all four steps
        seen.add(cur)
        cur = nxt[cur]
    assert seen == steps


def test_sdd_pipeline_five_stages_two_gates_rail():
    s = _build("sdd-pipeline", keys=P2KEYS)
    stages = _by(s, "stage-")
    assert [x.name for x in stages] == [f"stage-{k}" for k in
            ["constitution", "specify", "plan", "tasks", "implement"]]
    xs = [x.left for x in stages]
    assert xs == sorted(xs)
    gates = _by(s, "gate-")
    assert {g.name for g in gates} == {"gate-clarify", "gate-analyze"}
    st = {x.name: x for x in stages}
    g = {x.name: x for x in gates}
    # clarify sits between specify and plan; analyze between tasks and implement
    assert st["stage-specify"].left < g["gate-clarify"].left + g["gate-clarify"].width // 2 < st["stage-plan"].left + st["stage-plan"].width
    assert st["stage-tasks"].left < g["gate-analyze"].left + g["gate-analyze"].width // 2 < st["stage-implement"].left + st["stage-implement"].width
    rail = _by(s, "rail")
    assert len(rail) == 1 and rail[0].width >= 0.9 * AREA[2]
    assert len(_by(s, "feedback")) == 1
    assert _by(s, "feedback")[0].top >= st["stage-implement"].top


def test_context_rot_no_numbers():
    s = _build("context-rot", keys=P2KEYS)
    runs = _all_runs(s)
    assert runs
    assert not any(ch.isdigit() for r in runs for ch in r.text)
    assert _by(s, "curve")


def test_team_roles_relay_via_architect():
    s = _build("team-roles", keys=P2KEYS)
    boxes = _by(s, "role-")
    assert len(boxes) in (3, 4)
    conns = _connectors(s)
    assert conns
    assert all("role-architect" in c for c in conns)
    assert not any({"role-po", "role-dev"} == set(c) for c in conns)
    assert {n for c in conns for n in c} >= {"role-architect", "role-po", "role-dev"}
    human = [c for c in conns if "role-human" in c]
    assert len(human) == 1  # human connects to the architect only
    arch = next(b for b in boxes if b.name == "role-architect")
    po = next(b for b in boxes if b.name == "role-po")
    dev = next(b for b in boxes if b.name == "role-dev")
    assert po.left < arch.left < dev.left


@pytest.mark.parametrize("name", P2)
@pytest.mark.parametrize("lang", ["en", "he"])
def test_p2_area_font_and_fallback(name, lang):
    s = _build(name, lang=lang, keys=P2KEYS)
    l, t, w, h = AREA
    for sh in s.shapes:
        assert sh.left >= l and sh.top >= t, sh.name
        assert sh.left + sh.width <= l + w and sh.top + sh.height <= t + h, sh.name
    assert min(r.font.size.pt for r in _all_runs(s)) >= 18
    s2 = _slide()  # no labels at all: falls back to keys, never raises
    DIAGRAMS[name](s2, AREA, {"name": name}, lang, [])
    assert len(s2.shapes) > 0
