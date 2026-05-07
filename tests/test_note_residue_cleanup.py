"""Regression checks for recent inline note-residue cleanup."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CH03 = REPO_ROOT / "tex" / "chapters" / "ch03.tex"
CH04 = REPO_ROOT / "tex" / "chapters" / "ch04.tex"
APP04 = REPO_ROOT / "tex" / "appendices" / "app04.tex"
APP05 = REPO_ROOT / "tex" / "appendices" / "app05.tex"


def test_ch03_no_long_note_spills():
    text = CH03.read_text(encoding="utf-8")
    offenders = [
        "dictionary. 14 Following",
        "} 15 it also quotes",
        "(fig.\\footnote[57]",
        "(fig.\\footnote[65]",
        "104105106107108109",
        "inscriptionless cracks identified in sec.\\footnote[119]",
        "87 U U ]",
    ]

    found = [needle for needle in offenders if needle in text]
    assert not found, "Found lingering ch03 note residue:\n" + "\n".join(found)

    assert "dictionary.\\footnote[14]{" in text
    assert "vessels,\\footnote[15]{" in text
    assert "Guo\\footnote[104]{" in text
    assert "routine abbreviation.\\footnote[106]{" in text
    assert "sec. 3.7.2\\footnote[119]{" in text


def test_ch04_no_calligraphy_note_block_spill():
    text = CH04.read_text(encoding="utf-8")
    offenders = [
        "董 found the style",
        "董 described the style",
        "陳 cites",
        "乙 Kung",
        "(fig. 7)@@",
        "upon}",
        "107 U 11 |",
        "(sec. 4.3.1.2).49",
    ]

    found = [needle for needle in offenders if needle in text]
    assert not found, "Found lingering ch04 note residue:\n" + "\n".join(found)

    assert "\\footnote[49]{On touchstone inscriptions, see n. 1.}" in text
    assert "\\pinyinterm{dong-short} found the style of period II" in text
    assert "\\pinyinterm{dong-short} found the style of period III" in text
    assert "\\pinyinterm{dong-short} found the style of period IV" in text
    assert "\\pinyinterm{dong-short} described the style of period V" in text
    assert "Yi Kung (1957)" in text


def test_appendix_note_reference_residue_removed():
    app04 = APP04.read_text(encoding="utf-8")
    app05 = APP05.read_text(encoding="utf-8")

    assert "table\\footnote[28]" not in app04
    assert "table 2.\\footnote[28]{" in app04
    assert "described in sec.\\footnote[1]" not in app05
    assert "described in sec. 4.3.1.12.\\footnote[1]{" in app05
