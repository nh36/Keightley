"""Regression checks for the repaired frontmatter opening pages."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
HALFTITLE = REPO_ROOT / "tex" / "frontmatter" / "halftitle.tex"
COPYRIGHT = REPO_ROOT / "tex" / "frontmatter" / "copyright.tex"
DEDICATION = REPO_ROOT / "tex" / "frontmatter" / "dedication.tex"
EPIGRAPH = REPO_ROOT / "tex" / "frontmatter" / "epigraph.tex"


def test_halftitle_has_no_ocr_title_spill():
    text = HALFTITLE.read_text(encoding="utf-8")

    assert "Oracle-Bor" not in text
    assert "\\null" in text


def test_copyright_page_has_no_ocr_markup():
    text = COPYRIGHT.read_text(encoding="utf-8")

    assert "HEADING@@" not in text
    assert "Copyright 1978 by" in text


def test_dedication_page_has_no_library_stamp_residue():
    text = DEDICATION.read_text(encoding="utf-8")

    assert "UNIVERSITYO" not in text
    assert "WASHINGTON" not in text
    assert "SEATTLE" not in text


def test_epigraph_page_has_no_footer_residue():
    text = EPIGRAPH.read_text(encoding="utf-8")

    assert "G D C C G" not in text
    assert "De Divinatione" in text
