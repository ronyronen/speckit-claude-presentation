"""RTL-aware text writer. English terms stay English (own run, lang en-US)."""
import re

from lxml import etree
from pptx.oxml.ns import qn
from pptx.util import Pt

from .theme import COLORS, FONTS

_HE = re.compile(r"[֐-׿]")
_LATIN = re.compile(r"[A-Za-z0-9]")
_NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"


def split_runs(text, glossary):
    """Split text into (segment, "en"|"he") pairs; ''.join(segments) == text.

    Latin letters/digits and glossary terms are "en", Hebrew is "he".
    Neutral chars (space, punctuation) join the Hebrew neighbour, except
    between two English chars where they stay English (e.g. "Spec Kit").
    """
    labels = [None] * len(text)
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
        i = j
    out = []
    for ch, lab in zip(text, labels):
        if out and out[-1][1] == lab:
            out[-1] = (out[-1][0] + ch, lab)
        else:
            out.append((ch, lab))
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
        for seg, seg_lang in split_runs(line, glossary):
            r = p.add_run()
            r.text = seg
            r.font.size = Pt(size_pt)
            r.font.bold = bold
            r.font.color.rgb = color
            r.font.name = font  # <a:latin>
            rPr = r._r.get_or_add_rPr()
            rPr.set("lang", "he-IL" if (lang == "he" and seg_lang == "he") else "en-US")
            if lang == "he":
                etree.SubElement(rPr, qn("a:cs")).set("typeface", font)
