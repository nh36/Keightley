"""Regression checks for the ch01/ch05 inline footnote-block repairs."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CH01 = REPO_ROOT / "tex" / "chapters" / "ch01.tex"
CH05 = REPO_ROOT / "tex" / "chapters" / "ch05.tex"

CH01_SUSPICIOUS_STRINGS = [
    "103. \\pinyinterm{chen-mengjia}",
    "104. \\pinyinterm{xu-jinxiong}",
    "106. Since the order in which the inscriptions",
    "110. E.g., \\pinyinterm{pinbian} 304.22-24.",
    "117. \\pinyinterm{dong-short} (1948a), p. 122, estimated that on",
    "Density of Use\nThe pattern of burning on some plastrons",
]

CH05_SUSPICIOUS_STRINGS = [
    "Historical Sources\\footnote[1]",
    "Before examining how the oracle-bone inscriptions function as sources",
]


def test_no_inline_note_block_residue_in_ch01():
    text = CH01.read_text(encoding="utf-8")
    offenders = [needle for needle in CH01_SUSPICIOUS_STRINGS if needle in text]

    assert not offenders, "Found ch01 inline-note residue:\n" + "\n".join(offenders)


def test_ch05_opening_notes_are_not_attached_to_chapter_title():
    text = CH05.read_text(encoding="utf-8")
    offenders = [needle for needle in CH05_SUSPICIOUS_STRINGS if needle in text]

    assert not offenders, "Found ch05 opening-page residue:\n" + "\n".join(offenders)


def test_ch05_opening_paragraph_carries_the_rehomed_notes():
    text = CH05.read_text(encoding="utf-8")

    assert "stone.\\footnote[1]{" in text
    assert "historical period,\\footnote[2]{" in text
    assert "shang} calendar\\footnote[3]{" in text
    assert "organization;\\footnote[4]{" in text
    assert "authenticity, and dating.\\footnote[5]{" in text
