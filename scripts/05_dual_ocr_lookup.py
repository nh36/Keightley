#!/usr/bin/env python3
"""Dual-OCR lookup: print both Tesseract and Google-Vision OCR for a scan page.

The 1978 book has been OCR'd twice:

  1. Google Vision (supplied) — `source/Keightley_1978.txt`, split per page on
     form-feed (\\f). Generally a bit weaker than Tesseract on running prose
     but sometimes catches CJK glyphs, italics, or layout that Tesseract
     misses. Stored intact for cross-checking. Per-page text comes from the
     form-feed split (matching the segmenter's own logic). Note that the
     `ocr_start_offset` / `ocr_end_offset` columns in `data/pages.csv` are
     *character* offsets into the .read_text() decoded string, not byte
     offsets — only valid for character-level slicing.

  2. Tesseract 5.5.2 with `eng+chi_tra` (Phase 2 re-OCR) —
     `build/ocr/pages/p_NNNN.txt` (and .tsv with per-token confidence).

Use this script whenever a downstream phase (bibliography, figures, tables,
proofing) hits a low-confidence Tesseract token: print both versions side by
side and pick the more plausible reading, or merge.

Examples
--------
  # show both OCRs for scan page 275 (Bibliography A start)
  python3 scripts/05_dual_ocr_lookup.py 275

  # show with diff highlighting
  python3 scripts/05_dual_ocr_lookup.py 275 --diff

  # show a range
  python3 scripts/05_dual_ocr_lookup.py 230 --to 232

  # programmatic API used by downstream scripts: returns (tesseract, google)
  from scripts._dual_ocr import get_pair
  tess, google = get_pair(275)
"""
from __future__ import annotations

import argparse
import csv
import difflib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOOGLE_TXT = ROOT / "source" / "Keightley_1978.txt"
TESSERACT_DIR = ROOT / "build" / "ocr" / "pages"
PAGES_CSV = ROOT / "data" / "pages.csv"


def google_page(scan: int) -> str:
    """Return scan page N from the Google Vision OCR.

    The supplied OCR is form-feed delimited and produces exactly 326 chunks,
    one per scan page. We rely on the split rather than byte offsets because
    pages.csv stores *character* offsets (not byte offsets); using the split
    keeps this utility independent of that representation.
    """
    text = GOOGLE_TXT.read_text(errors="replace")
    chunks = text.split("\f")
    if not (1 <= scan <= len(chunks)):
        raise ValueError(f"scan page {scan} out of range 1..{len(chunks)}")
    return chunks[scan - 1].strip()


def tesseract_page(scan: int) -> str:
    p = TESSERACT_DIR / f"p_{scan:04d}.txt"
    return p.read_text(errors="replace") if p.exists() else ""


def get_pair(scan: int) -> tuple[str, str]:
    """Return (tesseract, google) text for scan page N."""
    return tesseract_page(scan), google_page(scan)


def show(scan: int, diff: bool = False) -> None:
    rows = list(csv.DictReader(PAGES_CSV.open()))
    r = rows[scan - 1]
    printed = r.get("printed_page") or "-"
    section = r.get("section") or "-"
    print(f"=== scan {scan:03d}  printed {printed!r}  section {section} ===")
    tess, google = get_pair(scan)
    if diff:
        diff_lines = difflib.unified_diff(
            google.splitlines(), tess.splitlines(),
            fromfile="google", tofile="tesseract", lineterm="",
        )
        print("\n".join(diff_lines))
        return
    print("--- TESSERACT ---")
    print(tess.rstrip())
    print("--- GOOGLE VISION ---")
    print(google.rstrip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scan", type=int, help="scan page number (1-326)")
    ap.add_argument("--to", type=int, default=None, help="show range scan..to")
    ap.add_argument("--diff", action="store_true", help="unified diff instead of side-by-side")
    args = ap.parse_args()
    end = args.to or args.scan
    for s in range(args.scan, end + 1):
        show(s, diff=args.diff)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
