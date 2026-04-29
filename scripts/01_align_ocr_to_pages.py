#!/usr/bin/env python3
"""Align the supplied OCR text to PDF page boundaries and produce data/pages.csv.

Strategy:
  source/Keightley_1978.txt is already page-delimited by form-feed (\\f). The
  primary PDF has no embedded text layer, so we cannot re-derive per-page text
  with pdftotext; we trust the supplied delimiters.

  We split on \\f and record per-page byte offsets into the OCR file. We
  cross-check that the form-feed count == (page count - 1) reported by
  pdfinfo. If it does not match, we abort: a mismatch means a human has to
  decide which side is authoritative before downstream work proceeds.

  printed_page / logical_page / section are left blank; populated by humans
  via the source audit pass (Phase 1 review gate).

Outputs:
  data/pages.csv
  build/qa/ocr_alignment_report.tsv  (per-page: chunk_chars, blank_chars, status)
"""
from __future__ import annotations

import csv
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "source" / "Keightley_1978.pdf"
OCR_TXT = ROOT / "source" / "Keightley_1978.txt"
PAGES_DIR = ROOT / "source" / "pages"
PAGES_CSV = ROOT / "data" / "pages.csv"
REPORT = ROOT / "build" / "qa" / "ocr_alignment_report.tsv"


def pdf_page_count(pdf: Path) -> int:
    out = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError("pdfinfo did not report a page count")


def split_pages(ocr_text: str) -> list[tuple[int, int, str]]:
    """Return [(start_offset, end_offset, chunk_text)] per page, splitting on \\f."""
    spans: list[tuple[int, int, str]] = []
    start = 0
    i = 0
    n = len(ocr_text)
    while i < n:
        j = ocr_text.find("\f", i)
        if j == -1:
            spans.append((start, n, ocr_text[start:n]))
            break
        # Page chunk is [start, j). Form-feed itself is the boundary, not part
        # of either page; the next page begins at j+1.
        spans.append((start, j, ocr_text[start:j]))
        start = j + 1
        i = j + 1
    return spans


def main() -> None:
    PAGES_CSV.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    ocr_full = OCR_TXT.read_text(errors="replace")
    spans = split_pages(ocr_full)

    expected = pdf_page_count(PDF)
    if len(spans) != expected:
        raise SystemExit(
            f"page count mismatch: OCR file yields {len(spans)} pages "
            f"(form-feed count + 1), pdfinfo reports {expected}. Refusing to "
            "produce pages.csv until a human decides which side is authoritative."
        )

    rows: list[dict] = []
    report_rows: list[dict] = []

    for i, (start, end, chunk) in enumerate(spans, start=1):
        image_path = f"source/pages/p_{i:04d}.png"
        chunk_chars = end - start
        non_space = sum(1 for c in chunk if not c.isspace())
        rows.append({
            "scan_page": i,
            "printed_page": "",
            "logical_page": "",
            "section": "",
            "image_path": image_path,
            "ocr_start_offset": start,
            "ocr_end_offset": end,
            "notes": "",
        })
        report_rows.append({
            "scan_page": i,
            "chunk_chars": chunk_chars,
            "non_space_chars": non_space,
            "status": "blank" if non_space == 0 else "ok",
        })

    with PAGES_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    with REPORT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(report_rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(report_rows)

    n_blank = sum(1 for r in report_rows if r["status"] == "blank")
    print(f"pages: {len(rows)}  with_text: {len(rows) - n_blank}  blank: {n_blank}")


if __name__ == "__main__":
    main()
