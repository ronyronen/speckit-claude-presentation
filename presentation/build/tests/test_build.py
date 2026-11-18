import re
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.enum.text import MSO_AUTO_SIZE

from presentation.build.model import Bullet, Slide, Tip, load_deck
from presentation.build.shapes import DIAGRAMS
from presentation.build.theme import SLIDE_H, SLIDE_W, tip_box
from presentation.build.validate import _he_term_re, validate

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
    assert len(ids) == 34
    for lang in ("en", "he"):
        prs = decks[lang]
        assert len(prs.slides) == 34
        assert (prs.slide_width, prs.slide_height) == (SLIDE_W, SLIDE_H)
        got = [s.name for s in prs.slides]  # slide name == slide id
        assert got == ids


def test_notes_prefix_and_end(decks):
    for lang in ("en", "he"):
        sl = decks[lang].slides
        assert _notes(sl[25]).startswith("[3:00] [@45:00]")
        assert _notes(sl[26]).startswith("[backup, not timed]")


def _all_text(prs):
    out = []
    for s in prs.slides:
        for sh in s.shapes:
            if sh.has_text_frame:
                out.append(sh.text_frame.text)
            if sh.has_table:
                out += [c.text_frame.text for r in sh.table.rows for c in r.cells]
    return out


def test_tip_is_bulb_icon_without_label(decks):
    """A tip shows a light-bulb picture and its text; no "TIP" word anywhere."""
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    for lang in ("en", "he"):
        icons = [_shape(s, "lay-tip-icon") for s in decks[lang].slides
                 if any(sh.name == "lay-tip-icon" for sh in s.shapes)]
        assert len(icons) >= 10
        assert all(i.shape_type == MSO_SHAPE_TYPE.PICTURE for i in icons)
        assert not any(re.search(r"\bTIP\b", t) for t in _all_text(decks[lang]))
    tip_re = _he_term_re("טיפ")
    assert not any(tip_re.search(t) for t in _all_text(decks["he"]))


def test_bulb_icon_asset_exists():
    from PIL import Image
    from presentation.build.theme import ASSETS
    im = Image.open(ASSETS / "tip-bulb.png")
    assert im.mode == "RGBA" and im.size[0] == im.size[1]


def test_footer_numbers_every_slide_but_title(decks):
    for lang in ("en", "he"):
        for n, s in enumerate(decks[lang].slides, 1):
            nums = [sh for sh in s.shapes if sh.name == "lay-footer-num"]
            if n == 1:
                assert not nums
            else:
                assert [x.text_frame.text.strip("\u200e\u200f") for x in nums] == [str(n)]


def test_tip_term_matcher_word_boundaries():
    tip_re = _he_term_re("טיפ")
    assert not tip_re.search("אב-טיפוס")
    assert tip_re.search("הטיפ")
    assert tip_re.search("טיפ")


def test_tip_band_mirrored(decks):
    for lang, left_half in (("en", True), ("he", False)):
        n = 0
        for s in decks[lang].slides:
            for sh in s.shapes:
                if sh.name == "lay-tip-icon":
                    n += 1
                    assert (sh.left < SLIDE_W / 2) is left_half, (lang, s.name)
        assert n >= 10


def test_diagram_area_above_tip_band(decks):
    band_top = tip_box()[1]
    checked = 0
    for lang in ("en", "he"):
        for s in decks[lang].slides:
            names = [sh.name for sh in s.shapes]
            if "lay-tip-icon" not in names:
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
# Titles must fit one line (>= 28pt): as long as the longest real title.
LONG_TITLE = {"en": "Heltec board + DHT22: implicit vs explicit",
              "he": "לוח Heltec עם DHT22: מרומז מול מפורש בדיוק"}


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
        title=dict(LONG_TITLE), bullets=[Bullet(f"b{i}", LONG, LONG_HE) for i in range(5)],
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
              ]
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


# --- task 6: fit guard on every text body (no reliance on normAutofit) ------

from presentation.build.layouts import BODY_PT, CODE_PT, SMALL_PT, TIP_PT, TITLE_PT  # noqa: E402

MID = "Medium length bullet text that wraps once or twice in a box"  # 59 chars
HUGE = " ".join(["overflowing"] * 400)


def _runs_pt(sl, name):
    sh = _shape(sl, name)
    return {r.font.size.pt for p in sh.text_frame.paragraphs for r in p.runs}


def _fits(sh, size):
    from presentation.build.layouts import (BULLET_INDENT, FRAME_INSET_H,
                                            FRAME_INSET_V, est_height, est_lines)
    tw = sh.width - FRAME_INSET_H - BULLET_INDENT
    lines = sum(est_lines(p.text, tw, size) for p in sh.text_frame.paragraphs)
    return est_height(lines, size) + FRAME_INSET_V <= sh.height


