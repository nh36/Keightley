"""Regression checks for appendix anchors and duplicated internal crossrefs."""

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parent.parent

APPENDICES = {
    "app01": REPO_ROOT / "tex" / "appendices" / "app01.tex",
    "app02": REPO_ROOT / "tex" / "appendices" / "app02.tex",
    "app03": REPO_ROOT / "tex" / "appendices" / "app03.tex",
    "app04": REPO_ROOT / "tex" / "appendices" / "app04.tex",
    "app05": REPO_ROOT / "tex" / "appendices" / "app05.tex",
}

CH01 = REPO_ROOT / "tex" / "chapters" / "ch01.tex"
CH02 = REPO_ROOT / "tex" / "chapters" / "ch02.tex"
CH03 = REPO_ROOT / "tex" / "chapters" / "ch03.tex"
CH04 = REPO_ROOT / "tex" / "chapters" / "ch04.tex"
CH05 = REPO_ROOT / "tex" / "chapters" / "ch05.tex"
FIGURES = REPO_ROOT / "tex" / "plates" / "figures.tex"
PREFACE = REPO_ROOT / "tex" / "frontmatter" / "preface.tex"
BOOK_PREAMBLE = REPO_ROOT / "tex" / "frontmatter" / "book-preamble.tex"

NONCHAPTER_CROSSREF_DIRS = [
    REPO_ROOT / "tex" / "appendices",
    REPO_ROOT / "tex" / "frontmatter",
    REPO_ROOT / "tex" / "plates",
]
PLAIN_INTERNAL_REF_RE = re.compile(r"\bsecs?\.\s+[0-9]|\bappendix\s+[1-5]\b")


def test_appendix_internal_section_labels_exist():
    expected = {
        "app01": ["sec:appendices-app01:2", "sec:appendices-app01:3", "sec:appendices-app01:4"],
        "app02": ["sec:appendices-app02:1", "sec:appendices-app02:2", "sec:appendices-app02:3"],
        "app03": [
            "sec:appendices-app03:1",
            "sec:appendices-app03:2",
            "sec:appendices-app03:3",
            "sec:appendices-app03:4",
        ],
        "app04": [
            "sec:appendices-app04:1",
            "sec:appendices-app04:2",
            "sec:appendices-app04:3",
            "sec:appendices-app04:4",
            "sec:appendices-app04:5",
            "sec:appendices-app04:6",
        ],
        "app05": [
            "sec:appendices-app05:1",
            "sec:appendices-app05:2",
            "sec:appendices-app05:3",
            "sec:appendices-app05:4",
            "sec:appendices-app05:5",
            "sec:appendices-app05:6",
        ],
    }

    for key, labels in expected.items():
        text = APPENDICES[key].read_text(encoding="utf-8")
        missing = [label for label in labels if f"\\appendixsectionlabel{{{label}}}" not in text]
        assert not missing, f"Missing appendix labels in {key}: {missing}"


def test_no_malformed_double_section_refs_remain():
    offenders = []
    for path in (REPO_ROOT / "tex").glob("**/*.tex"):
        text = path.read_text(encoding="utf-8")
        if "see see sec." in text or "cf. cf. sec." in text:
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert not offenders, "Malformed duplicated section refs remain:\n" + "\n".join(offenders)


def test_external_chapter_citations_remain_plain():
    ch01 = CH01.read_text(encoding="utf-8")
    ch05 = CH05.read_text(encoding="utf-8")

    assert "see 史赤, ch. 128." in ch01
    assert "SKK, ch. 128, pp. 26-27; CLCY, ch. 48, pp. 2a-b" in ch01
    assert "pt. 2, ch. 5, pp. 22a ff.; ch. 8, pp. 12a-13a;" in ch05
    assert "\\pinyinterm{zhuixin}, ch. 10, passim," in ch05


