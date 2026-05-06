"""Regression checks for known hybrid and citation residue in live TeX."""

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
    "金 祥-heng",
    "徐 chia-ku wenpien",
    "徐 chia-ku wen-pien",
    "乙-wen",
    "蛟城 chia-ku wen-pien",
    "Chin Hsiang-heng",
    "Hsü chia-ku wen-pien",
    "Chiao-cheng chia-ku wen-pien",
    r"\pinyinterm{jiaguwen-bian} \pinyinterm{jiaguwen-bian}",
    "the 安陽 site",
    "at 安陽 that",
    "安陽 fa-chiieh pao-kao",
    "安陽 remains",
    "安陽 material",
    "安陽 diviners",
    "The excavation at 小屯",
    "in the 小屯 area",
    "south of 小屯",
    "sites at 小屯",
    "For the description of 小屯",
    "Hsiao-t'un",
    "Ssu-ma Ch'ien",
    "Shih-ching",
    "San-t'ung-li",
    "Shang-shu",
    "Han-shu",
    "Shih-chi",
    "Tso-chuan",
    "Meng-tzu",
    "Ku-pen chu-shu chi-nien",
    "Ti-wang shih-chi",
    "wang chan yüeh",
    "wang chan pu yüeh",
]


def test_no_known_hybrid_name_residue_in_live_tex():
    offenders = []

    for path in (REPO_ROOT / "tex").rglob("*.tex"):
        text = path.read_text(encoding="utf-8")
        for needle in SUSPICIOUS_STRINGS:
            if needle in text:
                offenders.append(f"{path.relative_to(REPO_ROOT)}: {needle}")

    assert not offenders, "Found hybrid residue:\n" + "\n".join(offenders)
