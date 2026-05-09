"""Regression checks for the first bibliography citation-conversion tranche."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
APP04 = REPO_ROOT / "tex" / "appendices" / "app04.tex"
APP02 = REPO_ROOT / "tex" / "appendices" / "app02.tex"
CH01 = REPO_ROOT / "tex" / "chapters" / "ch01.tex"
CH02 = REPO_ROOT / "tex" / "chapters" / "ch02.tex"
CH03 = REPO_ROOT / "tex" / "chapters" / "ch03.tex"
CH05 = REPO_ROOT / "tex" / "chapters" / "ch05.tex"
BIB = REPO_ROOT / "tex" / "bibliography" / "keightley.bib"
MANUAL_BIB = REPO_ROOT / "tex" / "bibliography" / "keightley_manual.bib"
CITATION_SCRIPT = REPO_ROOT / "scripts" / "09_intext_citations.py"


def test_first_tranche_citations_are_wired():
    app02 = APP02.read_text(encoding="utf-8")
    app04 = APP04.read_text(encoding="utf-8")
    ch01 = CH01.read_text(encoding="utf-8")
    ch02 = CH02.read_text(encoding="utf-8")
    ch03 = CH03.read_text(encoding="utf-8")
    ch05 = CH05.read_text(encoding="utf-8")

    assert "Lin Sheng (1963) records" not in ch01
    assert r"\textcite{Lin1963Chi} records" in ch01

    assert "Keightley (1973), p. 537, nn. 36, 37" not in ch02
    assert r"\textcite[p. 537, nn.~36, 37]{Keightley1973Religion}" in ch02

    assert "Lin Sheng (1963), pp. 162-163" not in ch05
    assert r"\textcite[pp.~162-163]{Lin1963Chi}" in ch05

    assert "Keightley (1975), pp. 132-1740; (1975b);" not in app04
    assert r"\textcite[pp.~132--174]{Keightley1975The};" in app04
    assert r"\textcite{Keightley1975bDate};" in app04

    assert "Keightley (1975), pp. 142144" not in ch02
    assert r"\textcite[pp.~142--144]{Keightley1975The}" in ch02

    assert r"\textcite[p. 98, n. 13]{Serruys1974The}" in ch01
    assert r"\textcite[p. 86, n. 3]{Serruys1974The}" in ch02
    assert r"\textcite{Serruys1974The}" in ch03
    assert r"\textcite[esp. pp. 19-21]{Serruys1974The}" in ch03
    assert r"\textcite{Mickel1973Book}" in app02


def test_citation_inventory_skips_backmatter():
    script = CITATION_SCRIPT.read_text(encoding="utf-8")

    assert 'if "backmatter" in tex.parts:' in script
    assert 'for bib_file in sorted(BIB_DIR.glob("*.bib")):' in script
    assert 'shortauthor' in script


def test_keightley_1975b_entry_exists():
    bib = BIB.read_text(encoding="utf-8")

    assert "@book{Keightley1975bDate," in bib
    assert "The Date of the Shang Historical Period: A Progress Report" in bib


def test_manual_bibliography_entries_exist():
    bib = MANUAL_BIB.read_text(encoding="utf-8")

    assert "@book{Shima1958Inkyo," in bib
    assert "@book{Barnard1975First," in bib
    assert "@article{Barnard1960aReview," in bib
    assert "@article{Barnard1960bReview," in bib
    assert "@article{Bishop1932Scapulimancy," in bib
    assert "@article{Clark1975Calibration," in bib
    assert "@book{Kaizuka1946Chiigoku," in bib
    assert "@book{Kaizuka1967Kodai," in bib
    assert "@article{Eisenberger1938Das," in bib
    assert "@book{EvansPritchard1937Witchcraft," in bib
    assert "@article{Fujino1960Kiboku," in bib
    assert "@article{Hultkrantz1968La," in bib
    assert "@book{Ho1975Cradle," in bib
    assert "@book{Ikeda1964Inkyo," in bib
    assert "@article{Kane1973Chronological," in bib
    assert "@article{Kane1975Reexamination," in bib
    assert "@article{Lefeuvre1975Les," in bib
    assert "@book{Li1972Kuei," in bib
    assert "shortauthor = {Daliang}" in bib
    assert "@phdthesis{Mickel1976Semantic," in bib
    assert "@book{Noda1945Kanjo," in bib
    assert "shortauthor = {Noda and Yabuuchi}" in bib
    assert "@book{Smith1931Fauna," in bib
    assert "@book{Speck1935Naskapi," in bib
    assert "@article{Satow1879Ancient," in bib
    assert "@book{Shirakawa1972Kokotsubun," in bib
    assert "@phdthesis{Takashima1973Negatives," in bib
    assert "@unpublished{Takashima1976Subordinate," in bib
    assert "@book{Tung1945Yin," in bib
    assert "@article{Tung1953Chia," in bib
    assert "@article{Nivison1977Three," in bib
    assert "@book{Wheatley1971Pivot," in bib
    assert "@book{Woodhead1967Study," in bib
    assert "@book{Zhang1970Der," in bib
    assert "shortauthor = {Zongdong}" in bib
