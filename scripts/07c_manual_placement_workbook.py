#!/usr/bin/env python3
"""Dump full context for each unanchored note: body text + Tesseract prose
with already-placed neighbour positions marked, to support manual semantic
placement decisions."""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIAG = ROOT / "build" / "qa" / "footnote_unanchored_diagnostics.tsv"
OUT = ROOT / "build" / "qa" / "manual_placement_workbook.txt"
CLEANED_WITH_NOTES = ROOT / "build" / "ocr" / "cleaned_with_notes"

# Map source_scan -> path to cleaned_with_notes md
def scan_path(scan: int) -> Path:
    return CLEANED_WITH_NOTES / f"p_{scan:04d}.md"

# Find positions of currently-placed FOOTNOTE sentinels in the md
SENT_RE = re.compile(r"<!-- FOOTNOTE:(\d+) -->")
UNANCH_RE = re.compile(r"<!-- FOOTNOTE-UNANCHORED:(\d+) -->(.*?)<!-- /FOOTNOTE -->", re.DOTALL)


def main() -> int:
    rows = list(csv.DictReader(DIAG.open(), delimiter="\t"))
    out_lines: list[str] = []
    for row in rows:
        scan = int(row["source_scan"])
        note_no = int(row["note_no"])
        unit = row["unit"]
        path = scan_path(scan)
        if not path.exists():
            out_lines.append(f"### {unit} note {note_no} (scan {scan}) — MD MISSING\n\n")
            continue
        text = path.read_text()
        # Strip out the unanchored note bodies for clean prose view
        prose_only = UNANCH_RE.sub("", text)
        # Mark placed sentinels with [N⌫] markers for visibility
        prose_marked = SENT_RE.sub(r"⟦MARK\1⟧", prose_only)
        # Find this note's body
        m = re.search(rf"<!-- FOOTNOTE-UNANCHORED:{note_no} -->(.*?)<!-- /FOOTNOTE -->", text, re.DOTALL)
        body = m.group(1).strip() if m else "(BODY NOT FOUND)"
        out_lines.append("=" * 80)
        out_lines.append(f"### {unit} | note {note_no} | scan {scan} (printed {row['source_printed']}) | status: {row['status']}")
        out_lines.append("--- NOTE BODY ---")
        out_lines.append(body[:800])
        out_lines.append("--- TESSERACT PROSE (placed-marker positions shown as ⟦MARKn⟧) ---")
        out_lines.append(prose_marked[:6000])
        out_lines.append("")
    OUT.write_text("\n".join(out_lines))
    print(f"wrote {len(rows)} entries to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
