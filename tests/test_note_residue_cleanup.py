"""Regression checks for recent inline note-residue cleanup."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CH01 = REPO_ROOT / "tex" / "chapters" / "ch01.tex"
CH02 = REPO_ROOT / "tex" / "chapters" / "ch02.tex"
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
    assert "Yi Kung (1957)" not in text
    assert r"Yi Kung (\citeyear{Yi1957Mantan})" in text


def test_ch01_and_ch02_long_note_sentinel_runs_removed():
    ch01 = CH01.read_text(encoding="utf-8")
    ch02 = CH02.read_text(encoding="utf-8")

    assert "535455565758" not in ch01
    assert "146147148149150151152153" not in ch02

    assert "smoothed.\\footnote[53]{" in ch01
    assert "thickness (fig. 3).\\footnote[54]{" in ch01
    assert "written on.\\footnote[55]{" in ch01
    assert "tie them together.\\footnote[56]{" in ch01
    assert "period V.\\footnote[57]{" in ch01
    assert "had been formed\\footnote[58]{" in ch01

    assert "black.\\footnote[146]{" in ch02
    assert "with brown.\\footnote[147]{" in ch02
    assert "clear.\\footnote[148]{" in ch02
    assert "beautiful.''\\footnote[149]{" in ch02
    assert "matter.''\\footnote[150]{" in ch02
    assert "divining rod.\\footnote[151]{" in ch02
    assert "notations were.\\footnote[152]{" in ch02
    assert "determined.\\footnote[153]{" in ch02
    assert 'exercise sheets."100' not in ch02
    assert "shell. 102 We are" not in ch02
    assert "exercise sheets.''\\footnote[100]{" in ch02
    assert "shell.\\footnote[102]{" in ch02
    assert "Ti 乙" not in ch02


def test_appendix_note_reference_residue_removed():
    app04 = APP04.read_text(encoding="utf-8")
    app05 = APP05.read_text(encoding="utf-8")

    assert "table\\footnote[28]" not in app04
    assert "table 2.\\footnote[28]{" in app04
    assert "described in sec.\\footnote[1]" not in app05
    assert "described in sec. 4.3.1.12.\\footnote[1]{" in app05


def test_cross_chapter_footnote_and_name_residue_removed():
    ch03 = CH03.read_text(encoding="utf-8")
    ch04 = CH04.read_text(encoding="utf-8")

    assert "first published by 董" not in ch03
    assert "Wang 乙-jung" not in ch03
    assert "刘 E" not in ch03
    assert "Wang Yi-jung and Liu E" in ch03

    assert "vice versa.¹ 179" not in ch04
    assert "(V).8 These dating" not in ch04
    assert "significant.\\footnote[179]" not in ch04
    assert "董 concluded that the pit" not in ch04
    assert "董 and his" not in ch04
    assert "Ti 乙" not in ch04
    assert "vice versa.\\footnote[179]{" in ch04
    assert "significant.\\footnote[180]{" in ch04
    assert "appeared.\\footnote[181]{" in ch04
    assert "Chia-pien.\\footnote[182]{" in ch04
    assert "Late (V).\\footnote[8]{" in ch04
    assert "comparative certainty.\\footnote[10]{" in ch04
    assert "historical terms.\\footnote[11]{" in ch04
