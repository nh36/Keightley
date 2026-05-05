"""Regression tests for TSV-driven pinyin term generation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_pinyin_terms_tex import generate_terms_tex


def test_generate_terms_tex_renders_expected_registrations(tmp_path):
    input_path = tmp_path / "pinyin_terms.tsv"
    output_path = tmp_path / "pinyin_terms.tex"
    input_path.write_text(
        "\n".join(
            [
                "key\tcategory\thanzi\tpinyin_plain\tpinyin_accented",
                "li-fanggui\tperson\t李方桂\tLi Fanggui\tLǐ Fāngguì",
                "renmin-gongyuan\tplace\t人民公園\tRenmin Gongyuan\tRénmín Gōngyuán",
                "dalu-zazhi\ttitle\t大陸雜誌\tDalu zazhi\tDàlù zázhì",
                "guiyou\tday\t癸酉\tGuiyou\tGuǐyǒu",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    generate_terms_tex(input_path, output_path)
    content = output_path.read_text(encoding="utf-8")

    assert (
        r"\RegisterPinyinTerm{li-fanggui}{person}{李方桂}{Li Fanggui}{Lǐ Fāngguì}"
        in content
    )
    assert (
        r"\RegisterPinyinTerm{renmin-gongyuan}{place}{人民公園}{Renmin Gongyuan}{Rénmín Gōngyuán}"
        in content
    )
    assert (
        r"\RegisterPinyinTerm{dalu-zazhi}{title}{大陸雜誌}{Dalu zazhi}{Dàlù zázhì}"
        in content
    )
    assert r"\RegisterPinyinTerm{guiyou}{day}{癸酉}{Guiyou}{Guǐyǒu}" in content
