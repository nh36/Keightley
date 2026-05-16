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


def test_missing_mcdowell_entry_is_now_indexed():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "McDowell", "1964", "")]

    assert keys == ["McDowell1964Partition"]


def test_missing_nakamura_entry_is_now_indexed():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Nakamura", "1934", "")]

    assert keys == ["Nakamura1934Clemmys"]


def test_chiu_shortauthor_alias_matches_manual_entry():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Ch'iu", "1972", "")]

    assert keys == ["Chiu1972DuAnyang"]


def test_ckwt_shortauthor_alias_matches_li_hsiaoting_entry():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "CKWT", "1965", "")]

    assert keys == ["LiHsiaoting1965Chiaku"]


def test_suffix_preserving_mickel_1977a_entry_is_indexed():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Mickel", "1977", "a")]

    assert keys == ["Mickel1977aIndex"]


def test_best_score_prefers_li_daliang_entry():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Li Daliang", "1972", "")]

    assert keys == ["Li1972Kuei"]


def test_best_score_prefers_wrapped_li_daliang_entry():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "As Li Daliang", "1972", "")]

    assert keys == ["Li1972Kuei"]


def test_best_score_prefers_zhang_zongdong_entry():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Zhang Zongdong", "1970", "")]

    assert keys == ["Zhang1970Der"]


def test_best_score_prefers_chardin_and_young_entry():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "De Chardin and Young", "1936", "")]

    assert keys == ["ChardinYoung1936Mammalian"]


def test_lao_kan_alias_matches_existing_entry():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Lao Kan", "1957", "")]

    assert keys == ["Lao1957Shih"]


def test_lu_shih_hsien_alias_matches_existing_entry():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Lu Shih-hsien", "1961", "")]

    assert keys == ["Lu1961Yinchi"]


def test_single_author_barnard_citation_does_not_tie_multi_author_volume():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Barnard", "1975", "")]

    assert keys == ["Barnard1975First"]


def test_page_range_filters_mickel_1976_to_dissertation():
    bib = intext_citations.load_bib_index()
    candidates = intext_citations.find_candidates(bib, "Mickel", "1976", "")
    keys = [entry["key"] for entry in intext_citations.filter_candidates_by_pages(candidates, "158-168")]

    assert keys == ["Mickel1976Semantic"]


def test_unsuffixed_britton_citation_prefers_unsuffixed_key():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Britton", "1937", "")]

    assert keys == ["Britton1937Oracle"]


def test_unsuffixed_barnard_citation_prefers_unsuffixed_key():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Barnard", "1959", "")]

    assert keys == ["Barnard1959Remarks"]


def test_unsuffixed_mickel_1974_citation_prefers_unsuffixed_key():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Mickel", "1974", "")]

    assert keys == ["Mickel1974Reduplicated"]


def test_unsuffixed_mickel_1976_citation_prefers_unsuffixed_key():
    bib = intext_citations.load_bib_index()
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, "Mickel", "1976", "")]

    assert keys == ["Mickel1976Semantic"]


def test_pinyinterm_qiu_short_citation_maps_to_manual_entry():
    bib = intext_citations.load_bib_index()
    pinyin_terms = intext_citations.load_pinyin_terms()
    matches = intext_citations.iter_line_citation_matches(
        r"The study of \pinyinterm{qiu-short} (1972) remains relevant.",
        pinyin_terms,
    )

    assert matches == [{
        "raw": r"\pinyinterm{qiu-short} (1972)",
        "surname": "Qiu",
        "year": "1972",
        "suffix": "",
        "pages": "",
        "source_kind": "pinyinterm",
        "term_key": "qiu-short",
        "term_category": "person",
    }]
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, matches[0]["surname"], matches[0]["year"], matches[0]["suffix"])]

    assert keys == ["Chiu1972DuAnyang"]


def test_pinyinterm_xu_jinxiong_suffix_maps_to_suffixed_entry():
    bib = intext_citations.load_bib_index()
    pinyin_terms = intext_citations.load_pinyin_terms()
    matches = intext_citations.iter_line_citation_matches(
        r"See \pinyinterm{xu-jinxiong-tight} (1973a) for the book-length version.",
        pinyin_terms,
    )

    assert matches == [{
        "raw": r"\pinyinterm{xu-jinxiong-tight} (1973a)",
        "surname": "Xu Jinxiong",
        "year": "1973",
        "suffix": "a",
        "pages": "",
        "source_kind": "pinyinterm",
        "term_key": "xu-jinxiong-tight",
        "term_category": "person",
    }]
    keys = [entry["key"] for entry in intext_citations.find_candidates(bib, matches[0]["surname"], matches[0]["year"], matches[0]["suffix"])]

    assert keys == ["Hsu1973aPuku"]


