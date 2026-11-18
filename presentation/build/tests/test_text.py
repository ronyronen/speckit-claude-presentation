from lxml import etree
from pptx import Presentation
from pptx.util import Inches

from presentation.build.text import set_rtl, split_runs, write_paragraphs


def _tf():
    prs = Presentation()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    return s.shapes.add_textbox(0, 0, Inches(5), Inches(3)).text_frame


def _xml(tf):
    return etree.tostring(tf._txBody, encoding="unicode")


def test_split_runs_mixed():
    text = "השתמשו ב-Spec Kit עם Claude"
    segs = split_runs(text, ["Spec Kit"])
    assert "".join(s for s, _ in segs) == text
    assert ("Spec Kit", "en") in [(s.strip(), l) for s, l in segs] or \
        any(s == "Spec Kit" and l == "en" for s, l in segs)
    assert any(s == "Claude" and l == "en" for s, l in segs)
    assert all(l == "he" for s, l in segs if "השתמשו" in s or "עם" in s)


def test_split_runs_roundtrip_edge():
    for t in ["", "abc", "שלום", "שלום, world!", "a  שלום  b"]:
        assert "".join(s for s, _ in split_runs(t, [])) == t


def test_he_paragraph_rtl():
    tf = _tf()
    write_paragraphs(tf, ["שלום"], "he", 20, [])
    x = _xml(tf)
    assert 'rtl="1"' in x and 'algn="r"' in x
    assert 'lang="he-IL"' in x
    assert '<a:cs typeface="Arial"' in x
    assert '<a:latin typeface="Arial"' in x


def test_he_runs_tag_english_terms():
    tf = _tf()
    write_paragraphs(tf, ["שלום Spec Kit עולם"], "he", 20, ["Spec Kit"])
    runs = tf.paragraphs[0].runs
    en = [r for r in runs if r.text == "Spec Kit"]
    assert en and 'lang="en-US"' in etree.tostring(en[0]._r, encoding="unicode")
    assert any('lang="he-IL"' in etree.tostring(r._r, encoding="unicode") for r in runs)


def test_no_newline_in_run():
    tf = _tf()
    write_paragraphs(tf, ["one\ntwo"], "en", 18, [])
    assert len(tf.paragraphs) == 2
    assert all("\n" not in r.text for p in tf.paragraphs for r in p.runs)


def test_en_paragraph_ltr():
    tf = _tf()
    write_paragraphs(tf, ["Hello"], "en", 18, [])
    x = _xml(tf)
    assert 'rtl="1"' not in x
    assert "Plus Jakarta Sans" in x


def test_bullets_not_numbered():
    for lang, t in (("en", "Hello"), ("he", "שלום")):
        tf = _tf()
        write_paragraphs(tf, [t], lang, 18, [])
        x = _xml(tf)
        assert "buChar" in x and "buAutoNum" not in x


def test_no_bullet_option():
    tf = _tf()
    write_paragraphs(tf, ["Hello"], "en", 18, [], bullet=False)
    assert "buNone" in _xml(tf)


def test_set_rtl():
    tf = _tf()
    p = tf.paragraphs[0]
    set_rtl(p)
    assert p._p.pPr.get("rtl") == "1" and p._p.pPr.get("algn") == "r"
