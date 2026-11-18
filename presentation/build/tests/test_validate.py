import copy
from pathlib import Path

import pytest
import yaml

from presentation.build.model import (Deck, _slide, fmt_mmss, load_deck,
                                      parse_budget, timing_prefixes)
from presentation.build.validate import validate

FIX = Path(__file__).parent / "fixtures" / "valid_min.yaml"


@pytest.fixture
def raw():
    return yaml.safe_load(FIX.read_text(encoding="utf-8"))


def build(raw) -> Deck:
    return Deck(raw["meta"], raw.get("glossary_keep_en", []),
                raw.get("glossary_forbidden_he", []),
                [_slide(s) for s in raw["slides"]])


def errs(raw, diagrams=frozenset()):
    return validate(build(raw), set(diagrams))


def has(es, text):
    return any(text in e for e in es)


def content(raw):
    return raw["slides"][1]


def test_valid_fixture_passes(raw):
    assert errs(raw) == []


def test_slide_missing_he_title(raw):
    del content(raw)["title"]["he"]
    assert has(errs(raw), "title.he")


def test_bullet_key_mismatch(raw):
    content(raw)["bullets"][0]["he"] = ""
    assert has(errs(raw), "bullet key mismatch")


def test_more_than_five_bullets(raw):
    content(raw)["bullets"] = [{"key": f"k{i}", "en": "a", "he": "b"} for i in range(6)]
    assert has(errs(raw), "max 5")


def test_tip_key_mismatch(raw):
    content(raw)["tip"]["he"] = ""
    assert has(errs(raw), "tip key mismatch")


def test_budget_sum_not_total(raw):
    del raw["meta"]["total_budget"]
    assert has(errs(raw), "45:00")


def test_qa_not_3min(raw):
    del raw["meta"]["qa_budget"]
    assert has(errs(raw), "3:00")


def test_prefixes_cumulative_end(raw):
    for s, b in zip(raw["slides"], ["0:30", "1:00", "1:30"]):
        s["budget"] = b
    p = timing_prefixes(build(raw))
    assert [p[s["id"]] for s in raw["slides"]] == [
        "[0:30] [@0:30]", "[1:00] [@1:30]", "[1:30] [@3:00]"]


def test_appendix_prefix_and_excluded_from_timing(raw):
    raw["slides"].append(_appendix())
    d = build(raw)
    assert timing_prefixes(d)["a1"] == "[backup, not timed]"
    assert validate(d, set()) == []


def test_missing_analogy(raw):
    content(raw)["notes"]["en"] = "No such line."
    assert has(errs(raw), "Analogy")


def test_part_iv_analogy_reference_ok(raw):
    content(raw)["part"] = "IV"
    content(raw)["notes"] = {"en": "Analogy: see slide 3", "he": "Analogy: see slide 3"}
    assert errs(raw) == []
    content(raw)["part"] = "I"
    assert has(errs(raw), "only allowed in part IV")


def test_tip_count_below_10(raw):
    del raw["meta"]["min_tips"]
    assert has(errs(raw), "need at least 10")


def test_tip_over_20_words(raw):
    content(raw)["tip"]["en"] = " ".join(["w"] * 21)
    assert has(errs(raw), "tip.en has 21 words")


def test_tip_on_title_forbidden(raw):
    raw["slides"][0]["tip"] = {"key": "t", "en": "x", "he": "y"}
    assert has(errs(raw), "tip not allowed")


@pytest.mark.parametrize("text", ["/speckit-plan", "run $ specify"])
def test_cli_in_theory(raw, text):
    content(raw)["bullets"][0]["en"] = f"Use {text}"
    assert has(errs(raw), "CLI syntax")
    content(raw)["part"] = "IV"
    assert errs(raw) == []


@pytest.mark.parametrize("text", ["300k+ stars", "55,497 stars"])
def test_star_count_in_text(raw, text):
    content(raw)["bullets"][0]["en"] = f"Has {text}"
    assert has(errs(raw), "star count")


@pytest.mark.parametrize("text", ["21+", "Lex Christopherson"])
def test_banned_claims(raw, text):
    content(raw)["bullets"][0]["en"] = f"About {text}"
    assert has(errs(raw), "banned claim")


def test_star_count_allowed_in_notes_only(raw):
    content(raw)["notes"]["en"] += "\n300k+ stars (Nov 2026)"
    assert errs(raw) == []
    content(raw)["bullets"][0]["en"] = "300K+ stars (Nov 2026)"
    assert has(errs(raw), "star count")


def test_banned_claim_ignored_in_notes_and_later_parts(raw):
    content(raw)["notes"]["en"] += "\nLex Christopherson 21+"
    assert errs(raw) == []
    content(raw)["bullets"][0]["en"] = "21+"
    content(raw)["part"] = "V"
    assert errs(raw) == []


def _appendix(**kw):
    d = {"id": "a1", "part": "close", "budget": "0:00", "appendix": True,
         "title": {"en": "A", "he": "א"},
         "notes": {"en": "backup, not timed", "he": "backup, not timed"}}
    d.update(kw)
    return d


def test_appendix_notes_must_start_with_backup(raw):
    raw["slides"].append(_appendix(notes={"en": "x", "he": "backup, not timed"}))
    assert has(errs(raw), "appendix notes.en")


def test_appendix_tip_rules_apply(raw):
    raw["slides"].append(_appendix(tip={"key": "k", "en": " ".join(["w"] * 21), "he": ""}))
    e = errs(raw)
    assert has(e, "tip.en has 21 words") and has(e, "tip key mismatch")
    raw["meta"]["min_tips"] = 2  # appendix tip must not count
    assert has(errs(raw), "only 1 tips")


def test_hebrew_term_token_boundaries(raw):
    content(raw)["tip"]["he"] = "טיפול טיפוס"
    assert errs(raw) == []
    content(raw)["tip"]["he"] = "הטיפ שלנו"
    assert has(errs(raw), "forbidden Hebrew term")


def test_sources_need_url(raw):
    content(raw)["sources"] = ["F6"]
    assert has(errs(raw), "no URL")
    content(raw)["notes"]["en"] += "\nhttps://example.com"
    content(raw)["notes"]["he"] += "\nhttps://example.com"
    assert errs(raw) == []


def test_unknown_diagram(raw):
    content(raw)["diagram"] = {"name": "nope"}
    assert has(errs(raw, {"other"}), "unknown diagram")
    assert errs(raw, {"nope"}) == []


def test_forbidden_hebrew_term(raw):
    content(raw)["tip"]["he"] = "טיפ קטן"
    assert has(errs(raw), "forbidden Hebrew term")


def test_loader_roundtrips_unicode():
    d = load_deck(FIX)
    assert d.slides[1].title["he"] == "פער הכוונה"
    assert d.slides[1].budget_s == 90
    assert "טיפ" in d.glossary_forbidden_he


@pytest.mark.parametrize("bad", ["2:5", "150", "2.5", ""])
def test_parse_budget_rejects_malformed(bad):
    with pytest.raises(ValueError, match="bad budget"):
        parse_budget(bad, "s1")


def test_fmt_mmss():
    assert fmt_mmss(90) == "1:30"
