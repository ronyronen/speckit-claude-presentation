"""RTL-aware text writer. English terms stay English (own run, lang en-US)."""
import re

from lxml import etree
from pptx.oxml.ns import qn
from pptx.util import Pt

from .theme import COLORS, FONTS

HEBREW_CHARS = "\u0590-\u05ff"  # the Hebrew block; single shared definition
_HE = re.compile(f"[{HEBREW_CHARS}]")
_LATIN = re.compile(r"[A-Za-z0-9]")
_NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"


_SENTENCE_PUNCT = re.compile(r"[,;:()!?]")
_CLOSE_Q = "”’\"'"
_OPEN_Q = "“‘\"'"


def _hebrew_gap(text, labels, i, j):
    """In a Hebrew line, a neutral gap after English that ends the line or
    holds sentence punctuation ("agent: skills", "prompt.") belongs to the
    Hebrew sentence. Quote marks glued to an English word stay English."""
    while i < j and text[i] in _CLOSE_Q:
        i += 1
    if j < len(text):  # followed by English: an opening quote stays with it
        while j > i and text[j - 1] in _OPEN_Q:
            j -= 1
    labels[i:j] = ["he"] * (j - i)


def split_runs(text, glossary):
    """Split text into (segment, "en"|"he") pairs; ''.join(segments) == text.

    Latin letters/digits and glossary terms are "en", Hebrew is "he".
    Neutral chars (space, punctuation) join the Hebrew neighbour, except
    between two English chars where they stay English (e.g. "Spec Kit").
    In a line with Hebrew, sentence punctuation between English words and
    trailing punctuation after English join the Hebrew flow instead.
    """
    labels = [None] * len(text)
    has_he = bool(_HE.search(text))
    for term in sorted(set(glossary), key=len, reverse=True):
        for m in re.finditer(re.escape(term), text):
            if all(l is None for l in labels[m.start():m.end()]):
                labels[m.start():m.end()] = ["en"] * len(term)
    for i, ch in enumerate(text):
        if labels[i] is None:
            if _HE.match(ch):
                labels[i] = "he"
            elif _LATIN.match(ch):
                labels[i] = "en"
    i = 0
    while i < len(text):
        if labels[i] is not None:
            i += 1
            continue
        j = i
        while j < len(text) and labels[j] is None:
            j += 1
        prev = labels[i - 1] if i > 0 else None
        nxt = labels[j] if j < len(text) else None
        if prev and nxt:
            lab = "en" if prev == nxt == "en" else "he"
        else:
            lab = prev or nxt or "en"
        labels[i:j] = [lab] * (j - i)
        if has_he and prev == "en" and (nxt is None or (
                nxt == "en" and _SENTENCE_PUNCT.search(text[i:j]))):
            _hebrew_gap(text, labels, i, j)
        i = j
    # A slash glued to an English word belongs to it ("/speckit-x", "specs/").
    changed = True
    while changed:
        changed = False
        for i, ch in enumerate(text):
            if ch == "/" and labels[i] != "en" and any(
                    0 <= k < len(text) and labels[k] == "en" and not text[k].isspace()
                    for k in (i - 1, i + 1)):
                labels[i] = "en"
                changed = True
    out = []
    for ch, lab in zip(text, labels):
        if out and out[-1][1] == lab:
            out[-1] = (out[-1][0] + ch, lab)
        else:
            out.append((ch, lab))
    return out


LRM = "\u200e"
RLM = "\u200f"


def _isolate(seg):
    """Wrap an English segment in LRM where its edge is not a letter, so a
    leading slash/digit or trailing slash stays on the LTR side in HE."""
    if seg[:1] and not (seg[0].isalpha() or seg[0].isspace()):
        seg = LRM + seg
    if seg[-1:] and not (seg[-1].isalnum() or seg[-1].isspace()):
        seg = seg + LRM
    return seg


def _he_text(segs):
    """Run texts for an HE paragraph: LRM-isolate English edges, and start a
    letterless Hebrew run between two English runs with RLM so the bidi
    algorithm does not fold its punctuation into the LTR run."""
    out = []
    for k, (seg, lab) in enumerate(segs):
        if lab == "en":
            seg = _isolate(seg)
        elif 0 < k < len(segs) - 1 and not _HE.search(seg):
            seg = RLM + seg
        out.append(seg)
    return out


def set_rtl(paragraph):
    """Mark a paragraph right-to-left and right-aligned."""
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set("rtl", "1")
    pPr.set("algn", "r")


def _bullet(paragraph, bullet):
    pPr = paragraph._p.get_or_add_pPr()
    if bullet:
        pPr.set("marL", "285750")
        pPr.set("indent", "-285750")
        # Bullet dot, never buAutoNum (numbering breaks in RTL).
        etree.SubElement(pPr, f"{{{_NS_A}}}buFont").set("typeface", "Arial")
        etree.SubElement(pPr, f"{{{_NS_A}}}buChar").set("char", "•")
    else:
        etree.SubElement(pPr, f"{{{_NS_A}}}buNone")


def write_paragraphs(tf, items, lang, size_pt, glossary, bullet=True,
                     color=None, bold=False):
    """Replace tf contents with one paragraph per item ('\\n' splits too)."""
    lines = []
    for item in items:
        lines.extend(re.split(r"\r\n|\r|\n", item))
    font = FONTS[lang]["body"]
    color = color if color is not None else COLORS["text"]
    tf.clear()
    tf.word_wrap = True
    for n, line in enumerate(lines):
        p = tf.paragraphs[0] if n == 0 else tf.add_paragraph()
        if lang == "he":
            set_rtl(p)
        _bullet(p, bullet)
        segs = split_runs(line, glossary)
        texts = _he_text(segs) if lang == "he" else [s for s, _ in segs]
        for (_, seg_lang), text in zip(segs, texts):
            r = p.add_run()
            r.text = text
            r.font.size = Pt(size_pt)
            r.font.bold = bold
            r.font.color.rgb = color
            r.font.name = font  # <a:latin>
            rPr = r._r.get_or_add_rPr()
            rPr.set("lang", "he-IL" if (lang == "he" and seg_lang == "he") else "en-US")
            if lang == "he":
                etree.SubElement(rPr, qn("a:cs")).set("typeface", font)
