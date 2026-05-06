"""Regression checks for known hybrid CJK+Latin residue in live TeX."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

SUSPICIOUS_STRINGS = [
    "powerful Ho",
    "Father Chia",
    "Father Keng",
    "Father Hsin",
    "长 Kwangchih",
    "Yang 中-chien",
    "刘 董-sheng",
    "李 京-tan",
    "韦 and Yellow",
    "董 乙",
    "Huai 乙",
    "刘里-ke",
    "长 Kuang-",
    "长 光",
    "长 Tsungtung",
    "An 知-min",
    "Chan 并-leung",
    "Huang 蔡-chün",
    "Huang 京-hsin",
    "Kuan 谢楚",
    "Yü 邢-wu",
    "Lu 史-hsien",
    "董-tsuan",
    "中-hua jen-min",
    "乙-li",
    "刘-lu",
    "颜 Yün",
    "李 史",
]


def test_no_known_hybrid_name_residue_in_live_tex():
    offenders = []

    for path in (REPO_ROOT / "tex").rglob("*.tex"):
        text = path.read_text(encoding="utf-8")
        for needle in SUSPICIOUS_STRINGS:
            if needle in text:
                offenders.append(f"{path.relative_to(REPO_ROOT)}: {needle}")

    assert not offenders, "Found hybrid residue:\n" + "\n".join(offenders)
