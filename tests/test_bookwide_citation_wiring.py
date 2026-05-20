"""Regression checks for book-wide in-text citation hyperlinking."""

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "10_wire_intext_citations.py"
SPEC = importlib.util.spec_from_file_location("wire_intext_citations", SCRIPT_PATH)
wire_intext_citations = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(wire_intext_citations)

CH03 = REPO_ROOT / "tex" / "chapters" / "ch03.tex"
CH05 = REPO_ROOT / "tex" / "chapters" / "ch05.tex"


def test_no_raw_author_year_citations_remain_bookwide():
    offenders: list[str] = []
    for tex_path in wire_intext_citations.target_tex_files():
        for line_number, raw in wire_intext_citations.scan_remaining_raw_citations(tex_path):
            offenders.append(f"{tex_path.relative_to(REPO_ROOT)}:{line_number}: {raw}")

    assert not offenders, "Found remaining raw citations:\n" + "\n".join(offenders[:200])


def test_user_flagged_lefeuvre_and_basso_case_is_wired():
    text = CH03.read_text(encoding="utf-8")

    assert "Lefeuvre (1971);" not in text
    assert "Basso and Anderson (1973)." not in text
    assert r"Lefeuvre (\citeyear{Lefeuvre1971SerieH});" in text
    assert "Western Apache analogy, see Basso and Anderson" in text
    assert r"(\citeyear{BassoAnderson1973Western})." in text


def test_same_author_follow_on_years_are_wired():
    ch05 = CH05.read_text(encoding="utf-8")

    assert "Keightley (1969); (1975);" not in ch05
    assert r"\textcite{Keightley1969Public}; (\citeyear{Keightley1975The});" in ch05
