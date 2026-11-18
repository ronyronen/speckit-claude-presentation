"""Deck validator: checks from the design spec section 4, plus the {en, he}
pair completeness check.

Spec check 4 (timing prefix at the start of every note) is NOT checked here:
the generator writes the prefix itself (model.timing_prefixes) and
test_build.py asserts it. So: 10 validator checks plus the generator-enforced
timing prefix."""
from __future__ import annotations

import re
import sys

from .model import Deck, Slide, load_deck, parse_budget
from .text import HEBREW_CHARS

PARTS = {"0", "I", "II", "III", "IV", "V", "VI", "close"}
THEORY = {"0", "I", "II", "III"}
EXEMPT = {"title", "resources", "qa"}
CLI_RE = re.compile(r"(^|\s)/[a-z]+-[a-z]+|\$ \w")
STAR_RE = re.compile(r"\d[\d,.]*k?\+?\s*stars", re.I)
BANNED = ["21+", "Lex Christopherson"]
ANALOGY_RE = re.compile(r"(?m)^Analogy:\s*\S")
ANALOGY_REF_RE = re.compile(r"(?m)^Analogy:\s*see slide\b")
LANGS = ("en", "he")


def _slide_text(s: Slide) -> list[tuple[str, str]]:
    """(location, text) for title, bullets and tip."""
    out = [(f"title.{l}", s.title.get(l, "")) for l in LANGS]
    for b in s.bullets:
        out += [(f"bullet[{b.key}].{l}", getattr(b, l)) for l in LANGS]
    if s.tip:
        out += [(f"tip.{l}", getattr(s.tip, l)) for l in LANGS]
    return out


def _all_text(s: Slide) -> list[tuple[str, str]]:
    return _slide_text(s) + [(f"notes.{l}", s.notes.get(l, "")) for l in LANGS]


def _he_term_re(term: str) -> re.Pattern:
    """Term not followed by a Hebrew letter; optional one-letter prefix allowed."""
    he = f"[{HEBREW_CHARS}]"
    return re.compile(f"(?<!{he})[הובלמשכ]?" + re.escape(term) + f"(?!{he})")


