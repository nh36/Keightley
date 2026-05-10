"""Regression checks for live bibliography backmatter wiring."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BIBLIO_A = REPO_ROOT / "tex" / "backmatter" / "biblio_a.tex"
BIBLIO_B = REPO_ROOT / "tex" / "backmatter" / "biblio_b.tex"
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build.sh"
EXTRACT_SCRIPT = REPO_ROOT / "scripts" / "08_extract_bibliography.py"
PREAMBLE = REPO_ROOT / "tex" / "preamble.tex"
MANUAL_BIB = REPO_ROOT / "tex" / "bibliography" / "keightley_manual.bib"
GENERATED_BIB = REPO_ROOT / "tex" / "bibliography" / "keightley.bib"


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
    assert r"\AtEveryBibitem{\clearfield{note}}" in preamble
    assert MANUAL_BIB.exists()


def test_generated_bibliography_qa_uses_annotation_not_note():
    extract_script = EXTRACT_SCRIPT.read_text(encoding="utf-8")

    assert "CHECK annotation" in extract_script
    assert "MANUAL_OVERRIDE_KEYS" in extract_script
    assert '"Chti1948Shih"' in extract_script
    assert '"Deydier1974BALD"' in extract_script
    assert '"Hsiao1976Work"' in extract_script
    assert '"Studies1970The"' in extract_script
    assert '"Japan1972Work"' in extract_script
    assert '"Cheng1974Kao"' in extract_script
    assert '"LPR1959Some"' in extract_script
    assert '"Britton1968Divination"' in extract_script
    assert '"  annotation   = {CHECK: bibliography extraction artifacts retained "' in extract_script
    assert '"  note        = {CHECK: bibliography extraction artifacts retained "' not in extract_script


def test_first_manual_override_tranche_replaces_corrupted_top_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{Bishop1932Chronology," in manual_bib
    assert "@article{Bishop1932Scapulimancy," not in manual_bib
    assert "@incollection{Andree1906Scapulimantia," in manual_bib
    assert "@article{Auffenberg1962Status," in manual_bib
    assert "@book{Barnard1974Mao," in manual_bib
    assert "@book{Britton1937aYin," in manual_bib

    assert "@book{LPR1959Some," not in generated_bib
    assert "@article{Bawden1958Practice," not in generated_bib
    assert "@book{Britton1968Divination," not in generated_bib


def test_second_manual_override_tranche_replaces_corrupted_c_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{Chang1972Rediscovery," in manual_bib
    assert "@article{Chang1963Shang," in manual_bib
    assert "@article{Zhang1954Yin," in manual_bib
    assert "@book{Chao1970Marriage," in manual_bib
    assert "@article{Cheng1974Kao," in manual_bib

    assert "@book{Japan1972Work," not in generated_bib
    assert "@book{Japan1972The," not in generated_bib
    assert "@book{Chang1954Yin," not in generated_bib
    assert "@book{Chao1970Marriage," not in generated_bib
    assert "@article{Cheng1971The," not in generated_bib


def test_third_manual_override_tranche_replaces_corrupted_chen_to_creel_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@article{Chen1951Chiapien," in manual_bib
    assert "@article{Chin1962aKufang," in manual_bib
    assert "@incollection{Chou1968Early," in manual_bib
    assert "@article{Chu1965aShihchi," in manual_bib
    assert "@book{CooleyLohnes1971Multivariate," in manual_bib
    assert "@book{Creel1938Studies," in manual_bib

    assert "@book{Chen1936Yin," not in generated_bib
    assert "@book{Chin1962Shih," not in generated_bib
    assert "@book{Chou1968The," not in generated_bib
    assert "@book{Chti1948Shih," not in generated_bib
    assert "@book{Studies1970The," not in generated_bib


def test_fourth_manual_override_tranche_replaces_corrupted_d_to_h_block():
    manual_bib = MANUAL_BIB.read_text(encoding="utf-8")
    generated_bib = GENERATED_BIB.read_text(encoding="utf-8")

    assert "@book{Deydier1976Jiaguwen," in manual_bib
    assert "@article{Gelb1967Approaches," in manual_bib
    assert "@article{Gibson1934Picture," in manual_bib
    assert "@article{Hayashi1968Inshu," in manual_bib
    assert "@article{Hopkins1938Ancestral," in manual_bib
    assert "@article{Hsiao1976Anyang," in manual_bib

    assert "@book{Deydier1974BALD," not in generated_bib
    assert "@book{Eberhard1937Witchcraft," not in generated_bib
    assert "@article{Gardner1934The," not in generated_bib
    assert "@book{Hiroshima1973The," not in generated_bib
    assert "@book{Hsiao1976Work," not in generated_bib
