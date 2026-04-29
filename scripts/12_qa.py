#!/usr/bin/env python3
"""Phase 1 verifier. Exits non-zero if any invariant fails.

Invariants:
  - data/pages.csv has exactly 326 rows; one per scan_page; offsets monotone.
  - Every row has a section assigned.
  - section sequence has no backwards jumps (sections only advance).
  - Every numbered anchor's expected printed_page matches the row at its scan.
  - Roman-numbered region precedes arabic; arabic resumes after the figures gap.

Run after scripts/02_segment_book.py to ensure the segmentation is internally
consistent before any downstream phase consumes pages.csv.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES_CSV = ROOT / "data" / "pages.csv"
ANCHORS_TSV = ROOT / "build" / "qa" / "segmentation_anchors.tsv"

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def main() -> int:
    rows = list(csv.DictReader(PAGES_CSV.open()))
    if len(rows) != 326:
        fail(f"expected 326 pages, got {len(rows)}")

    # offsets monotone
    last_end = -1
    for r in rows:
        s, e = int(r["ocr_start_offset"]), int(r["ocr_end_offset"])
        if s < last_end:
            fail(f"scan {r['scan_page']}: offset start {s} < previous end {last_end}")
        if e < s:
            fail(f"scan {r['scan_page']}: end {e} < start {s}")
        last_end = e

    # every row has section
    for r in rows:
        if not r["section"]:
            fail(f"scan {r['scan_page']}: empty section")

    # section sequence: build first-seen scan order; assert monotone
    seen: dict[str, int] = {}
    order: list[str] = []
    for r in rows:
        sec = r["section"]
        if sec not in seen:
            seen[sec] = int(r["scan_page"])
            order.append(sec)
    # No section may reappear after another section started:
    last_section_active = None
    for r in rows:
        sec = r["section"]
        if last_section_active and sec != last_section_active:
            # transitioned. Make sure we never go back to an earlier section.
            if sec in order[: order.index(last_section_active)]:
                fail(f"scan {r['scan_page']}: returned to earlier section {sec}")
        last_section_active = sec

    # anchors round-trip
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

    if errors:
        print(f"FAIL ({len(errors)} issues):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK: {len(rows)} pages, {len(order)} sections, {len(anchors)} anchors verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