def test_appendix_note_citations_remain_plain():
    ch01 = CH01.read_text(encoding="utf-8")
    ch05 = CH05.read_text(encoding="utf-8")

    assert "(appendix 3, n. 11)" in ch01
    assert "See appendix 3, nn. 12, 14." in ch01
    assert "see appendix 3, n. 5." in ch05
    assert "see appendix 3, n. 2." in ch05


def test_chapter_note_citations_remain_plain():
    preface = PREFACE.read_text(encoding="utf-8")
    book_preamble = BOOK_PREAMBLE.read_text(encoding="utf-8")

    assert "See ch. 4, n. 24." in preface
    assert "See ch. 2, n. 2." in preface
    assert "see ch. 3, nn. 85, 98." in book_preamble
    assert "see ch. 3, n. 98." in book_preamble
    assert "see ch. 1, n. 97." in book_preamble
    assert "see the works cited in ch. 5, n. 8." in book_preamble


def test_nonchapter_surfaces_have_no_plain_internal_refs():
    offenders = []

    for directory in NONCHAPTER_CROSSREF_DIRS:
        for path in sorted(directory.glob("*.tex")):
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if "\\ref{" in line:
                    continue
                if PLAIN_INTERNAL_REF_RE.search(line):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{line_no}:{line.strip()}")

    assert not offenders, "Plain internal refs remain in non-chapter surfaces:\n" + "\n".join(offenders)


def test_appendix_crossrefs_show_ref_plus_ocr_copy():
    assert (
        "appendix \\ref{app:1}, sec. \\ref{sec:appendices-app01:4} (appendix 1, sec. 4)"
        in CH01.read_text(encoding="utf-8")
    )
    assert (
        "appendix \\ref{app:5}, sec. \\ref{sec:appendices-app05:2} (appendix 5, sec. 2)"
        in CH02.read_text(encoding="utf-8")
    )
    assert (
        "appendix \\ref{app:4}, sec. \\ref{sec:appendices-app04:6} (appendix 4, sec. 6)"
        in CH03.read_text(encoding="utf-8")
    )
    assert (
        "appendix \\ref{app:4}, sec. \\ref{sec:appendices-app04:5} (appendix 4, sec. 5)"
        in CH04.read_text(encoding="utf-8")
    )
    assert (
        "appendix \\ref{app:5}, sec. \\ref{sec:appendices-app05:2} (appendix 5, sec. 2)"
        in CH05.read_text(encoding="utf-8")
    )


def test_app01_section_crossrefs_show_ref_plus_ocr_copy():
    text = APPENDICES["app01"].read_text(encoding="utf-8")

    assert "\\ref{sec:chapters-ch05:5.4} (sec. 5.4)" in text
    assert "\\ref{sec:chapters-ch01:1.3.2} (sec. 1.3.2)" in text


def test_app02_section_crossrefs_show_ref_plus_ocr_copy():
    text = APPENDICES["app02"].read_text(encoding="utf-8")

    assert (
        "appendix\n\\ref{app:3}, sec. \\ref{sec:appendices-app03:1} "
        "(appendix 3, sec. 1)"
    ) in text
    assert "\\ref{sec:chapters-ch01:1.3.2} (sec. 1.3.2)" in text
    assert "\\ref{sec:chapters-ch01:1.2.3} (sec. 1.2.3)" in text


def test_app03_section_crossrefs_show_ref_plus_ocr_copy():
    text = APPENDICES["app03"].read_text(encoding="utf-8")

    assert "\\ref{sec:chapters-ch03:3.7.4.1} (sec. 3.7.4.1)" in text
    assert "\\ref{sec:chapters-ch02:2.9.3} (sec. 2.9.3)" in text
    assert "\\ref{sec:chapters-ch01:1.4} (sec. 1.4)" in text
    assert "\\ref{sec:chapters-ch03:3.7} (see sec. 3.7)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.6} (sec. 4.3.1.6)" in text
    assert "\\ref{sec:chapters-ch03:3.3.2} (sec. 3.3.2)" in text
    assert "appendix \\ref{app:4} (appendix 4)" in text
    assert (
        "appendix \\ref{app:4}, sec. \\ref{sec:appendices-app04:5} "
        "(appendix 4, sec. 5)"
    ) in text
    assert (
        "\\ref{sec:appendices-app03:1} and \\ref{sec:appendices-app03:2} "
        "(sec. 1 and 2 above)"
    ) in text
    assert "\\ref{sec:appendices-app03:3} (sec. 3)" in text
    assert "\\ref{sec:appendices-app03:1} (sec. 1)" in text


