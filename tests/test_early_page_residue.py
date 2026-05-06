"""Regression checks for the early-page residue family in ch01/ch02."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
EARLY_CHAPTERS = [
    REPO_ROOT / "tex" / "chapters" / "ch01.tex",
    REPO_ROOT / "tex" / "chapters" / "ch02.tex",
]

SUSPICIOUS_STRINGS = [
    "k'ao-shih",
    "Lo Chen-",
    "IO. Childbirth.",
    "pu-chao chi-shu-tz'uor hsü-shu",
    "江 captives",
    "羌 captives",
    "长 [1954]",
    "长 notes",
    "董 [",
    "董 also suggested",
    "as 董 claims",
]


def test_no_early_page_residue_in_ch01_ch02():
    offenders = []

    for path in EARLY_CHAPTERS:
        text = path.read_text(encoding="utf-8")
        for needle in SUSPICIOUS_STRINGS:
            if needle in text:
                offenders.append(f"{path.relative_to(REPO_ROOT)}: {needle}")

    assert not offenders, "Found early-page residue:\n" + "\n".join(offenders)
