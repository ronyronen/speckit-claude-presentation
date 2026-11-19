"""The transcript as a reader's edition: the talk written up like a paper.

One section per part, one subsection per slide (numbered as in the deck, so
a reader can follow along), the speaker notes as prose, and numbered citations
with a References list at the end. Presenter-only material is left out:
timings, "backup, not timed", "Cue:" paragraphs and divider transitions.
"""
from __future__ import annotations

import re

_URL = re.compile(r"https?://[^\s)\"'”]+")
# "Source: url", "Sources:", "Source (diagram adapted from): url", or a short
# "Label: url" line as on the References slide.
_SOURCE_LINE = re.compile(r"^(?:Sources?(?: \(([^)]*)\))?:(?:\s*https?://.*)?"
                          r"|[A-Za-z][\w ]{0,24}:\s*https?://\S+)$")

# Paper-style entries for every URL the notes cite. A URL missing here is
# listed by itself, so a new source never breaks the build.
CITATIONS = {
    "https://vimal-dwarampudi.medium.com/spec-driven-ai-bmad-speckit-gsd-superpowers-2cae4512819a":
        "Dwarampudi, V. (2026). *Spec-Driven AI: BMAD, SpecKit, GSD & Superpowers*. Medium.",
    "https://arxiv.org/abs/2307.03172":
        "Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., "
        "& Liang, P. (2024). Lost in the Middle: How Language Models Use Long Contexts. "
        "*Transactions of the Association for Computational Linguistics*, 12.",
    "https://www.trychroma.com/research/context-rot":
        "Hong, K., Troynikov, A., & Huber, J. (2025). *Context Rot: How Increasing "
        "Input Tokens Impacts LLM Performance*. Chroma Research.",
    "https://github.com/github/spec-kit":
        "GitHub. (2025). *Spec Kit* [Computer software].",
    "https://github.github.io/spec-kit/":
        "GitHub. (2025). *Spec Kit documentation*.",
    "https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/":
        "GitHub. (2025). Spec-driven development with AI: Get started with a new "
        "open source toolkit. *The GitHub Blog*.",
    "https://github.com/obra/superpowers":
        "obra. (2025). *Superpowers* [Computer software].",
    "https://github.com/bmad-code-org/BMAD-METHOD":
        "BMad Code. (2025). *BMAD-METHOD* [Computer software].",
    "https://docs.bmad-method.org/":
        "BMad Code. (2025). *BMAD Method documentation*.",
    "https://github.com/open-gsd/gsd-core":
        "open-gsd. (2026). *GSD core* [Computer software].",
    "https://github.com/gsd-build/get-shit-done":
        "TÂCHES. (2025). *get-shit-done* [Computer software, archived].",
    "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents":
        "Anthropic. (2025). *Effective context engineering for AI agents*. Anthropic Engineering.",
    "https://www.anthropic.com/engineering/claude-code-best-practices":
        "Anthropic. (2025). *Claude Code: Best practices for agentic coding*. Anthropic Engineering.",
    "https://code.claude.com/docs/en/plugins":
        "Anthropic. (2026). *Claude Code documentation: Plugins*.",
    "https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html":
        "Böckeler, B. (2025). *Understanding Spec-Driven Development: Kiro, spec-kit, "
        "and Tessl*. martinfowler.com.",
    "https://github.com/ronyronen/speckit-claude-presentation":
        "*Spec-Driven Development with AI: talk materials* [Repository]. (2026). GitHub.",
    "https://github.com/ronyronen/speckit-claude-presentation/blob/main/docs/textbook.md":
        "*Spec-Driven Development with AI: textbook* (docs/textbook.md). (2026). GitHub.",
    "https://github.com/ronyronen/speckit-claude-presentation/tree/main/specs/001-heltec-monitor":
        "*Heltec monitor case study: specs/001-heltec-monitor*. (2026). GitHub.",
}

_T = {
    "en": {
        "intro": "A reader's edition of the talk, written to be read alongside the "
                 "slides. Each section below matches one slide and carries its number, "
                 "so you can follow along. Numbers in square brackets point to the "
                 "References at the end.",
        "deck": "Slides", "deck_name": "English deck",
        "part": "Part", "appendix": "Appendix", "slide": "Slide",
        "intro_h": "Introduction", "close_h": "Closing",
        "key": "Key point", "analogy": "Analogy", "sources": "Sources",
        "adapted": "Diagram adapted from", "refs": "References",
    },
    "he": {
        "intro": "גרסת קריאה של ההרצאה, שנכתבה כדי לקרוא אותה לצד השקפים. כל סעיף "
                 "מתאים לשקף אחד ונושא את המספר שלו, כך שקל לעקוב. מספרים בסוגריים "
                 "מרובעים מפנים לרשימת המקורות בסוף.",
        "deck": "שקפים", "deck_name": "המצגת בעברית",
        "part": "חלק", "appendix": "נספח", "slide": "שקף",
        "intro_h": "מבוא", "close_h": "סיכום",
        "key": "הנקודה המרכזית", "analogy": "אנלוגיה", "sources": "מקורות",
        "adapted": "התרשים מעובד מתוך", "refs": "רשימת מקורות",
    },
}