def test_app04_section_crossrefs_show_ref_plus_ocr_copy():
    text = APPENDICES["app04"].read_text(encoding="utf-8")

    assert "\\ref{sec:appendices-app04:5} (cf. sec. 5 below)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.7} (sec. 4.3.1.7)" in text
    assert "\\ref{sec:chapters-ch05:5.3.2} (sec. 5.3.2)" in text


def test_app05_section_crossrefs_show_ref_plus_ocr_copy():
    text = APPENDICES["app05"].read_text(encoding="utf-8")

    assert "\\ref{sec:chapters-ch04:4.3.1.12} (sec. 4.3.1.12)" in text
    assert "\\ref{sec:chapters-ch03:3.7.4.2} (sec. 3.7.4.2)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.5} (cf. sec. 4.3.1.5)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.7} (sec. 4.3.1.7)" in text
    assert "\\ref{sec:chapters-ch03:3.3.2} (sec. 3.3.2)" in text
    assert "\\ref{sec:chapters-ch04:4.1.1} (sec. 4.1.1)" in text
    assert "\\ref{sec:chapters-ch03:3.6.3} (sec. 3.6.3)" in text


def test_ch01_section_crossrefs_show_ref_plus_ocr_copy():
    text = CH01.read_text(encoding="utf-8")

    assert "\\ref{sec:chapters-ch01:1.2.2} (sec. 1.2.2)" in text
    assert "appendix \\ref{app:1} (appendix 1)" in text
    assert "appendix \\ref{app:2} (appendix 2)" in text
    assert (
        "\\ref{sec:chapters-ch01:1.3}; \\ref{sec:chapters-ch01:1.5} "
        "(secs. 1.3; 1.5)"
    ) in text
    assert "\\ref{sec:chapters-ch01:1.4} (sec. 1.4)" in text
    assert "\\ref{sec:chapters-ch01:1.5} (sec. 1.5)" in text
    assert "\\ref{sec:chapters-ch01:1.5.2} (sec. 1.5.2)" in text
    assert (
        "\\ref{sec:chapters-ch01:1.2.4}\nand \\ref{sec:chapters-ch01:1.4} "
        "(secs. 1.2.4 and 1.4)"
    ) in text
    assert "\\ref{sec:chapters-ch02:2.4} (sec. 2.4)" in text
    assert "\\ref{sec:chapters-ch02:2.7} (sec. 2.7)" in text
    assert "\\ref{sec:chapters-ch02:2.8} (sec. 2.8)" in text
    assert "\\ref{sec:chapters-ch02:2.9.4} (sec. 2.9.4)" in text
    assert "\\ref{sec:chapters-ch02:2.10} (sec. 2.10)" in text
    assert "\\ref{sec:chapters-ch04:4.3.2.5} (sec. 4.3.2.5)" in text
    assert (
        "\\ref{sec:chapters-ch04:4.3.2.2} and \\ref{sec:chapters-ch04:4.3.2.3} "
        "(secs. 4.3.2.2 and 4.3.2.3)"
    ) in text