def test_pinyinterm_hanzi_bridge_matches_shih_entry():
    bib = intext_citations.load_bib_index()
    term = intext_citations.load_pinyin_terms()["shi-zhangru"]
    keys = [
        entry["key"]
        for entry in intext_citations.find_candidates(
            bib,
            term["pinyin_plain"],
            "1959",
            "",
            term_hanzi=term["hanzi"],
        )
    ]

    assert keys == ["Shih1959Hsiao"]


def test_pinyinterm_alias_field_matches_hsu_1974_dissertation():
    bib = intext_citations.load_bib_index()
    term = intext_citations.load_pinyin_terms()["xu-jinxiong"]
    keys = [
        entry["key"]
        for entry in intext_citations.find_candidates(
            bib,
            term["pinyin_plain"],
            "1974",
            "",
            term_hanzi=term["hanzi"],
        )
    ]

    assert keys == ["Hsu1974Scapulimantic"]


def test_pinyinterm_alias_field_matches_li_hsiaoting_entry():
    bib = intext_citations.load_bib_index()
    term = intext_citations.load_pinyin_terms()["li-xiaoting"]
    keys = [
        entry["key"]
        for entry in intext_citations.find_candidates(
            bib,
            term["pinyin_plain"],
            "1968",
            "",
            term_hanzi=term["hanzi"],
        )
    ]

    assert keys == ["LiHsiaoting1968Tsung"]


def test_pinyinterm_new_zhou_hongxiang_book_entry_is_indexed():
    bib = intext_citations.load_bib_index()
    term = intext_citations.load_pinyin_terms()["zhou-hongxiang"]
    keys = [
        entry["key"]
        for entry in intext_citations.find_candidates(
            bib,
            term["pinyin_plain"],
            "1969",
            "",
            term_hanzi=term["hanzi"],
        )
    ]

    assert keys == ["Chou1969Putzu"]


def test_pinyinterm_new_zhou_hongxiang_article_entry_is_indexed():
    bib = intext_citations.load_bib_index()
    term = intext_citations.load_pinyin_terms()["zhou-hongxiang"]
    keys = [
        entry["key"]
        for entry in intext_citations.find_candidates(
            bib,
            term["pinyin_plain"],
            "1973",
            "",
            term_hanzi=term["hanzi"],
        )
    ]

    assert keys == ["Chou1973Computer"]


def test_pinyinterm_new_su_yinghui_entry_is_indexed():
    bib = intext_citations.load_bib_index()
    term = intext_citations.load_pinyin_terms()["su-yinghui"]
    keys = [
        entry["key"]
        for entry in intext_citations.find_candidates(
            bib,
            term["pinyin_plain"],
            "1957",
            "",
            term_hanzi=term["hanzi"],
        )
    ]

    assert keys == ["Su1957Zhongguo"]


def test_pinyinterm_new_sun_haibo_entry_is_indexed():
    bib = intext_citations.load_bib_index()
    term = intext_citations.load_pinyin_terms()["sun-haibo"]
    keys = [
        entry["key"]
        for entry in intext_citations.find_candidates(
            bib,
            term["pinyin_plain"],
            "1937",
            "",
            term_hanzi=term["hanzi"],
        )
    ]

    assert keys == ["Sun1937Fushi"]


def test_bracketed_pinyinterm_year_is_detected():
    pinyin_terms = intext_citations.load_pinyin_terms()
    matches = intext_citations.iter_line_citation_matches(
        r"As \pinyinterm{yan-yiping} [1959], pp. 230, 233 already observed, the reading is secure.",
        pinyin_terms,
    )

    assert matches == [{
        "raw": r"\pinyinterm{yan-yiping} [1959], pp. 230, 233",
        "surname": "Yan Yiping",
        "year": "1959",
        "suffix": "",
        "pages": "230, 233",
        "source_kind": "pinyinterm",
        "term_key": "yan-yiping",
        "term_category": "person",
    }]