_BACKUP = re.compile(r"^backup, not timed\.?\s*")
_DROP = re.compile(r"^(Cue|Transition|מעבר):")


def _paragraphs(s, lang) -> list[str]:
    paras = [p.strip() for p in s.notes.get(lang, "").split("\n") if p.strip()]
    out = []
    for p in paras:
        p = _BACKUP.sub("", p)
        if p and not _DROP.match(p):
            out.append(p)
    return out


class _Refs:
    def __init__(self):
        self.order: list[str] = []

    def cite(self, url: str) -> str:
        url = url.rstrip(".,;")
        if url not in self.order:
            self.order.append(url)
        return f"[{self.order.index(url) + 1}]"

    def render(self) -> list[str]:
        return [f"{i}. {CITATIONS[u]} <{u}>" if u in CITATIONS else f"{i}. <{u}>"
                for i, u in enumerate(self.order, 1)]


def _section(s, lang, t, refs) -> list[str]:
    """Body of one slide: key point, analogy, prose, then its citations."""
    out = []
    if s.tip:
        out += [f"> **{t['key']}:** {getattr(s.tip, lang)}", ""]
    pending: list[str] = []
    adapted = False

    def flush():
        nonlocal pending, adapted
        if pending:
            label = t["adapted"] if adapted else t["sources"]
            out.extend([f"*{label}:* {', '.join(pending)}", ""])
        pending, adapted = [], False

    for p in _paragraphs(s, lang):
        m = _SOURCE_LINE.match(p)
        if m:
            pending += [refs.cite(u) for u in _URL.findall(p)]
            adapted = adapted or "adapted" in (m.group(1) or "")
            continue
        if _URL.fullmatch(p):
            pending.append(refs.cite(p))
            continue
        flush()
        if p.startswith("Analogy:"):
            out += [f"*{t['analogy']}:* {p[len('Analogy:'):].strip()}", ""]
        else:
            out += [_URL.sub(lambda u: refs.cite(u.group(0)), p), ""]
    flush()
    return out


def reader_md(deck, lang: str, deck_file: str) -> str:
    t = _T[lang]
    refs = _Refs()
    slides = deck.slides
    cover = slides[0]
    subtitle = next((getattr(b, lang) for b in cover.bullets if b.key == "subtitle"), "")
    out = [f"# {cover.title.get(lang, '')}", ""]
    if subtitle:
        out += [f"*{subtitle}*", ""]
    out += [t["intro"], "", f"{t['deck']}: [{t['deck_name']}]({deck_file})", ""]
    out += [p for p in _paragraphs(cover, lang) for p in (p, "")]
    part_no, current = 0, cover.part
    for n, s in enumerate(slides[1:], 2):
        if s.layout == "divider":
            if s.appendix:
                head = f"{t['appendix']}: {s.title.get(lang, '')}"
            else:
                part_no += 1
                head = f"{t['part']} {part_no}: {s.title.get(lang, '')}"
            out += ["---", "", f"## {head}", ""]
            lead = next((getattr(b, lang) for b in s.bullets if b.key == "subtitle"), "")
            if lead:
                out += [f"*{lead}*", ""]
            current = s.part
            continue
        if s.part != current:
            current = s.part
            if s.part in ("0", "close"):
                out += ["---", "", f"## {t['intro_h' if s.part == '0' else 'close_h']}", ""]
        if n == 2 and s.part == "0":
            out += [f"## {t['intro_h']}", ""]
        out += [f"### {t['slide']} {n} · {s.title.get(lang, '')}", ""]
        body = _section(s, lang, t, refs)
        if not any(ln and not ln.startswith(">") for ln in body):
            # nothing to read but the slide itself: give its points as a list
            body += [f"- {getattr(b, lang)}" for b in s.bullets] + [""]
        out += body
    out += ["---", "", f"## {t['refs']}", ""] + refs.render()
    body = "\n".join(out).rstrip() + "\n"
    if lang == "he":
        body = '<div dir="rtl">\n\n' + body + '\n</div>\n'
    return body
