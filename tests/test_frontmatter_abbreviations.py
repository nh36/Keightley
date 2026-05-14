"""Regression checks for the curated frontmatter abbreviation list."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTMATTER_ABBREVIATIONS = REPO_ROOT / "tex" / "frontmatter" / "abbreviations.tex"
MAIN_BODY = REPO_ROOT / "tex" / "main_body.tex"


def test_frontmatter_abbreviation_list_is_curated():
    abbreviations = FRONTMATTER_ABBREVIATIONS.read_text(encoding="utf-8")
    main_body = MAIN_BODY.read_text(encoding="utf-8")

    assert r"\input{frontmatter/abbreviations}" in main_body
    assert "% Phase 3 deliverable" not in abbreviations
    assert r"\begin{list}{}{%" in abbreviations
    assert r"\renewcommand{\makelabel}[1]{\textbf{#1}\hfill}%" in abbreviations

    assert r"\item[AYFC] Guoli Zhongyang Yanjiuyuan Lishi Yuyan Yanjiusuo zhuankan 國立中央研究院歷史語言研究所專刊 I. \booktitle{Anyang fajue baogao 安陽發掘報告}." in abbreviations
    assert r"\item[CKWP] Zhongguo Kexueyuan Kaogu Yanjiusuo 中國科學院考古研究所. \booktitle{Jiagu wenbian 甲骨文編}. Kaoguxue zhuankan yizhong dishisi hao 考古學專刊乙種第十四號." in abbreviations
    assert r"\item[CKWT] Li Xiaoding. \booktitle{Jiaguwenzi jishi 甲骨文字集釋}. Zhongyang Yanjiuyuan Lishi Yuyan Yanjiusuo zhuankan zhi wushi 中央研究院歷史語言研究所專刊之五十. 8 vols." in abbreviations
    assert r"\item[CWP] Rong Geng. \booktitle{Jinwen bian 金文編}." in abbreviations
    assert r"\item[KKHP] \booktitle{Kaogu xuebao 考古學報}." in abbreviations
    assert r"\item[S] Shima Kunio. \booktitle{Inkyo bokuji sōrui 殷墟卜辭綜類}, 2d rev. ed." in abbreviations
    assert r"\item[SKK] Takigawa Kametarō. \booktitle{Shiki kaichū kōshō 史記會注考證}." in abbreviations
    assert r"\item[TLK] \booktitle{Daliankeng 大連坑}." in abbreviations
    assert r"\item[TLTC] \booktitle{Dalu zazhi 大陸雜誌}." in abbreviations
    assert r"\item[WW] \booktitle{Wenwu 文物}." in abbreviations

    assert "Kuo-li chung-yang yen-chiu-yüan" not in abbreviations
    assert "Chung-yang yen-chiu-yüan" not in abbreviations
    assert "Chia-ku wen-pien" not in abbreviations
    assert "Ta-lien-k'eng" not in abbreviations
    assert "Ta-lu tsa-chih" not in abbreviations
    assert "Wen-wu" not in abbreviations