@pytest.mark.parametrize("lang", ["en", "he"])
def test_long_bullets_fit_by_downsizing(lang):
    s = _long_slide("bullets")
    s.bullets = [Bullet(f"b{i}", MID + " " + MID, MID + " " + MID) for i in range(7)]
    sl = _render(s, lang)
    (size,) = _runs_pt(sl, "lay-body")
    assert 14 <= size < BODY_PT
    assert _fits(_shape(sl, "lay-body"), size)


def test_short_bullets_keep_default_size():
    s = _long_slide("bullets")
    s.bullets = [Bullet("a", "short", "קצר")]
    assert _runs_pt(_render(s), "lay-body") == {BODY_PT}


def _overflow(layout, mutate):
    s = _long_slide(layout)
    mutate(s)
    return s


TOO_LONG = {
    "bullets": ("bullets", lambda s: setattr(s, "bullets", [Bullet("x", HUGE, HUGE)])),
    "code-bullets": ("code", lambda s: setattr(s, "bullets", [Bullet("x", HUGE, HUGE)])),
    "code": ("code", lambda s: s.extra.__setitem__("code", "\n".join(["x = 1"] * 60))),
    "compare": ("compare", lambda s: s.extra.__setitem__(
        "columns", [{"heading": {"en": "h", "he": "h"},
                     "items": [{"en": HUGE, "he": HUGE}]}] * 2)),
    "caption": ("photos", lambda s: s.extra["images"][1].__setitem__(
        "caption", {"en": HUGE, "he": HUGE})),
    "tip": ("bullets", lambda s: setattr(s, "tip", Tip("t", HUGE, HUGE))),
}


@pytest.mark.parametrize("case", sorted(TOO_LONG))
def test_too_long_body_raises(case):
    layout, mutate = TOO_LONG[case]
    with pytest.raises(ValueError, match=f"long-{layout}"):
        _render(_overflow(layout, mutate))


def test_long_tip_fits_by_downsizing():
    s = _long_slide("bullets")
    s.tip = Tip("t", " ".join(["word"] * 40), " ".join(["מילה"] * 40))
    (size,) = _runs_pt(_render(s), "lay-tip-text")
    assert 14 <= size < TIP_PT


def test_long_code_fits_by_downsizing():
    s = _long_slide("code")
    s.extra["code"] = "\n".join(["line"] * 14)
    (size,) = _runs_pt(_render(s), "lay-code")
    assert 14 <= size < CODE_PT


def test_compare_items_fit_by_downsizing():
    s = _long_slide("compare")
    pair = {"en": MID + " " + MID, "he": MID + " " + MID}
    s.extra["columns"] = [{"heading": {"en": "h", "he": "h"}, "items": [pair] * 4}] * 2
    (size,) = _runs_pt(_render(s), "lay-col0-body")
    assert 14 <= size < SMALL_PT


def test_bullet_strip_leaves_min_diagram_height():
    s = _long_slide("bullets-diagram")
    four = MID + " " + MID + " " + MID + " " + MID
    s.bullets = [Bullet(f"b{i}", four, four) for i in range(3)]
    with pytest.raises(ValueError, match="long-bullets-diagram"):
        _render(s)


def test_title_steps_down_to_one_line():
    s = _long_slide("bullets")
    s.title = {"en": "Heltec board + DHT22: implicit vs explicit wiring",
               "he": "Heltec board + DHT22: implicit vs explicit wiring"}
    (size,) = _runs_pt(_render(s), "lay-title")
    assert 28 <= size < TITLE_PT


def test_short_title_keeps_size():
    s = _long_slide("bullets")
    s.title = {"en": "Takeaways", "he": "סיכום"}
    assert _runs_pt(_render(s), "lay-title") == {TITLE_PT}


def test_title_needing_two_lines_raises():
    s = _long_slide("bullets")
    s.title = {"en": LONG + " " + LONG, "he": LONG_HE + " " + LONG_HE}
    with pytest.raises(ValueError, match="long-bullets.*title"):
        _render(s)


def test_code_lines_do_not_wrap_when_avoidable():
    """Mono code wraps badly: step down until no source line wraps (>= 14pt)."""
    from presentation.build.layouts import FRAME_INSET_H, MONO_EM, est_lines
    s = _long_slide("code")
    line = "test_third_consecutive_failure_enters_sensor_error [PASSED]"  # 59
    s.extra["code"] = "$ pio test -e native\n" + line + "\n"
    sl = _render(s)
    (size,) = _runs_pt(sl, "lay-code")
    tw = _shape(sl, "lay-code").width - FRAME_INSET_H
    assert 14 <= size < CODE_PT
    assert est_lines(line, tw, size, char_em=MONO_EM) == 1


def test_short_code_keeps_default_size():
    s = _long_slide("code")
    s.extra["code"] = "cd heltec-monitor\n"
    assert _runs_pt(_render(s), "lay-code") == {CODE_PT}


