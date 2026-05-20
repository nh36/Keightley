"""Regression checks for appendix anchors and normalized internal crossrefs."""

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
VISIBLE_DUPLICATED_SECTION_RE = re.compile(
    r"""
    appendix\s+\\ref\{app:[^}]+\},\s+secs?\.\s+
    (?:\\ref\{sec:[^}]+\}(?:[\s\n]*(?:and|to|,|;)\s*)?)+
    \s*\(appendix\s+\d+,\s+secs?\.[^)]*\)
    |
    (?:\\ref\{sec:[^}]+\}(?:[\s\n]*(?:and|to|,|;)\s*)?)+
    \s*\((?:see\s+|cf\.\s+)?secs?\.[^)]*\)
    """,
    re.VERBOSE | re.MULTILINE,
)
COMMENTED_OCR_COPY_RE = re.compile(
    r"(?<!\\)%\s*was:\s*\((?:see\s+|cf\.\s+)?(?:appendix\s+\d+,\s+)?secs?\.[^)]*\)"
)


def strip_tex_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def normalized_visible_text(path: Path) -> str:
    return re.sub(r"\s+", " ", strip_tex_comments(path.read_text(encoding="utf-8"))).strip()


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
        text = strip_tex_comments(path.read_text(encoding="utf-8"))
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
            visible_lines = strip_tex_comments(path.read_text(encoding="utf-8")).splitlines()
            for line_no, line in enumerate(visible_lines, start=1):
                if "\\ref{" in line:
                    continue
                if PLAIN_INTERNAL_REF_RE.search(line):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{line_no}:{line.strip()}")

    assert not offenders, "Plain internal refs remain in non-chapter surfaces:\n" + "\n".join(offenders)


def test_visible_section_crossrefs_no_longer_duplicate_ocr_copy():
    offenders = []

    for path in sorted((REPO_ROOT / "tex").glob("**/*.tex")):
        visible = strip_tex_comments(path.read_text(encoding="utf-8"))
        match = VISIBLE_DUPLICATED_SECTION_RE.search(visible)
        if match:
            offenders.append(f"{path.relative_to(REPO_ROOT)}: {match.group(0)[:160]}")

    assert not offenders, "Visible duplicated section refs remain:\n" + "\n".join(offenders)


def test_section_crossref_comments_preserve_old_copy():
    total = 0
    for path in sorted((REPO_ROOT / "tex").glob("**/*.tex")):
        total += len(COMMENTED_OCR_COPY_RE.findall(path.read_text(encoding="utf-8")))

    assert total >= 150
    assert "% was: (see sec. 2.8)" in FIGURES.read_text(encoding="utf-8")
    assert "% was: (cf. sec. 5 below)" in APPENDICES["app04"].read_text(encoding="utf-8")
    assert "% was: (secs. 2.6 and 2.7)" in BOOK_PREAMBLE.read_text(encoding="utf-8")


def test_section_crossrefs_show_single_linked_form():
    app01 = normalized_visible_text(APPENDICES["app01"])
    app03 = normalized_visible_text(APPENDICES["app03"])
    app04 = normalized_visible_text(APPENDICES["app04"])
    ch04 = normalized_visible_text(REPO_ROOT / "tex" / "chapters" / "ch04.tex")
    ch03 = normalized_visible_text(REPO_ROOT / "tex" / "chapters" / "ch03.tex")
    figures = normalized_visible_text(FIGURES)
    book_preamble = normalized_visible_text(BOOK_PREAMBLE)

    assert "which were scraped clean (sec.~\\ref{sec:chapters-ch01:1.3.2}" in app01
    assert "so that only the bone seams are visible" in app01
    assert "secs.~\\ref{sec:appendices-app03:1} and \\ref{sec:appendices-app03:2} above" in app03
    assert "cf. sec.~\\ref{sec:appendices-app04:5} below" in app04
    assert "appendix \\ref{app:5}, secs. \\ref{sec:appendices-app05:3} and \\ref{sec:appendices-app05:4}" in ch04
    assert "no question (sec.~\\ref{sec:chapters-ch05:5.5}" in ch03
    assert "these rubbings are the primary sources" in ch03
    assert "For a translation of 拼編 235.1-2, sec.~\\ref{sec:chapters-ch02:2.8}" in figures
    assert "Exactly how the pyromantic cracks were read and by whom is not entirely clear" in book_preamble
    assert "see secs.~\\ref{sec:chapters-ch02:2.6} and \\ref{sec:chapters-ch02:2.7}" in book_preamble
