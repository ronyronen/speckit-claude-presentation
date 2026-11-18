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


LRM = "‎"


def test_split_runs_slash_glued_to_latin_is_english():
    segs = split_runs("מה /speckit-analyze תפס", [])
    assert ("/speckit-analyze", "en") in segs
    segs = split_runs("תיקיית specs/ נוסעת", [])
    assert ("specs/", "en") in segs
    assert all(l == "he" for s, l in split_runs("קלט/פלט", []))


def test_he_lrm_isolates_latin_edges():
    """Leading slash/digit and trailing slash of an English run stay LTR in HE."""
    tf = _tf()
    write_paragraphs(tf, ["מה /speckit-analyze תפס", "תיקיית specs/ נוסעת",
                          "מ-01-start ועד 08-implemented"], "he", 20, [])
    runs = [r.text for p in tf.paragraphs for r in p.runs]
    assert LRM + "/speckit-analyze" in runs
    assert "specs/" + LRM in runs
    assert LRM + "01-start" in runs and LRM + "08-implemented" in runs


def test_lrm_only_where_needed():
    tf = _tf()
    write_paragraphs(tf, ["שלום Spec Kit עולם", "TIP"], "he", 20, ["Spec Kit"])
    write_paragraphs(_tf(), ["/x 1"], "en", 20, [])
    assert LRM not in "".join(r.text for p in tf.paragraphs for r in p.runs)
    en = _tf()
    write_paragraphs(en, ["/speckit-analyze"], "en", 20, [])
    assert LRM not in en.text


RLM = "‏"


def _he_runs(line, glossary=()):
    tf = _tf()
    write_paragraphs(tf, [line], "he", 20, list(glossary))
    return [r.text for r in tf.paragraphs[0].runs]


def test_trailing_punctuation_after_english_is_hebrew():
    """'... prompt.' must end with the period on the far left in RTL."""
    segs = split_runs("לפני שאתם כותבים prompt.", [])
    assert segs[-2:] == [("prompt", "en"), (".", "he")]
    assert split_runs("אחרי קריאה 1, או 3?", [])[-1] == ("?", "he")
    assert "prompt" + LRM not in "".join(_he_runs("כותבים prompt."))


def test_sentence_punctuation_between_english_words_is_hebrew():
    """'ה-agent: skills': the colon belongs to the Hebrew sentence, so the
    prefix stays glued to 'agent' and an RLM breaks the LTR run."""
    segs = split_runs("בשביל ה-agent: skills שהוא", [])
    assert ("agent", "en") in segs and (": ", "he") in segs and ("skills", "en") in segs
    assert RLM + ": " in _he_runs("בשביל ה-agent: skills שהוא")
    assert (", ", "he") in split_runs("עם Claude Code, Codex ואחרים", [])
    assert (" (", "he") in split_runs("PR (pull request) = בקשה", [])


def test_quotes_stay_glued_to_english():
    line = "של V. Dwarampudi, “Spec-Driven AI” (Medium, יוני 2026)"
    segs = split_runs(line, [])
    assert "".join(s for s, _ in segs) == line
    assert ("“Spec-Driven AI”", "en") in segs
    assert LRM + "“Spec-Driven AI”" + LRM in _he_runs(line)


def test_all_english_line_unchanged():
    for t in ["plan.md, tasks.md", "GitHub: github/spec-kit · bmad-code-org/BMAD-METHOD",
              "feature branch (DHT22)", "PR #4"]:
        assert split_runs(t, []) == [(t, "en")]
    assert RLM not in "".join(_he_runs("plan.md, tasks.md"))