def test_ch02_section_crossrefs_show_ref_plus_ocr_copy():
    text = CH02.read_text(encoding="utf-8")

    assert "\\ref{sec:chapters-ch02:2.8} (sec. 2.8)" in text
    assert "\\ref{sec:chapters-ch02:2.7} (sec. 2.7)" in text
    assert "\\ref{sec:chapters-ch02:2.7.1} (sec. 2.7.1)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.2} (sec. 4.3.1.2)" in text
    assert "\\ref{sec:chapters-ch03:3.3.2} (sec. 3.3.2)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.12} (sec. 4.3.1.12)" in text
    assert "\\ref{sec:chapters-ch02:2.4} (sec. 2.4)" in text
    assert "\\ref{sec:chapters-ch02:2.5} (sec. 2.5)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.11} (sec. 4.3.1.11)" in text
    assert (
        "\\ref{sec:chapters-ch01:1.5.1}; \\ref{sec:chapters-ch01:1.6.2}; "
        "\\ref{sec:chapters-ch01:1.6.3} (secs. 1.5.1; 1.6.2; 1.6.3)"
    ) in text
    assert "\\ref{sec:chapters-ch03:3.7.1.2} (sec. 3.7.1.2)" in text
    assert text.count("\\ref{sec:chapters-ch03:3.7} (see sec. 3.7)") >= 2
    assert "\\ref{sec:chapters-ch03:3.7.4} (sec. 3.7.4)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.8} (sec. 4.3.1.8)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.3} (sec. 4.3.1.3)" in text
    assert (
        "\\ref{sec:chapters-ch04:4.3.1.3} and \\ref{sec:chapters-ch04:4.3.1.4} "
        "(secs. 4.3.1.3 and 4.3.1.4)"
    ) in text
    assert "\\ref{sec:chapters-ch01:1.6.3} (sec. 1.6.3)" in text
    assert "\\ref{sec:chapters-ch05:5.7} (sec. 5.7)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.10} (sec. 4.3.1.10)" in text
    assert "\\ref{sec:chapters-ch02:2.12} (sec. 2.12)" in text
    assert "\\ref{sec:chapters-ch01:1.3.3} (sec. 1.3.3)" in text
    assert "\\ref{sec:chapters-ch02:2.10} (sec. 2.10)" in text


def test_ch03_section_crossrefs_show_ref_plus_ocr_copy():
    text = CH03.read_text(encoding="utf-8")

    assert "\\ref{sec:chapters-ch03:3.3.1} (sec. 3.3.1)" in text
    assert "\\ref{sec:chapters-ch03:3.3.2} (sec. 3.3.2)" in text
    assert "\\ref{sec:chapters-ch03:3.5.2} (sec. 3.5.2)" in text
    assert "\\ref{sec:chapters-ch05:5.6} (sec.\n5.6)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.4} (sec. 4.3.1.4)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.3} (sec. 4.3.1.3)" in text
    assert "\\ref{sec:chapters-ch02:2.9.4} (sec. 2.9.4)" in text
    assert "\\ref{sec:chapters-ch03:3.7.4.2} (sec. 3.7.4.2)" in text
    assert "\\ref{sec:chapters-ch03:3.7.3} (sec. 3.7.3)" in text
    assert "\\ref{sec:chapters-ch02:2.6} (sec. 2.6)" in text
    assert "\\ref{sec:chapters-ch03:3.7.2} (sec. 3.7.2)" in text
    assert "\\ref{sec:chapters-ch02:2.12} (sec. 2.12)" in text
    assert "\\ref{sec:chapters-ch02:2.12.1} (sec. 2.12.1)" in text
    assert "\\ref{sec:chapters-ch03:3.7.4} (sec. 3.7.4)" in text
    assert "\\ref{sec:chapters-ch01:1.6.4} (sec. 1.6.4)" in text
    assert "\\ref{sec:chapters-ch01:1.4} (sec. 1.4)" in text
    assert "\\ref{sec:chapters-ch01:1.2.4} (sec. 1.2.4)" in text
    assert "\\ref{sec:chapters-ch01:1.5} (sec. 1.5)" in text
    assert "[\\ref{sec:chapters-ch02:2.5} (sec. 2.5)]" in text
    assert "[\\ref{sec:chapters-ch02:2.4} (sec. 2.4)]" in text
    assert (
        "\\ref{sec:chapters-ch03:3.6.1} to \\ref{sec:chapters-ch03:3.6.3} "
        "(secs. 3.6.1 to 3.6.3)"
    ) in text
    assert "\\ref{sec:chapters-ch03:3.6.3} (sec. 3.6.3)" in text