def _pairs(node, loc):
    """(location, dict) for every {en, he} dict nested in node."""
    if isinstance(node, dict):
        if "en" in node or "he" in node:
            yield loc, node
        for k, v in node.items():
            yield from _pairs(v, f"{loc}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _pairs(v, f"{loc}[{i}]")


def validate(deck: Deck, diagram_names: set[str]) -> list[str]:
    errs: list[str] = []
    meta = deck.meta

    # 1. unique ids, titles in both languages
    seen: set[str] = set()
    for s in deck.slides:
        if s.id in seen:
            errs.append(f"{s.id}: duplicate slide id")
        seen.add(s.id)
        if s.part not in PARTS:
            errs.append(f"{s.id}: unknown part {s.part!r}")
        for l in LANGS:
            if not s.title.get(l, "").strip():
                errs.append(f"{s.id}: missing title.{l}")

    # 2. bullet/tip keys, max 5 bullets
    for s in deck.slides:
        if len(s.bullets) > 5:
            errs.append(f"{s.id}: {len(s.bullets)} bullets (max 5)")
        for b in s.bullets:
            for l in LANGS:
                if not getattr(b, l).strip():
                    errs.append(f"{s.id}: bullet key mismatch, {b.key!r} missing {l}")
        if s.tip:
            for l in LANGS:
                if not getattr(s.tip, l).strip():
                    errs.append(f"{s.id}: tip key mismatch, {s.tip.key!r} missing {l}")

    timed = [s for s in deck.slides if not s.appendix]

    # 3. budgets
    try:
        total = parse_budget(meta.get("total_budget", "45:00"), "meta.total_budget")
        qa = parse_budget(meta.get("qa_budget", "3:00"), "meta.qa_budget")
    except ValueError as e:
        return errs + [str(e)]
    total_label = meta.get("total_budget", "45:00")
    qa_label = meta.get("qa_budget", "3:00")
    got = sum(s.budget_s for s in timed)
    if got != total:
        errs.append(f"timed budgets sum to {got}s, expected {total_label} ({total}s)")
    for s in deck.slides:
        if s.appendix and s.budget_s != 0:
            errs.append(f"{s.id}: appendix slide must have budget 0:00")
        if s.appendix:
            for l in LANGS:
                if not s.notes.get(l, "").startswith("backup, not timed"):
                    errs.append(f"{s.id}: appendix notes.{l} must start with 'backup, not timed'")
        if s.id == "qa" and s.budget_s != qa:
            errs.append(f"qa: budget must be exactly {qa_label}")

    # 5. analogy
    for s in timed:
        if s.id in EXEMPT:
            continue
        for l in LANGS:
            n = s.notes.get(l, "")
            if not ANALOGY_RE.search(n):
                errs.append(f"{s.id}: notes.{l} missing 'Analogy:' line")
            elif s.part != "IV" and ANALOGY_REF_RE.search(n):
                errs.append(f"{s.id}: notes.{l} 'Analogy: see slide' only allowed in part IV")

    # 6. tips (shape checks on all slides; the minimum counts timed slides only)
    tips = 0
    for s in deck.slides:
        if not s.tip:
            continue
        if s.id in EXEMPT:
            errs.append(f"{s.id}: tip not allowed on this slide")
            continue
        if not s.appendix:
            tips += 1
        for l in LANGS:
            w = len(getattr(s.tip, l).split())
            if w > 20:
                errs.append(f"{s.id}: tip.{l} has {w} words (max 20)")
    min_tips = int(meta.get("min_tips", 10))
    if tips < min_tips:
        errs.append(f"only {tips} tips, need at least {min_tips}")

    for s in deck.slides:
        # 7. CLI in theory parts
        if s.part in THEORY:
            for loc, t in _slide_text(s):
                if CLI_RE.search(t):
                    errs.append(f"{s.id}: CLI syntax in {loc}")
        # 8. star counts in slide text (dated counts allowed in notes)
        for loc, t in _slide_text(s):
            if STAR_RE.search(t):
                errs.append(f"{s.id}: star count in {loc}")
            # banned claims: slide text of theory parts only
            if s.part in THEORY:
                for b in BANNED:
                    if b in t:
                        errs.append(f"{s.id}: banned claim {b!r} in {loc}")
        # 9. sources need URL
        if s.sources:
            for l in LANGS:
                if "http" not in s.notes.get(l, ""):
                    errs.append(f"{s.id}: sources {s.sources} but no URL in notes.{l}")
        # 10. diagrams
        if s.diagram:
            name = s.diagram.get("name")
            if name not in diagram_names:
                errs.append(f"{s.id}: unknown diagram {name!r}")
        # 11. forbidden Hebrew renderings
        he = [(loc, t) for loc, t in _all_text(s) if loc.endswith(".he")]
        for loc, t in he:
            for term in deck.glossary_forbidden_he:
                if _he_term_re(term).search(t):
                    errs.append(f"{s.id}: forbidden Hebrew term {term!r} in {loc}")
    # 12. {en, he} pairs in extra and diagram.labels: both values non-empty
    for s in deck.slides:
        parts = [("extra", s.extra)]
        if s.diagram:
            parts.append(("diagram.labels", s.diagram.get("labels") or {}))
        for base, node in parts:
            for loc, d in _pairs(node, base):
                for l in LANGS:
                    v = d.get(l)
                    if not isinstance(v, str) or not v.strip():
                        errs.append(f"{s.id}: empty {l} in {loc}")
    return errs


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python -m presentation.build.validate DECK.yaml", file=sys.stderr)
        return 2
    try:
        from .shapes import DIAGRAMS  # added in a later task
        names = set(DIAGRAMS)
    except ImportError:
        names = set()
    try:
        errs = validate(load_deck(argv[0]), names)
    except ValueError as e:
        print(e)
        return 1
    for e in errs:
        print(e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
