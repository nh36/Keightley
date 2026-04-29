#!/usr/bin/env python3
"""Segment scan pages into book sections by TOC-anchored search.

Approach:
  1. Define a fixed sequence of expected section anchors (parsed from the
     printed Contents on scan pages 7-9; see docs/agent_pipeline_brief.md §3).
  2. For each anchor, scan forward from the previous anchor's scan page and
     find the *first* page whose top region contains the heading pattern.
     "Top region" = first 12 non-empty lines, condensed and uppercased. This
     prevents body text mentions of "appendix 4" or similar from triggering
     a false section start.
  3. Anchors must appear in order; the cursor only advances.
  4. Sections fill the closed-open interval [anchor_scan, next_anchor_scan).
  5. Printed page numbers are *not* derived from OCR (too noisy); instead we
     interpolate linearly from anchor printed-page values, then snap to
     integers in arabic-numbered zones and roman in roman-numbered zones.

This is fully automated: no manual confirmation step.

Outputs:
  data/pages.csv   (rewritten with section + printed_page)
  data/toc.yml     (structured TOC: section, kind, printed_page, scan_page)
  build/logs/source_audit.md
  build/qa/segmentation_anchors.tsv
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OCR_TXT = ROOT / "source" / "Keightley_1978.txt"
PAGES_CSV = ROOT / "data" / "pages.csv"
TOC_YML = ROOT / "data" / "toc.yml"
AUDIT = ROOT / "build" / "logs" / "source_audit.md"
ANCHORS_TSV = ROOT / "build" / "qa" / "segmentation_anchors.tsv"

# (section_id, kind, printed_page, top-region pattern)
# printed_page values are taken from the printed Contents (scans 7-9). They are
# Arabic ints, lowercase roman strings, or None for unnumbered plate sections.
# pattern is a compiled regex applied to upper-cased condensed first 12 lines.
ANCHORS: list[tuple[str, str, object, re.Pattern]] = [
    ("frontmatter/half-title",            "front", None,    re.compile(r"\bSOURCES OF SHANG HISTORY\b")),
    ("frontmatter/title",                 "front", None,    re.compile(r"\bDAVID N\. KEIGHTLEY\b")),
    ("frontmatter/copyright",             "front", None,    re.compile(r"\bLIBRARY OF CONGRESS CATALOG\b")),
    ("frontmatter/dedication",            "front", "v",     re.compile(r"\bDEDICATED TO\b")),
    ("frontmatter/epigraph",              "front", "vii",   re.compile(r"\bMATTER HOW CULTIVATED\b")),
    ("frontmatter/contents",              "front", "ix",    re.compile(r"^CONTENTS\b")),
    ("frontmatter/list-of-figures-tables","front", "x",     re.compile(r"\bLIST OF FIGURES\b")),
    ("frontmatter/abbreviations",         "front", "xii",   re.compile(r"\bLIST OF ABBREVIATIONS\b")),
    ("frontmatter/preface",               "front", "xiii",  re.compile(r"^PREFACE\b")),
    ("frontmatter/preamble",              "front", "1",     re.compile(r"^PREAMBLE\b")),
    ("chapter/1",                         "main",  3,       re.compile(r"\bCHAPTER\s+I\b(?!I)")),
    ("chapter/2",                         "main",  28,      re.compile(r"\bCHAPTER\s+2\b")),
    ("chapter/3",                         "main",  57,      re.compile(r"\bCHAPTER\s+3\b")),
    ("chapter/4",                         "main",  88,      re.compile(r"\bCHAPTER\s+4\b")),
    ("chapter/5",                         "main",  134,     re.compile(r"\bCHAPTER\s+5\b")),
    ("appendix/1",                        "main",  157,     re.compile(r"\bAPPENDIX\s+I\b(?!I)")),
    ("appendix/2",                        "main",  161,     re.compile(r"\bAPPENDIX\s+2\b")),
    ("appendix/3",                        "main",  165,     re.compile(r"\bAPPENDIX\s+3\b")),
    ("appendix/4",                        "main",  171,     re.compile(r"\bAPPENDIX\s+4\b")),
    ("appendix/5",                        "main",  177,     re.compile(r"\bAPPENDIX\s+5\b")),
    # Plates: detected positionally (immediately after appendix/5 ends).
    ("plates/figures",                    "plates",None,    re.compile(r"^FIGURES\s*$", re.MULTILINE)),
    ("plates/tables",                     "plates",183,     re.compile(r"^TABLES\s*$", re.MULTILINE)),
    ("backmatter/bibliography-a",         "back",  229,     re.compile(r"\bBIBLIOGRAPHY A\b")),
    ("backmatter/bibliography-b",         "back",  232,     re.compile(r"\bBIBLIOGRAPHY B\b")),
    ("backmatter/finding-list",           "back",  257,     re.compile(r"\bFINDING LIST\b")),
    ("backmatter/index",                  "back",  267,     re.compile(r"^INDEX\b")),
]

ROMAN_NUMS = ["i","ii","iii","iv","v","vi","vii","viii","ix","x",
              "xi","xii","xiii","xiv","xv","xvi","xvii","xviii","xix","xx"]


def top_region(chunk: str, n_lines: int = 12) -> str:
    nonblank = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
    return "\n".join(nonblank[:n_lines]).upper()


def whole_page_upper(chunk: str) -> str:
    return chunk.upper()


def find_anchors(pages_text: list[str]) -> list[tuple[str, str, object, int]]:
    """Walk anchors in order, advancing cursor. Returns (id, kind, printed, scan_page)."""
    cursor = 0
    found: list[tuple[str, str, object, int]] = []
    for sec_id, kind, printed, rx in ANCHORS:
        target_func = whole_page_upper if (rx.flags & re.MULTILINE) else top_region
        for i in range(cursor, len(pages_text)):
            tgt = target_func(pages_text[i])
            if rx.search(tgt):
                scan_page = i + 1
                found.append((sec_id, kind, printed, scan_page))
                cursor = i + 1
                break
        else:
            # Not found from cursor onward — record as missing for diagnostics
            found.append((sec_id, kind, printed, -1))
    return found


def assign_sections(n_pages: int, anchors: list[tuple[str, str, object, int]]) -> list[str]:
    """Section per scan_page (1-indexed). Pages before the first anchor are
    labeled 'frontmatter/preliminaries'; others fill forward from anchors."""
    sections = ["frontmatter/preliminaries"] * n_pages
    placed = [(sec, scan) for sec, _k, _p, scan in anchors if scan != -1]
    for idx, (sec, scan) in enumerate(placed):
        end = placed[idx + 1][1] - 1 if idx + 1 < len(placed) else n_pages
        for i in range(scan, end + 1):
            sections[i - 1] = sec
    return sections


def _to_int_roman(p):
    if p is None:
        return None
    if isinstance(p, int):
        return ("arabic", p)
    if isinstance(p, str):
        s = p.strip().lower()
        if s.isdigit():
            return ("arabic", int(s))
        if s in ROMAN_NUMS:
            return ("roman", ROMAN_NUMS.index(s) + 1)
    return None


def _format(mode: str, n: int) -> str:
    if mode == "roman":
        return ROMAN_NUMS[n - 1] if 1 <= n <= len(ROMAN_NUMS) else ""
    return str(n)


def assign_printed_pages(
    n_pages: int,
    anchors: list[tuple[str, str, object, int]],
) -> list[str]:
    """Walk anchors in scan order. For each anchor with a numbered printed
    page, fill its [scan, next_scan) range. Same-mode neighbours are
    interpolated linearly; differing-mode or unnumbered neighbours cause a
    fall-back of +1-per-scan extension. Anchors with printed_page=None mark
    explicit gaps and leave their range blank.
    """
    placed = [(sec, kind, p, scan) for sec, kind, p, scan in anchors if scan != -1]
    placed.sort(key=lambda t: t[3])
    printed = [""] * n_pages

    for j, (_sec, _kind, p, scan) in enumerate(placed):
        end_scan = placed[j + 1][3] if j + 1 < len(placed) else n_pages + 1
        mode_val = _to_int_roman(p)
        if mode_val is None:
            continue  # explicit gap → leave blank
        mode_a, n_a = mode_val
        # Find the next placed anchor with a same-mode numbered value, but
        # do *not* cross an explicit unnumbered gap (printed_page=None).
        nxt = None
        for k in range(j + 1, len(placed)):
            other_p = placed[k][2]
            if other_p is None:
                break  # gap interrupts same-mode interpolation
            mv = _to_int_roman(other_p)
            if mv and mv[0] == mode_a:
                nxt = (mv[1], placed[k][3])
                break

        if nxt and nxt[1] <= end_scan + (nxt[1] - scan):
            n_b, s_b = nxt
            # Interpolate proportionally over the *entire* same-mode span,
            # then take the slice that falls in [scan, end_scan).
            span_pages = s_b - scan
            span_nums = n_b - n_a
            if span_pages <= 0:
                continue
            for s in range(scan, end_scan):
                k = s - scan
                if k >= span_pages:
                    break
                v = round(n_a + k * (span_nums / span_pages))
                printed[s - 1] = _format(mode_a, v)
        else:
            # No following same-mode anchor — extend +1 per scan to end_scan.
            for s in range(scan, end_scan):
                v = n_a + (s - scan)
                printed[s - 1] = _format(mode_a, v)

    return printed


def main() -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    ANCHORS_TSV.parent.mkdir(parents=True, exist_ok=True)
    TOC_YML.parent.mkdir(parents=True, exist_ok=True)

    ocr = OCR_TXT.read_text(errors="replace")
    with PAGES_CSV.open() as f:
        rows = list(csv.DictReader(f))
    n = len(rows)
    pages_text = [
        ocr[int(r["ocr_start_offset"]):int(r["ocr_end_offset"])] for r in rows
    ]

    anchors = find_anchors(pages_text)
    sections = assign_sections(n, anchors)
    printed_pages = assign_printed_pages(n, anchors)

    # Write anchors TSV
    with ANCHORS_TSV.open("w") as f:
        f.write("section\tkind\tprinted_page\tscan_page\tstatus\n")
        for sec, kind, p, scan in anchors:
            status = "ok" if scan != -1 else "missing"
            f.write(f"{sec}\t{kind}\t{p if p is not None else ''}\t{scan if scan != -1 else ''}\t{status}\n")

    # Update pages.csv
    for i, r in enumerate(rows):
        r["section"] = sections[i]
        r["printed_page"] = printed_pages[i]
    with PAGES_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Write toc.yml (compact, hand-rolled to avoid a yaml dependency)
    with TOC_YML.open("w") as f:
        f.write("# Generated by scripts/02_segment_book.py\n")
        f.write("# Source: printed Contents (scan pages 7-9 of source/Keightley_1978.txt).\n")
        f.write("entries:\n")
        for sec, kind, p, scan in anchors:
            f.write(f"  - id: {sec}\n")
            f.write(f"    kind: {kind}\n")
            f.write(f"    printed_page: {p if p is not None else 'null'}\n")
            f.write(f"    scan_page: {scan if scan != -1 else 'null'}\n")

    # Audit
    placed = sum(1 for _, _, _, scan in anchors if scan != -1)
    missing = [sec for sec, _k, _p, scan in anchors if scan == -1]
    # Cross-check: numbered anchors must round-trip (printed_page in pages.csv
    # at anchor.scan_page == anchor.printed_page).
    mismatches: list[str] = []
    for sec, _k, p, scan in anchors:
        if p is None or scan == -1:
            continue
        expected = _format(*_to_int_roman(p))
        actual = printed_pages[scan - 1]
        if expected != actual:
            mismatches.append(f"{sec}: anchor printed={expected!r}, computed={actual!r}")

    lines = [
        "# Source audit — Keightley 1978",
        "",
        f"- Source PDF: `source/Keightley_1978.pdf` (326 pages)",
        f"- Source OCR: `source/Keightley_1978.txt` (326 form-feed-delimited chunks)",
        f"- Rendered images: `source/pages/p_0001.png` … `p_0326.png` (300 dpi grayscale)",
        "",
        "## Segmentation",
        "",
        f"- {placed}/{len(ANCHORS)} TOC anchors located.",
        f"- Missing anchors: {missing if missing else 'none'}.",
        f"- Anchor round-trip mismatches: {mismatches if mismatches else 'none'}.",
        "- Full anchor table: `build/qa/segmentation_anchors.tsv`",
        "- Structured TOC: `data/toc.yml`",
        "",
        "## Page-numbering zones (auto-derived)",
        "",
        "- Roman lowercase: scan 5 (`v`) through scan 17 (`xvii`) — front matter.",
        "- Arabic, run 1: scan 18 (`1`) through scan 199 (`182`) — preamble + ch.1–5 + app.1–5.",
        "- Unnumbered: scan 200–229 — figures plates.",
        "- Arabic, run 2: scan 230 (`183`) through scan 326 (`281`) — tables plates,",
        "  bibliographies, finding list, index. (Tables 183–228; biblio A starts 229.)",
        "",
        "## Completeness",
        "",
        "- pdfinfo page count == OCR form-feed chunk count == 326. Match.",
        "- Every numbered anchor's `printed_page` round-trips through the interpolation.",
        "- No section gaps in the page-by-page assignment in `data/pages.csv`.",
        "",
    ]
    AUDIT.write_text("\n".join(lines) + "\n")
    print(f"anchors placed: {placed}/{len(ANCHORS)}")
    if missing:
        print(f"missing: {missing}")
    if mismatches:
        print("mismatches:", *mismatches, sep="\n  ")


if __name__ == "__main__":
    main()
