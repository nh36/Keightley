"""Regression checks for in-text citation matching aliases."""

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CITATION_SCRIPT_PATH = REPO_ROOT / "scripts" / "09_intext_citations.py"
SPEC = importlib.util.spec_from_file_location("intext_citations", CITATION_SCRIPT_PATH)
intext_citations = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(intext_citations)


def test_key_stem_alias_matches_tung_entry():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Tung", "1945", "")]

    assert keys == ["Tung1945Yin"]


def test_normalized_shortauthor_matches_hyphenated_name():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Hao-liang", "1977", "")]

    assert keys == ["Yu1977Shuo"]


def test_two_word_citation_name_matches_key_stem():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Jung Keng", "1947", "")]

    assert keys == ["Jung1947Chiaku"]


def test_family_name_last_token_matches_ting_su_citation():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Ting Su", "1969", "")]

    assert keys == ["Su1969Shuo"]


def test_lead_in_word_is_ignored_for_see_shima_citation():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "See Shima", "1958", "")]

    assert keys == ["Shima1958Inkyo"]
