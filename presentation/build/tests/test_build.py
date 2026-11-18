from pathlib import Path

import pytest
from pptx import Presentation
from pptx.enum.text import MSO_AUTO_SIZE

from presentation.build.model import Bullet, Slide, Tip, load_deck
from presentation.build.shapes import DIAGRAMS
from presentation.build.theme import SLIDE_H, SLIDE_W, tip_box
from presentation.build.validate import validate

ROOT = Path(__file__).resolve().parents[3]
DECK = ROOT / "presentation" / "content" / "deck.yaml"
LAYOUT_SHAPE = "lay-"


@pytest.fixture(scope="module")
def decks(tmp_path_factory):
    from presentation.build.build_decks import build
    d = tmp_path_factory.mktemp("decks")
    out = {}
    for lang in ("en", "he"):
        p = d / f"{lang}.pptx"
        build(str(DECK), lang, str(p))
        out[lang] = Presentation(str(p))
    return out


def _notes(slide):
    return slide.notes_slide.notes_text_frame.text


def _shape(slide, name):
    return next(sh for sh in slide.shapes if sh.name == name)


def test_skeleton_validates():
    assert validate(load_deck(DECK), set(DIAGRAMS)) == []


def test_build_both_langs(decks):
    ids = [s.id for s in load_deck(DECK).slides]
    assert len(ids) == 33
    for lang in ("en", "he"):
        prs = decks[lang]
        assert len(prs.slides) == 33
        assert (prs.slide_width, prs.slide_height) == (SLIDE_W, SLIDE_H)
        got = [s.name for s in prs.slides]  # slide name == slide id
        assert got == ids


def test_notes_prefix_and_end(decks):
    for lang in ("en", "he"):
        sl = decks[lang].slides
        assert _notes(sl[26]).startswith("[3:00] [@45:00]")
        assert _notes(sl[27]).startswith("[backup, not timed]")


def _all_text(prs):
    out = []
    for s in prs.slides:
        for sh in s.shapes:
            if sh.has_text_frame:
                out.append(sh.text_frame.text)
            if sh.has_table:
                out += [c.text_frame.text for r in sh.table.rows for c in r.cells]
    return out


def test_tip_pill_label_english_in_he(decks):
    he = decks["he"]
    pills = [_shape(s, "lay-tip-pill") for s in he.slides
             if any(sh.name == "lay-tip-pill" for sh in s.shapes)]
    assert len(pills) >= 10
    assert all(p.text_frame.text == "TIP" for p in pills)
    assert not any("טיפ" in t for t in _all_text(he))


def test_tip_band_mirrored(decks):
    for lang, left_half in (("en", True), ("he", False)):
        n = 0
        for s in decks[lang].slides:
            for sh in s.shapes:
                if sh.name == "lay-tip-pill":
                    n += 1
                    assert (sh.left < SLIDE_W / 2) is left_half, (lang, s.name)
        assert n >= 10


def test_diagram_area_above_tip_band(decks):
    band_top = tip_box()[1]
    checked = 0
    for lang in ("en", "he"):
        for s in decks[lang].slides:
            names = [sh.name for sh in s.shapes]
            if "lay-tip-pill" not in names:
                continue
            dg = [sh for sh in s.shapes if not sh.name.startswith(LAYOUT_SHAPE)]
            if not dg:
                continue
            checked += 1
            assert max(sh.top + sh.height for sh in dg) <= band_top, (lang, s.name)
    assert checked >= 2


LONG = "Long placeholder text that keeps going to sixty characters!!"
LONG_HE = "טקסט ארוך מאוד שממשיך וממשיך עד שהוא מגיע לשישים תווים בדיוק"
TIP20 = " ".join(["word"] * 20)


def _long_slide(layout):
    assert len(LONG) == 60
    pair = {"en": LONG, "he": LONG_HE}
    extra = {
        "columns": [{"heading": pair, "items": [pair] * 4}] * 2,
        "table": {"header": [pair] * 3, "rows": [[pair] * 3] * 4},
        "images": [{"file": "photo-ok.jpg", "caption": pair},
                   {"file": "photo-warning.jpg", "caption": pair}],
        "code": "\n".join([LONG] * 8),
    }
    diagram = {"name": "branch-flow", "highlight": ["dev"]} \
        if layout == "bullets-diagram" else None
    return Slide(
        id=f"long-{layout}", part="I", budget_s=60, layout=layout,
        title=pair, bullets=[Bullet(f"b{i}", LONG, LONG_HE) for i in range(5)],
        tip=Tip("t", TIP20, TIP20), notes={"en": "", "he": ""},
        diagram=diagram, sources=[], appendix=False, extra=extra)


@pytest.mark.parametrize("lang", ["en", "he"])
@pytest.mark.parametrize("layout", ["title", "section", "bullets", "bullets-diagram",
                                    "compare", "table", "photos", "code"])
