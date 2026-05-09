"""Regression checks for live bibliography backmatter wiring."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BIBLIO_A = REPO_ROOT / "tex" / "backmatter" / "biblio_a.tex"
BIBLIO_B = REPO_ROOT / "tex" / "backmatter" / "biblio_b.tex"
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build.sh"
PREAMBLE = REPO_ROOT / "tex" / "preamble.tex"
MANUAL_BIB = REPO_ROOT / "tex" / "bibliography" / "keightley_manual.bib"


def test_backmatter_bibliography_files_are_live():
    biblio_a = BIBLIO_A.read_text(encoding="utf-8")
    biblio_b = BIBLIO_B.read_text(encoding="utf-8")

    assert "STUB" not in biblio_a
    assert "STUB" not in biblio_b

    assert r"\input{backmatter/abbreviations_live}" in biblio_a
    assert r"\printbibliography[heading=none]" in biblio_b
    assert r"\nocite{*}" in biblio_b


def test_build_script_runs_biber():
    build_script = BUILD_SCRIPT.read_text(encoding="utf-8")

    assert "command -v biber" in build_script
    assert '--input-directory="$BUILD_OUTPUT"' in build_script
    assert 'run_xelatex_pass 3' in build_script
    assert "render_abbreviations_tex.py" in build_script


def test_manual_bibliography_resource_is_loaded():
    preamble = PREAMBLE.read_text(encoding="utf-8")

    assert r"\addbibresource{bibliography/keightley.bib}" in preamble
    assert r"\addbibresource{bibliography/keightley_manual.bib}" in preamble
    assert MANUAL_BIB.exists()