def test_list_mixed_lines():
    from presentation.build.build_decks import list_mixed_lines
    from presentation.build.model import Deck
    s = Slide(id="s1", part="intro", budget_s=60, layout="bullets",
              title={"en": "T", "he": "כותרת"},
              bullets=[Bullet("a", "x", "עם Spec Kit"), Bullet("b", "y", "רק עברית")],
              tip=Tip("t", "tip", "טיפ עם AI"), notes={"he": "הערה עם AI"},
              diagram={"name": "d", "labels": {"k": {"en": "L", "he": "תווית PR #4"}}},
              sources=[], appendix=False,
              extra={"table": {"rows": [[{"en": "a", "he": "spec.md"}]]}})
    deck = Deck(meta={}, glossary_keep_en=[], glossary_forbidden_he=[], slides=[s])
    assert list_mixed_lines(deck) == [("s1", "עם Spec Kit"), ("s1", "טיפ עם AI"),
                                      ("s1", "תווית PR #4")]
    real = list_mixed_lines(load_deck(str(DECK)))
    assert ("superpowers", "כמו checklist של טייס: skills שה-agent חייב לעבוד לפיהם") in real


def test_manual_check_md_lists_mixed_lines_and_tips_once():
    from presentation.build.build_decks import list_mixed_lines, manual_check_md
    deck = load_deck(str(DECK))
    md = manual_check_md(deck)
    tips = {s.tip.he for s in deck.slides if s.tip}
    for sid, line in list_mixed_lines(deck):
        assert f"- [ ] {line}" in md or line in tips
    for s in deck.slides:
        if s.tip:
            assert md.count(f"- [ ] TIP: {s.tip.he}") == 1
            assert f"- [ ] {s.tip.he}\n" not in md


def test_est_lines_keeps_nbsp_words_together():
    from presentation.build.layouts import est_lines
    w = int(7.5 * 20 * 12700 * 0.55)  # 7 chars per line at 20 pt
    # "27<NBSP>°C" is one 5-char word: it moves to line 2 whole, and "bbb"
    # then no longer fits beside it (a split on NBSP would give 2 lines).
    assert est_lines("aa 27\u00a0°C bbb", w, 20) == 3
    assert est_lines("aa 27 °C bbb", w, 20) == 2


def test_icon_size_defined_once_in_theme():
    from presentation.build import layouts, theme
    assert layouts.ICON == theme.ICON


def test_heading_font_is_family_and_bold(decks):
    from presentation.build.theme import FONTS
    assert FONTS["en"]["head"] == "Arial"
    t = next(sh for sh in decks["en"].slides[1].shapes if sh.name == "lay-title")
    runs = [r for p in t.text_frame.paragraphs for r in p.runs]
    assert runs and all(r.font.bold and r.font.name == "Arial" for r in runs)


def test_manual_check_md_is_current():
    from presentation.build.build_decks import CHECK_MD, manual_check_md
    assert manual_check_md(load_deck(DECK)) == CHECK_MD.read_text(encoding="utf-8")


def test_adlc_title_label_fits_and_is_expanded():
    d = next(s for s in load_deck(DECK).slides if s.id == "intent-gap").diagram
    lab = d["labels"]["adlc_title"]
    assert lab["en"] == "ADLC: agentic dev life cycle"
    assert lab["he"] == "ADLC: מחזור פיתוח עם agents"
    assert len(lab["en"]) <= 30 and len(lab["he"]) <= 30


@pytest.mark.parametrize("lang", ["en", "he"])
def test_transcript_is_current_and_complete(lang):
    from presentation.build.build_decks import TRANSCRIPT, transcript_md
    deck = load_deck(DECK)
    md = transcript_md(deck, lang)
    assert md == TRANSCRIPT[lang].read_text(encoding="utf-8")
    for n, s in enumerate(deck.slides, 1):
        assert f"### {n}. {s.title[lang]}" in md
        first = next(ln for ln in s.notes[lang].splitlines() if ln.strip())
        assert first.strip() in md
    assert md.count("💡") == sum(1 for s in deck.slides if s.tip)
    assert ("<div dir=\"rtl\">" in md) == (lang == "he")


def test_opening_slide_is_keynote_style(decks):
    from presentation.build.theme import ASSETS
    assert (ASSETS / "bg.png").exists() and (ASSETS / "bg-title.png").exists()
    for lang, accent in (("en", "with AI"), ("he", "עם AI")):
        sl = decks[lang].slides[0]
        names = {sh.name: sh for sh in sl.shapes}
        assert {"lay-eyebrow", "lay-title", "lay-title-accent", "lay-body"} <= set(names)
        # the source is cited on the References slide, not on the cover
        assert "Dwarampudi" not in " ".join(sh.text_frame.text for sh in sl.shapes
                                             if sh.has_text_frame)
        assert names["lay-title-accent"].text_frame.text.replace("‎", "").replace(
            "‏", "").strip() == accent
        runs = [r for p in names["lay-title-accent"].text_frame.paragraphs for r in p.runs]
        assert runs and all(r._r.rPr.find(
            "{http://schemas.openxmlformats.org/drawingml/2006/main}gradFill") is not None
            for r in runs)
        assert min(r.font.size.pt for r in runs) >= 40
