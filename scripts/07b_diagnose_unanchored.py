"""Diagnose every unanchored footnote.

For each row in build/qa/footnote_inventory.tsv with anchor_status != "matched",
emit a TSV row with rich context to help iterate fixes:

unit, note_no, source_scan, source_printed, status, sig_excerpt,
note_body_first_60, gv_digit_candidates, gv_super_candidates,
tess_digit_candidates, tess_weird_marker_candidates, gv_prose_window

Output: build/qa/footnote_unanchored_diagnostics.tsv
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
INV = ROOT / "build/qa/footnote_inventory.tsv"
GV = ROOT / "source/Keightley_1978.txt"
CLEANED = ROOT / "build/ocr/cleaned"
NOTED = ROOT / "build/ocr/cleaned_with_notes"
OUT = ROOT / "build/qa/footnote_unanchored_diagnostics.tsv"

NOTE_BODY_START = re.compile(
    r"^(\d+)\s*[\.,]\s+(\S.+)$",
    re.MULTILINE,
)


def gv_chunk(scan: int) -> str:
    return GV.read_text().split("\f")[scan - 1]


def gv_prose(scan: int) -> str:
    chunk = gv_chunk(scan)
    m = NOTE_BODY_START.search(chunk)
    return chunk[: m.start()] if m else chunk


def note_body(unit: str, note_no: int) -> str:
    """Pull the body of note N from the cleaned_with_notes md for this unit."""
    # We don't have a per-unit map; scan all p_*.md and grep for the sentinel
    for p in sorted(NOTED.glob("p_*.md")):
        text = p.read_text()
        m = re.search(
            rf"<!-- FOOTNOTE:{note_no} -->(.*?)<!-- /FOOTNOTE -->", text, re.DOTALL
        )
        if m and f"unit: {unit}" in text:
            return m.group(1).strip()[:120]
    return ""


def main() -> None:
    rows = list(csv.DictReader(INV.open(), delimiter="\t"))
    unmatched = [r for r in rows if r["anchor_status"] != "matched"]

    out_rows: list[dict] = []
    for r in unmatched:
        scan = int(r["source_scan"])
        note_no = int(r["note_no"])

        gv_p = gv_prose(scan)
        # All loose digit candidates in GV prose (any digit run that could
        # plausibly be a marker, not just ones our regex catches)
        gv_dig = []
        for m in re.finditer(rf"\D({note_no})\D", gv_p):
            s = max(0, m.start() - 20)
            e = min(len(gv_p), m.end() + 15)
            gv_dig.append(gv_p[s:e].replace("\n", "⏎").replace("\t", " "))
        # Superscripts (any) — to find missing-superscript matches
        gv_sup = []
        for m in re.finditer(r"[\u2070-\u2079\u00b9\u00b2\u00b3]+", gv_p):
            s = max(0, m.start() - 20)
            e = min(len(gv_p), m.end() + 10)
            gv_sup.append(gv_p[s:e].replace("\n", "⏎"))

        # Tesseract prose
        tess_path = CLEANED / f"p_{scan:04d}.md"
        tess = tess_path.read_text() if tess_path.exists() else ""
        tess = re.sub(r"<!--.+?-->", "", tess, flags=re.DOTALL)
        tess_dig = []
        for m in re.finditer(rf"\D({note_no})\D", tess):
            s = max(0, m.start() - 20)
            e = min(len(tess), m.end() + 15)
            tess_dig.append(tess[s:e].replace("\n", "⏎"))
        tess_weird = []
        for m in re.finditer(
            r"([a-z\u2019\u201d.,;:\"\)])([\u00ae\u00a9\u00b0\u00b6\u00a7\u201c\u2018\*\u2666\u00b7\u00bb\u00ab])",
            tess,
        ):
            s = max(0, m.start() - 20)
            e = min(len(tess), m.end() + 10)
            tess_weird.append(tess[s:e].replace("\n", "⏎"))

        body = note_body(r["unit"], note_no)

        out_rows.append({
            "unit": r["unit"],
            "note_no": note_no,
            "source_scan": scan,
            "source_printed": r["source_printed"],
            "status": r["anchor_status"],
            "sig_excerpt": r["sig_excerpt"],
            "note_body_head": body,
            "gv_digit_candidates": " | ".join(gv_dig[:5]),
            "gv_super_candidates": " | ".join(gv_sup[:5]),
            "tess_digit_candidates": " | ".join(tess_dig[:5]),
            "tess_weird_markers": " | ".join(tess_weird[:8]),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(out_rows)
    print(f"wrote {len(out_rows)} diagnostic rows → {OUT}")


if __name__ == "__main__":
    main()