def test_ch04_section_crossrefs_show_ref_plus_ocr_copy():
    text = CH04.read_text(encoding="utf-8")

    assert "\\ref{sec:chapters-ch03:3.3.2} (sec. 3.3.2)" in text
    assert "[\\ref{sec:chapters-ch03:3.3.1} (sec. 3.3.1)]" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.12} (sec. 4.3.1.12)" in text
    assert (
        "appendix \\ref{app:5}, secs. \\ref{sec:appendices-app05:3} and "
        "\\ref{sec:appendices-app05:4} (appendix 5, secs. 3 and 4)"
    ) in text
    assert "\\ref{sec:chapters-ch04:4.3.1.1} (sec. 4.3.1.1)" in text
    assert "\\ref{sec:chapters-ch02:2.9.3} (sec. 2.9.3)" in text
    assert "[\\ref{sec:chapters-ch04:4.3.2.4} (sec. 4.3.2.4)]" in text
    assert "\\ref{sec:chapters-ch02:2.2.1.1} (sec. 2.2.1.1)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.3} (sec. 4.3.1.3)" in text
    assert "\\ref{sec:chapters-ch03:3.7} (sec. 3.7)" in text
    assert "\\ref{sec:chapters-ch02:2.11} (sec. 2.11)" in text
    assert "\\ref{sec:chapters-ch01:1.4} (sec. 1.4)" in text
    assert "\\ref{sec:chapters-ch02:2.2} (sec. 2.2)" in text
    assert "\\ref{sec:chapters-ch02:2.8} (sec. 2.8)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.11} (sec. 4.3.1.11)" in text
    assert "\\ref{sec:chapters-ch02:2.5} (sec. 2.5)" in text
    assert "period (appendix \\ref{app:3} (appendix 3)) must consider" in text
    assert "\\ref{sec:chapters-ch04:4.3.2.3} (sec. 4.3.2.3)" in text
    assert "\\ref{sec:chapters-ch01:1.2.3} (sec. 1.2.3)" in text
    assert "\\ref{sec:chapters-ch01:1.3.1} (sec. 1.3.1)" in text
    assert "\\ref{sec:chapters-ch01:1.3.2} (sec. 1.3.2)" in text
    assert "\\ref{sec:chapters-ch01:1.5.1} (sec. 1.5.1)" in text
    assert "\\ref{sec:chapters-ch04:4.3.3.2} (sec. 4.3.3.2)" in text
    assert "\\ref{sec:chapters-ch02:2.9.3} (sec. 2.9.3)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.2} (sec. 4.3.1.2)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.1} (sec. 4.3.1.1)" in text
    assert (
        "appendix\n\\ref{app:4}, sec. \\ref{sec:appendices-app04:4} "
        "(appendix 4, sec. 4)"
    ) in text
    assert "appendix \\ref{app:5} (appendix 5)" in text
    assert (
        "\\ref{sec:chapters-ch04:4.3.1.3} and\n\\ref{sec:chapters-ch04:4.3.1.4} "
        "(secs. 4.3.1.3 and 4.3.1.4)"
    ) in text
    assert (
        "\\ref{sec:chapters-ch02:2.4}, \\ref{sec:chapters-ch02:2.5} "
        "(secs. 2.4, 2.5)"
    ) in text


