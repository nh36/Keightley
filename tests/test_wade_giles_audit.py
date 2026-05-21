"""Regression tests for Wade-Giles audit classification noise."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from audit_wade_giles import WadeGilesAuditor


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_audit_ignores_possessive_pinyin_name_fragments():
    auditor = WadeGilesAuditor(REPO_ROOT)
    auditor.audit_all_chapters()

    findings = auditor.findings

    for noise in [
        "Athapaskan-speaking",
        "Bingquan's",
        "Cicero's",
        "Cheng",
        "Crack-making",
        "Guo's",
        "Hu",
        "Li",
        "Liu",
        "Shang",
        "Shima's",
        "Yi",
        "Yi's",
        "Yirong's",
        "Zhang's",
        "Zongdong's",
        "Zuobin's",
    ]:
        assert noise not in findings

    for preserved in ["Ping-leung", "Shih-ch'ang", "Shu-chi"]:
        assert preserved not in findings


def test_lowercase_wade_giles_residues_removed_from_live_tex():
    banned = [
        "Hsing divined",
        "[Hsing] divined",
        "kan-chih",
        "ta-tsung",
        "wei wang chi ssu",
        "chia-ch'en",
        "yi-yu",
        "yi-ssu",
        "yi-ch'ou",
        "yi-mao",
        "ping-shen",
        "hsin-ch'ou",
        "jen-yin",
        "jen-tzu",
        "ting-yu",
        "hsin-mao",
        "yung ritual",
        "hsieh ritual",
        "chui ritual",
        "hsieh-day ritual",
        "hsieh-ritual",
        "wo shih",
        "hsieh wang shih",
        "hsieh wo shih",
        "tso yi",
        "tzu yi",
        "wang hsing",
        "wang t'ien",
        "hsing-t'ien",
        "t'ien-hsing",
        "hsiang-hsing",
        "chih-shih",
        "hui-yi",
        "hsing-sheng",
        "hsieh-sheng",
        "chia-chieh",
    ]

    tex_roots = [
        REPO_ROOT / "tex" / "chapters",
        REPO_ROOT / "tex" / "appendices",
        REPO_ROOT / "tex" / "frontmatter",
        REPO_ROOT / "tex" / "plates",
    ]
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for root in tex_roots
        for path in sorted(root.rglob("*.tex"))
    )

    found = [needle for needle in banned if needle in text]
    assert not found, f"Found lingering lowercase Wade-Giles residue: {found}"
