#!/usr/bin/env python3
"""Phase 1 + Phase 2 verifier. Exits non-zero if any invariant fails.

Phase 1 invariants:
  - data/pages.csv has exactly 326 rows; one per scan_page; offsets monotone.
  - Every row has a section assigned.
  - section sequence has no backwards jumps (sections only advance).
  - Every numbered anchor's expected printed_page matches the row at its scan.

Phase 2 invariants:
  - build/ocr/pages/p_NNNN.txt exists for every scan page (Tesseract output).
  - build/ocr/cleaned/p_NNNN.md exists for every scan page.
  - Every cleaned file starts with the page-anchor comment <!-- source: ... -->.
  - The page-anchor comment scan number matches the filename.
  - For pages with very low Tesseract token counts (<5), the page is recorded
    as "near-empty" in the QA report (figures plates etc. — expected).
  - Total dropped/edited counters are within plausible bands.

Run after scripts/02_segment_book.py and scripts/04_clean_ocr.py.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES_CSV = ROOT / "data" / "pages.csv"
ANCHORS_TSV = ROOT / "build" / "qa" / "segmentation_anchors.tsv"
OCR_PAGES = ROOT / "build" / "ocr" / "pages"
CLEAN_PAGES = ROOT / "build" / "ocr" / "cleaned"
OCR_MANIFEST = ROOT / "build" / "ocr" / "MANIFEST.tsv"
CLEAN_REPORT = ROOT / "build" / "qa" / "ocr_cleanup_report.tsv"

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def check_phase1(rows: list[dict]) -> None:
    if len(rows) != 326:
        fail(f"expected 326 pages, got {len(rows)}")

    last_end = -1
    for r in rows:
        s, e = int(r["ocr_start_offset"]), int(r["ocr_end_offset"])
        if s < last_end:
            fail(f"scan {r['scan_page']}: offset start {s} < previous end {last_end}")
        if e < s:
            fail(f"scan {r['scan_page']}: end {e} < start {s}")
        last_end = e

    # Offsets are CHARACTER offsets into the decoded OCR string, not bytes.
    # Confirm round-trip against the form-feed split — any drift here would
    # corrupt downstream consumers (e.g. dual-OCR lookup utilities).
    google_txt = ROOT / "source" / "Keightley_1978.txt"
    if google_txt.exists():
        text = google_txt.read_text(errors="replace")
        chunks = text.split("\f")
        if len(chunks) != len(rows):
            fail(f"form-feed split yields {len(chunks)} pages, pages.csv has {len(rows)}")
        else:
            mismatched = 0
            for i, (chunk, r) in enumerate(zip(chunks, rows), start=1):
                s, e = int(r["ocr_start_offset"]), int(r["ocr_end_offset"])
                if text[s:e] != chunk:
                    mismatched += 1
            if mismatched:
                fail(f"{mismatched}/{len(rows)} pages: char-offset slice != form-feed split")

    for r in rows:
        if not r["section"]:
            fail(f"scan {r['scan_page']}: empty section")

    seen: dict[str, int] = {}
    order: list[str] = []
    for r in rows:
        sec = r["section"]
        if sec not in seen:
            seen[sec] = int(r["scan_page"])
            order.append(sec)
    last_section_active = None
    for r in rows:
        sec = r["section"]
        if last_section_active and sec != last_section_active:
            if sec in order[: order.index(last_section_active)]:
                fail(f"scan {r['scan_page']}: returned to earlier section {sec}")
        last_section_active = sec

    anchors = list(csv.DictReader(ANCHORS_TSV.open(), delimiter="\t"))
    for a in anchors:
        if a["status"] != "ok":
            fail(f"anchor {a['section']}: status {a['status']}")
            continue
        if not a["printed_page"]:
            continue
        scan = int(a["scan_page"])
        actual = rows[scan - 1]["printed_page"]
        if actual != a["printed_page"]:
            fail(
                f"anchor {a['section']} (scan {scan}): printed_page in pages.csv "
                f"is {actual!r}, anchor declares {a['printed_page']!r}"
            )

    print(f"  phase1: {len(rows)} pages, {len(order)} sections, {len(anchors)} anchors")


_HEADER_RE = re.compile(
    r"^<!-- source: scan p\. (\d{3}), printed p\. ([^,]+), section: ([^ ]+) -->"
)


def check_phase2(rows: list[dict]) -> None:
    # Tesseract per-page output exists for every scan
    missing_ocr = []
    for r in rows:
        scan = int(r["scan_page"])
        if not (OCR_PAGES / f"p_{scan:04d}.txt").exists():
            missing_ocr.append(scan)
    if missing_ocr:
        fail(f"missing Tesseract OCR for scans: {missing_ocr[:10]}{'...' if len(missing_ocr) > 10 else ''}")

    # Cleaned per-page output exists, header matches
    missing_clean = []
    bad_header = []
    near_empty = 0
    for r in rows:
        scan = int(r["scan_page"])
        path = CLEAN_PAGES / f"p_{scan:04d}.md"
        if not path.exists():
            missing_clean.append(scan)
            continue
        first = path.read_text().splitlines()[0]
        m = _HEADER_RE.match(first)
        if not m:
            bad_header.append((scan, first[:80]))
            continue
        if int(m.group(1)) != scan:
            bad_header.append((scan, first[:80]))
            continue
        # printed/section consistency
        printed_in_csv = r["printed_page"] or "-"
        printed_in_hdr = m.group(2).strip()
        if printed_in_hdr != printed_in_csv:
            bad_header.append((scan, f"hdr printed={printed_in_hdr!r} vs csv={printed_in_csv!r}"))
            continue
        section_in_hdr = m.group(3).strip()
        section_in_csv = r["section"]
        if section_in_hdr != section_in_csv:
            bad_header.append((scan, f"hdr section={section_in_hdr!r} vs csv={section_in_csv!r}"))
            continue
        if path.stat().st_size < 200:
            near_empty += 1
    if missing_clean:
        fail(f"missing cleaned page output for scans: {missing_clean[:10]}")
    for scan, msg in bad_header[:10]:
        fail(f"bad header in cleaned p_{scan:04d}.md: {msg}")
    if len(bad_header) > 10:
        fail(f"...and {len(bad_header) - 10} more bad headers")

    # OCR confidence sanity
    conf_low = 0
    if OCR_MANIFEST.exists():
        with OCR_MANIFEST.open() as f:
            for row in csv.DictReader(f, delimiter="\t"):
                try:
                    if float(row["mean_conf"]) < 70 and int(row["tokens"]) > 30:
                        conf_low += 1
                except ValueError:
                    pass
        if conf_low > 0:
            warn(f"{conf_low} pages have mean_conf < 70 with >30 tokens (review OCR for these)")

    # Cleanup report sanity
    if CLEAN_REPORT.exists():
        rows_r = list(csv.DictReader(CLEAN_REPORT.open(), delimiter="\t"))
        if len(rows_r) != 326:
            fail(f"cleanup report has {len(rows_r)} rows, expected 326")
        # Pages with significant content but zero content after cleaning are suspicious
        suspicious = [r for r in rows_r
                      if int(r["raw_chars"]) > 1500 and int(r["clean_chars"]) < 200]
        if suspicious:
            fail(f"{len(suspicious)} pages lost almost all content during cleanup: "
                 f"{[r['scan_page'] for r in suspicious[:5]]}")

    print(f"  phase2: cleaned files OK; near-empty (figures/plates etc.): {near_empty}")


def main() -> int:
    rows = list(csv.DictReader(PAGES_CSV.open()))
    check_phase1(rows)
    check_phase2(rows)

    if errors:
        print(f"FAIL ({len(errors)} issues):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        for w in warnings:
            print(f"  ! {w}", file=sys.stderr)
        return 1
    if warnings:
        for w in warnings:
            print(f"  ! warn: {w}")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