def test_ch05_section_crossrefs_show_ref_plus_ocr_copy():
    text = CH05.read_text(encoding="utf-8")

    assert "\\ref{sec:chapters-ch02:2.3.1} (sec. 2.3.1)" in text
    assert text.count("\\ref{sec:chapters-ch02:2.3.1} (sec. 2.3.1)") >= 2
    assert "\\ref{sec:chapters-ch05:5.3.2} (sec. 5.3.2)" in text
    assert "\\ref{sec:chapters-ch05:5.3.1} (sec. 5.3.1)" in text
    assert "\\ref{sec:chapters-ch03:3.3.2} (sec. 3.3.2)" in text
    assert "\\ref{sec:chapters-ch03:3.6.1} (sec. 3.6.1)" in text
    assert "\\ref{sec:chapters-ch03:3.5} (sec. 3.5)" in text
    assert "\\ref{sec:chapters-ch03:3.7} (sec. 3.7)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.7} (sec. 4.3.1.7)" in text
    assert (
        "\\ref{sec:chapters-ch04:4.3.1.8}, \\ref{sec:chapters-ch04:4.3.1.9} "
        "(secs. 4.3.1.8, 4.3.1.9)"
    ) in text
    assert "\\ref{sec:chapters-ch04:4.3.1.11} (sec. 4.3.1.11)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.10} (sec. 4.3.1.10)" in text
    assert "\\ref{sec:chapters-ch04:4.3.1.12} (sec. 4.3.1.12)" in text
    assert "\\ref{sec:chapters-ch02:2.10} (sec. 2.10)" in text
    assert "\\ref{sec:chapters-ch05:5.7} (sec. 5.7)" in text
    assert "\\ref{sec:chapters-ch05:5.4.1} (sec. 5.4.1)" in text
    assert "appendix \\ref{app:3} (appendix 3)" in text
    assert "\\ref{sec:chapters-ch01:1.3.1} (sec. 1.3.1)" in text
    assert (
        "\\ref{sec:chapters-ch01:1.5.1}; \\ref{sec:chapters-ch02:2.4};"
        "\n\\ref{sec:chapters-ch02:2.6}; \\ref{sec:chapters-ch02:2.9.4} "
        "(secs. 1.5.1; 2.4; 2.6; 2.9.4)"
    ) in text
    assert (
        "\\ref{sec:chapters-ch02:2.6}, \\ref{sec:chapters-ch02:2.8} "
        "(secs. 2.6, 2.8)"
    ) in text


def test_figure_caption_section_crossrefs_show_ref_plus_ocr_copy():
    text = FIGURES.read_text(encoding="utf-8")

    assert (
        "For a translation of 拼編 235.1-2, \\ref{sec:chapters-ch02:2.8} "
        "(see sec. 2.8)."
    ) in text
    assert (
        "For a translation of 拼編 248.7, \\ref{sec:chapters-ch02:2.7} "
        "(see sec. 2.7)"
    ) in text
    assert "For a translation, \\ref{sec:chapters-ch02:2.8} (see sec. 2.8)." in text
    assert (
        "For a translation, \\ref{sec:chapters-ch03:3.6.3} "
        "(see sec. 3.6.3)."
    ) in text


def test_preface_internal_crossrefs_show_ref_plus_ocr_copy():
    text = PREFACE.read_text(encoding="utf-8")

    assert "appendix \\ref{app:4} (appendix 4)" in text
    assert (
        "\\booktitle{Inkyo bokuji sōrui} "
        "(\\ref{sec:chapters-ch03:3.3.2} (sec. 3.3.2))"
    ) in text
    assert "\\ref{sec:chapters-ch05:5.6} (sec. 5.6)" in text
    assert "appendix \\ref{app:1} (appendix 1)" in text


def test_book_preamble_internal_crossrefs_show_ref_plus_ocr_copy():
    text = BOOK_PREAMBLE.read_text(encoding="utf-8")

    assert "\\ref{sec:chapters-ch03:3.7} (sec. 3.7)" in text
    assert (
        "\\ref{sec:chapters-ch02:2.6} and \\ref{sec:chapters-ch02:2.7} "
        "(secs. 2.6 and 2.7)"
    ) in text