def test_layouts_fit_long_text(layout, lang):
    from presentation.build.build_decks import new_presentation
    from presentation.build.layouts import LAYOUTS
    prs = new_presentation()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    LAYOUTS[layout](s, _long_slide(layout), lang, [])
    frames = [sh for sh in s.shapes if sh.name.startswith(LAYOUT_SHAPE)
              and sh.has_text_frame and sh.text_frame.text.strip()
              and sh.name != "lay-tip-pill"]
    assert any(sh.name == "lay-tip-text" for sh in frames)
    for sh in frames:
        assert sh.text_frame.auto_size == MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE, sh.name
    sizes = [r.font.size.pt for sh in s.shapes if sh.has_text_frame
             for p in sh.text_frame.paragraphs for r in p.runs]
    sizes += [r.font.size.pt for sh in s.shapes if sh.has_table
              for row in sh.table.rows for c in row.cells
              for p in c.text_frame.paragraphs for r in p.runs]
    assert sizes and min(sizes) >= 14
    for sh in s.shapes:  # everything stays on the slide
        assert sh.left >= 0 and sh.top >= 0, sh.name
        assert sh.left + sh.width <= SLIDE_W and sh.top + sh.height <= SLIDE_H, sh.name


def _paragraphs(sh):
    if sh.has_text_frame:
        yield from sh.text_frame.paragraphs
    if sh.has_table:
        for r in sh.table.rows:
            for c in r.cells:
                yield from c.text_frame.paragraphs


def test_he_text_is_rtl(decks):
    n = 0
    for s in decks["he"].slides:
        for sh in s.shapes:
            if sh.name == "lay-code":
                continue
            for p in _paragraphs(sh):
                if not p.text.strip():
                    continue
                n += 1
                pPr = p._p.pPr
                assert pPr is not None and pPr.get("rtl") == "1", (s.name, sh.name, p.text)
    assert n > 100


def test_en_text_is_not_rtl(decks):
    for s in decks["en"].slides:
        for sh in s.shapes:
            for p in _paragraphs(sh):
                assert p._p.pPr is None or p._p.pPr.get("rtl") != "1"


# --- fix round 1: table bound, bullet strip, title gap ----------------------

from pptx.util import Inches  # noqa: E402

from presentation.build.theme import content_box  # noqa: E402


def _render(slide_obj, lang="en"):
    from presentation.build.build_decks import new_presentation
    from presentation.build.layouts import LAYOUTS
    prs = new_presentation()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    LAYOUTS[slide_obj.layout](s, slide_obj, lang, [])
    return s


def _table_slide(ncols, text_en, text_he, nrows=7):
    s = _long_slide("table")
    cell = {"en": text_en, "he": text_he}
    s.extra["table"] = {"header": [cell] * ncols, "rows": [[cell] * ncols] * nrows}
    return s


def _table_sizes(sl):
    t = _shape(sl, "lay-table")
    return t, [r.font.size.pt for row in t.table.rows for c in row.cells
               for p in c.text_frame.paragraphs for r in p.runs]


@pytest.mark.parametrize("lang", ["en", "he"])
def test_table_7_rows_fits_by_downsizing(lang):
    s = _table_slide(2, LONG, LONG_HE)
    sl = _render(s, lang)
    t, sizes = _table_sizes(sl)
    assert 14 <= min(sizes) and max(sizes) < 18
    assert t.top + sum(r.height for r in t.table.rows) <= tip_box()[1]


def test_table_7_rows_too_long_raises():
    s = _table_slide(3, LONG + " " + LONG, LONG_HE + " " + LONG_HE)
    with pytest.raises(ValueError, match="long-table"):
        _render(s)


def test_table_short_keeps_18pt():
    s = _table_slide(2, "short", "קצר", nrows=3)
    _, sizes = _table_sizes(_render(s))
    assert set(sizes) == {18}


@pytest.mark.parametrize("lang", ["en", "he"])
def test_bullet_strip_does_not_overlap_diagram(lang):
    s = _long_slide("bullets-diagram")
    two_line = LONG + " " + LONG + " and more"  # ~130 chars: two lines at 20pt
    s.bullets = [Bullet("a", two_line, two_line), Bullet("b", two_line, two_line)]
    sl = _render(s, lang)
    body = _shape(sl, "lay-body")
    dg = [sh for sh in sl.shapes if not sh.name.startswith(LAYOUT_SHAPE)]
    assert dg
    assert body.top + body.height <= min(sh.top for sh in dg)
    assert body.height >= 4 * Inches(20 * 1.2 / 72)  # room for 4 lines


@pytest.mark.parametrize("layout", ["bullets", "bullets-diagram", "compare", "table",
                                    "photos", "code"])
def test_title_gap(layout):
    sl = _render(_long_slide(layout))
    t = _shape(sl, "lay-title")
    assert t.top + t.height + Inches(0.1) <= content_box(True)[1]
