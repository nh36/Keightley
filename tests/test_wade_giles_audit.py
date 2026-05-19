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
        "Crack-making",
        "Guo's",
        "Shima's",
        "Yirong's",
        "Zhang's",
        "Zongdong's",
        "Zuobin's",
    ]:
        assert noise not in findings

    assert "Ping-leung" in findings
    assert "Shih-ch'ang" in findings
