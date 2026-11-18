"""YAML content model for the theory deck."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_BUDGET_RE = re.compile(r"^\d+:[0-5]\d$")


@dataclass
class Bullet:
    key: str
    en: str
    he: str


@dataclass
class Tip:
    key: str
    en: str
    he: str


@dataclass
class Slide:
    id: str
    part: str
    budget_s: int
    layout: str
    title: dict[str, str]
    bullets: list[Bullet]
    tip: Tip | None
    notes: dict[str, str]
    diagram: dict | None
    sources: list[str]
    appendix: bool
    extra: dict = field(default_factory=dict)


@dataclass
class Deck:
    meta: dict
    glossary_keep_en: list[str]
    glossary_forbidden_he: list[str]
    slides: list[Slide]


def parse_budget(s, slide_id: str) -> int:
    """Parse "m:ss" into seconds. A bare integer 0 is accepted (appendix)."""
    if isinstance(s, int) and not isinstance(s, bool) and s == 0:
        return 0
    if not isinstance(s, str) or not _BUDGET_RE.match(s):
        raise ValueError(f"{slide_id}: bad budget {s!r}")
    m, sec = s.split(":")
    return int(m) * 60 + int(sec)


def fmt_mmss(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"


_KNOWN = {"id", "part", "budget", "layout", "title", "bullets", "tip",
          "notes", "diagram", "sources", "appendix"}


def _slide(raw: dict) -> Slide:
    sid = str(raw.get("id", ""))
    tip = raw.get("tip")
    return Slide(
        id=sid,
        part=str(raw.get("part", "")),
        budget_s=parse_budget(raw.get("budget", 0), sid),
        layout=raw.get("layout", ""),
        title=dict(raw.get("title") or {}),
        bullets=[Bullet(b.get("key", ""), b.get("en", ""), b.get("he", ""))
                 for b in raw.get("bullets") or []],
        tip=Tip(tip.get("key", ""), tip.get("en", ""), tip.get("he", ""))
        if tip else None,
        notes=dict(raw.get("notes") or {}),
        diagram=raw.get("diagram"),
        sources=list(raw.get("sources") or []),
        appendix=bool(raw.get("appendix", False)),
        extra={k: v for k, v in raw.items() if k not in _KNOWN},
    )


def load_deck(path) -> Deck:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return Deck(
        meta=dict(data.get("meta") or {}),
        glossary_keep_en=list(data.get("glossary_keep_en") or []),
        glossary_forbidden_he=list(data.get("glossary_forbidden_he") or []),
        slides=[_slide(s) for s in data.get("slides") or []],
    )


def timing_prefixes(deck: Deck) -> dict[str, str]:
    out: dict[str, str] = {}
    elapsed = 0
    for s in deck.slides:
        if s.appendix:
            out[s.id] = "[backup, not timed]"
            continue
        elapsed += s.budget_s
        out[s.id] = f"[{fmt_mmss(s.budget_s)}] [@{fmt_mmss(elapsed)}]"
    return out
