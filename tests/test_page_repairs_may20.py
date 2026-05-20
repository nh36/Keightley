from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parent.parent
CH01 = REPO_ROOT / "tex" / "chapters" / "ch01.tex"
CH02 = REPO_ROOT / "tex" / "chapters" / "ch02.tex"
CH03 = REPO_ROOT / "tex" / "chapters" / "ch03.tex"
PINYIN_TSV = REPO_ROOT / "data" / "pinyin_terms.tsv"
PINYIN_TEX = REPO_ROOT / "tex" / "generated" / "pinyin_terms.tex"
BIB = REPO_ROOT / "tex" / "bibliography" / "keightley_manual.bib"


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def test_ch01_page_12_knky_ocr_spill_removed():
    text = CH01.read_text(encoding="utf-8")
    assert "KNKY \\#13" not in text
    assert "(1" not in text.split("% source: scan 035, printed 18", 1)[0][-20:]


def test_pinyin_terms_cover_missing_days_and_traditional_shuowen():
    source = PINYIN_TSV.read_text(encoding="utf-8")
    generated = PINYIN_TEX.read_text(encoding="utf-8")

    assert "shuowen\ttitle\t說文\tShuowen\tShuōwén" in source
    assert "shuowen\ttitle\t说文\tShuowen\tShuōwén" not in source
    assert "gengxu\tday\t庚戌\tGengxu\tGēngxū" in source
    assert "gengzi\tday\t庚子\tGengzi\tGēngzǐ" in source

    assert "\\RegisterPinyinTerm{shuowen}{title}{說文}{Shuowen}{Shuōwén}" in generated
    assert "\\RegisterPinyinTerm{gengxu}{day}{庚戌}{Gengxu}{Gēngxū}" in generated
    assert "\\RegisterPinyinTerm{gengzi}{day}{庚子}{Gengzi}{Gēngzǐ}" in generated


def test_ch02_page_22_citations_are_live_and_page_28_footnotes_are_separated():
    text = CH02.read_text(encoding="utf-8")

    assert "Takashima (\\citeyear{Takashima1973Negatives}), p. 324" in text
    assert "\\pinyinterm{rao-short} [\\citeyear{Jao1959Yintai}]" in text
    assert "Serruys [\\citeyear{Serruys1974The}], p. 43" in text
    assert "Barnard [\\citeyear{Barnard1960Recently}], p. 105" in text
    assert "\\pinyinterm{zhou-fakao} et al. [\\citeyear{Chou1973Hantzu}]" in text
    assert "Keightley [\\citeyear{Keightley1972New}]" in text
    assert "Matsumaru [\\citeyear{Matsumaru1970Inshu}], pp. 65-68" in text
    assert "\\pinyinterm{dong-short} (\\citeyear{Tung1945Yin}), pt. 2, ch. 9" in text
    assert "Ikeda (\\citeyear{Ikeda1964Inkyo}), 1.15.12, 1.15.14" in text
    assert "Durrant [\\citeyear{Durrant1972Distribution}], p. 9" in text
    assert "Durrant [\\citeyear{Durrant1972Distribution}]). \\listitem{3}" in text
    assert "Matsumaru (\\citeyear{Matsumaru1963Inkyo}) has found" in text
    assert "\\pinyinterm{rao-short} (\\citeyear{Jao1959Yintai}), pp. 73-240" in text
    assert "\\pinyinposs{dong-short} hypothetical reconstruction of five scapulas ([\\citeyear{Tung1945Yin}]" in text

    assert "to pass,\\footnote[42]{" in text
    assert "prognosticated.\\footnote[43]{" in text
    assert "prognosticated.\\footnote[42]{" not in text


def test_ch03_page_47_sentence_is_not_isolated():
    text = CH03.read_text(encoding="utf-8")
    assert (
        "\\pinyinterm{jiaguxue} cannot be divorced from \\pinyinterm{jinshixue}. "
        "\\pinyinterm{shang} bronze inscriptions"
    ) in normalized(text)


def test_durrant_1972_bibliography_entry_exists():
    text = BIB.read_text(encoding="utf-8")
    assert "@unpublished{Durrant1972Distribution," in text
    assert "The Distribution of Oracle Divination According to the Cyclical Dates" in text
