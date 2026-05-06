"""Regression check for duplicate OCR footnote numbers after live LaTeX footnotes."""

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parent.parent
LIVE_TEX_DIRS = [
    REPO_ROOT / "tex" / "frontmatter",
    REPO_ROOT / "tex" / "chapters",
    REPO_ROOT / "tex" / "appendices",
]

FOOTNOTE_DUPLICATE_RE = re.compile(
    r"\\footnote\[(\d+)\]\{(?:[^{}]|\{[^{}]*\})*\}[ \t]*[,;:.!?\)\]\u2013\u2014-]?[ \t]*\1\b"
)


def test_no_inline_duplicate_ocr_footnote_numbers():
    offenders = []

    for base in LIVE_TEX_DIRS:
        for path in base.glob("*.tex"):
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if FOOTNOTE_DUPLICATE_RE.search(line):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{line_no}")

    assert not offenders, "Found inline duplicate OCR footnote numbers:\n" + "\n".join(offenders)
