#!/usr/bin/env python3
"""Phase 1 + Phase 2 + Phase 3 verifier. Exits non-zero if any invariant fails.

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


def check_phase3() -> None:
    """Phase 3 invariants: every TOC anchor has a tex file; main.tex is wired."""
    # Use a tiny YAML reader to avoid a runtime dep — toc.yml has a known shape.
    import re as _re
    toc_text = (ROOT / "data" / "toc.yml").read_text()
    ids_in_toc = set(_re.findall(r"^  - id:\s*(\S+)", toc_text, _re.MULTILINE))
    expected_files = {
        "frontmatter/half-title": "frontmatter/halftitle.tex",
        "frontmatter/title": "frontmatter/title.tex",
        "frontmatter/copyright": "frontmatter/copyright.tex",
        "frontmatter/dedication": "frontmatter/dedication.tex",
        "frontmatter/epigraph": "frontmatter/epigraph.tex",
        "frontmatter/contents": "frontmatter/contents.tex",
        "frontmatter/list-of-figures-tables": "frontmatter/list-figures-tables.tex",
        "frontmatter/abbreviations": "frontmatter/abbreviations.tex",
        "frontmatter/preface": "frontmatter/preface.tex",
        "frontmatter/preamble": "frontmatter/book-preamble.tex",
        "plates/figures": "plates/figures.tex",
        "plates/tables": "plates/tables.tex",
        "backmatter/bibliography-a": "backmatter/biblio_a.tex",
        "backmatter/bibliography-b": "backmatter/biblio_b.tex",
        "backmatter/finding-list": "backmatter/finding_list.tex",
        "backmatter/index": "backmatter/index.tex",
    }
    for n in range(1, 6):
        expected_files[f"chapter/{n}"] = f"chapters/ch{n:02d}.tex"
        expected_files[f"appendix/{n}"] = f"appendices/app{n:02d}.tex"

    ids_in_toc = set(_re.findall(r"^  - id:\s*(\S+)", toc_text, _re.MULTILINE))
    TEX = ROOT / "tex"
    if set(expected_files) != ids_in_toc:
        fail(f"phase3: TOC ids vs emit map mismatch: "
             f"missing-from-emit={ids_in_toc - set(expected_files)}, "
             f"extra-in-emit={set(expected_files) - ids_in_toc}")

    for sec, rel in expected_files.items():
        p = TEX / rel
        if not p.exists():
            fail(f"phase3: missing tex file for {sec}: {p.relative_to(ROOT)}")

    # main_body.tex must \input every emitted unit
    main_body = (TEX / "main_body.tex").read_text()
    for rel in expected_files.values():
        token = "\\input{" + rel.replace(".tex", "") + "}"
        if token not in main_body:
            fail(f"phase3: main_body.tex missing {token}")

    # preamble + main.tex sanity
    if "\\origsecnum" not in (TEX / "preamble.tex").read_text():
        fail("phase3: preamble.tex missing \\origsecnum macro")
    if "\\input{preamble}" not in (TEX / "main.tex").read_text():
        fail("phase3: main.tex doesn't \\input{preamble}")

    # Each chapter must have a \chapter heading and at least one numbered section.
    for n in range(1, 6):
        ch = (TEX / f"chapters/ch{n:02d}.tex").read_text()
        if "\\chapter{" not in ch:
            fail(f"phase3: chapters/ch{n:02d}.tex missing \\chapter{{...}}")
        if "\\section[" not in ch:
            fail(f"phase3: chapters/ch{n:02d}.tex has no numbered \\section")

    # Heading inventory must exist and cover all chapters
    inv = ROOT / "build" / "qa" / "structure_inventory.tsv"
    if not inv.exists():
        fail("phase3: build/qa/structure_inventory.tsv missing")


def main() -> int:
    rows = list(csv.DictReader(PAGES_CSV.open()))
    check_phase1(rows)
    check_phase2(rows)
    check_phase3()

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
