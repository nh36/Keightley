#!/usr/bin/env python3
"""Phase 6: clean Google Vision OCR as the primary prose substrate.

Companion to `scripts/04_clean_ocr.py` (Tesseract → `build/ocr/cleaned/`).
This script reads the supplied Google Vision OCR
(`source/Keightley_1978.txt`, form-feed-delimited, 326 chunks) and writes a
parallel cleaned corpus to `build/ocr/cleaned_gv/`.

Why parallel and not a replacement?  The current Phase 4b iter 5 footnote
work (95% anchored, 35 manual rows) is built on the Tesseract substrate.
We A/B compare both before promoting GV to canonical, so we never risk
the existing footnote work.

Cleanup rules — adapted from 04 to GV's specific artefacts:
  R0  Strip "marginal scanner-junk" lines: a line whose stripped content is
      a single character from {L l I i ] [ ( ) U W M w 1 0 ☐ ¦ │ |}. These
      appear all over GV chunks at top, bottom, and occasionally mid-page.
  R1  Edge-line stripping (top + bottom): low alpha-ratio, very-short lines
      until we hit real body text.
  R2  Running-head removal: ALL-CAPS line / numeric-section heading / bare
      page number on first surviving line.
  R3  Hyphen healing across line breaks (corpus-evidence aware).
  R4  Unicode-whitespace normalisation, trailing-whitespace trim,
      collapse 3+ blank lines to 2.
  R5  Pair-wise '' -> " (rare in GV).
  R6  CJK tagging: GV preserves some CJK (esp. bibliography and tables);
      tag runs as `<!-- CJK -->` so downstream knows where they live.
  R7  Junk-block tagging: short junk-line clusters mid-prose -> CHECK OCR.
  R8  CJK overlay from Tesseract: every CJK run found in
      `build/ocr/pages/p_NNNN.txt` is recorded in a HEADER comment block
      (`<!-- cjk-tess-overlay: ... -->`). Going in the header keeps it
      well clear of the body, so it cannot interfere with footnote splitting
      or anchor-snippet matching.

Outputs:
  build/ocr/cleaned_gv/p_NNNN.md         — one markdown file per scan page
  build/ocr/cleaned_gv_page_aligned.md   — concatenation
  build/logs/ocr_cleanup_rules_gv.md     — rule list + per-rule counters
  build/qa/ocr_cleanup_report_gv.tsv     — per-page diff metrics
"""
from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES_CSV = ROOT / "data" / "pages.csv"
GV_PATH = ROOT / "source" / "Keightley_1978.txt"
TESS_PAGES = ROOT / "build" / "ocr" / "pages"
OUT_DIR = ROOT / "build" / "ocr" / "cleaned_gv"
CONCAT = ROOT / "build" / "ocr" / "cleaned_gv_page_aligned.md"
RULES_LOG = ROOT / "build" / "logs" / "ocr_cleanup_rules_gv.md"
REPORT = ROOT / "build" / "qa" / "ocr_cleanup_report_gv.tsv"

CJK_RE = re.compile(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+")
NBSP_RE = re.compile(r"[\u00a0\u202f\ufeff]")
HYPHEN_BREAK_RE = re.compile(r"([A-Za-z]{2,})-\n([a-z]{2,})")

# R0: single-char garbage (after strip). These occur as scan-edge crud
# in nearly every GV chunk.  CRUCIAL: do NOT include digits here when
# they could legitimately be standalone footnote bodies; '0' alone never
# legitimately appears in this book's body.  '1' alone is rare too.
SINGLE_CHAR_JUNK = set("LlIi][()UWMmw10☐¦│|/\\—–·")

_WORDLIST_PATH = Path("/usr/share/dict/words")
WORDS: set[str] = set()
if _WORDLIST_PATH.exists():
    WORDS = {w.strip().lower() for w in _WORDLIST_PATH.read_text().splitlines() if w.strip()}

COMPOUND_EVIDENCE: set[str] = set()


def build_compound_evidence(pages_text: list[str]) -> None:
    pat = re.compile(r"\b([A-Za-z]{2,})-([A-Za-z]{2,})\b")
    for text in pages_text:
        masked = re.sub(r"-\n", "\n", text)
        for m in pat.finditer(masked):
            COMPOUND_EVIDENCE.add(f"{m.group(1).lower()}-{m.group(2).lower()}")


RUNNING_HEAD_PATTERNS = [
    re.compile(r"^[IVXLC]+\.[IVXLC0-9.]*\s+[A-Z][A-Z \-,'’]{4,}$"),
    re.compile(r"^\d+(?:\.\d+){0,3}\s+[A-Z][A-Z \-,'’]{3,}$"),
    re.compile(r"^[A-Z][A-Z \-,'’]{4,}$"),
    re.compile(r"^\d{1,3}$"),
    re.compile(r"^[A-Z][A-Z]+\s+\d+$"),
]


def alpha_ratio(s: str) -> float:
    if not s:
        return 0.0
    n = sum(1 for c in s if c.isalnum())
    return n / len(s)


def strip_single_char_junk(lines: list[str], counters: Counter) -> list[str]:
    """R0: drop any line whose stripped form is a single junk character."""
    out: list[str] = []
    for ln in lines:
        s = ln.strip()
        if len(s) == 1 and s in SINGLE_CHAR_JUNK:
            counters["R0_single_char_junk_dropped"] += 1
            continue
        out.append(ln)
    return out


def strip_edge_garbage(lines: list[str], counters: Counter) -> tuple[list[str], list[str]]:
    """R1: drop leading lines that are almost certainly scan-edge noise."""
    dropped: list[str] = []
    while lines:
        ln = lines[0].rstrip()
        if not ln.strip():
            dropped.append(ln)
            lines.pop(0)
            continue
        letters = sum(1 for c in ln if c.isalpha())
        if letters >= 20 and alpha_ratio(ln) >= 0.55:
            break
        if alpha_ratio(ln) < 0.30 or letters < 3:
            dropped.append(ln)
            lines.pop(0)
            counters["R1_edge_lines_dropped"] += 1
            continue
        break
    return lines, dropped


def strip_running_head(lines: list[str], counters: Counter) -> tuple[list[str], str | None]:
    """R2: if the first surviving line is a running head / page number, remove it."""
    if not lines:
        return lines, None
    first = lines[0].strip()
    for pat in RUNNING_HEAD_PATTERNS:
        if pat.match(first):
            counters["R2_running_heads_stripped"] += 1
            return lines[1:], first
    return lines, None


def heal_hyphens(text: str, counters: Counter) -> str:
    """R3: glue end-of-line hyphenation."""
    def repl(m: re.Match) -> str:
        a, b = m.group(1), m.group(2)
        start = m.start()
        prev = text[max(0, start - 2):start]
        if re.match(r"[A-Za-z]-$", prev):
            counters["R3_hyphen_breaks_kept_multipart"] += 1
            return f"{a}-{b}"
        compound = f"{a.lower()}-{b.lower()}"
        joined = (a + b).lower()
        if compound in COMPOUND_EVIDENCE:
            counters["R3_hyphen_breaks_kept_compound"] += 1
            return f"{a}-{b}"
        if WORDS and joined in WORDS:
            counters["R3_hyphen_breaks_joined"] += 1
            return a + b
        counters["R3_hyphen_breaks_joined_default"] += 1
        return a + b
    return HYPHEN_BREAK_RE.sub(repl, text)


def normalise_whitespace(text: str, counters: Counter) -> str:
    new, n = NBSP_RE.subn(" ", text)
    counters["R4_unicode_ws_normalised"] += n
    new = "\n".join(ln.rstrip() for ln in new.splitlines())
    new = re.sub(r"\n{3,}", "\n\n", new)
    return new


def normalise_quotes(text: str, counters: Counter) -> str:
    pat = re.compile(r"‘‘([^’\n]{1,80})’’")
    new, n = pat.subn(lambda m: '"' + m.group(1) + '"', text)
    counters["R5_doubled_singles_paired"] += n
    return new


def tag_cjk(text: str, counters: Counter) -> str:
    def repl(m: re.Match) -> str:
        counters["R6_cjk_runs_tagged"] += 1
        return m.group(0) + " <!-- CJK -->"
    return CJK_RE.sub(repl, text)


def tag_junk_blocks(lines: list[str], counters: Counter) -> list[str]:
    out: list[str] = []
    junk_run: list[str] = []

    def flush():
        if junk_run:
            joined = " / ".join(j.strip() for j in junk_run if j.strip())
            counters["R7_junk_blocks_tagged"] += 1
            out.append(f"<!-- CHECK OCR: residue: {joined} -->")
            junk_run.clear()

    for ln in lines:
        s = ln.strip()
        if not s:
            flush()
            out.append(ln)
            continue
        letters = sum(1 for c in s if c.isalpha())
        if letters < 3 and alpha_ratio(s) < 0.30:
            junk_run.append(s)
        else:
            flush()
            out.append(ln)
    flush()
    return out


def extract_tess_cjk(scan: int) -> list[str]:
    """R8 helper: read Tesseract per-page text, return de-duplicated CJK runs."""
    src = TESS_PAGES / f"p_{scan:04d}.txt"
    if not src.exists():
        return []
    raw = src.read_text(errors="replace")
    seen: list[str] = []
    seen_set: set[str] = set()
    for m in CJK_RE.finditer(raw):
        run = m.group(0).strip()
        # Tesseract often produces 1-glyph noise inside Latin text; keep
        # any run that has at least 1 CJK char but normalise inner spaces.
        run = re.sub(r"\s+", " ", run)
        if run and run not in seen_set:
            seen.append(run)
            seen_set.add(run)
    return seen


def clean_page(raw: str, counters: Counter) -> tuple[str, str | None, list[str]]:
    """Return (cleaned_text, removed_running_head_or_None, dropped_top_lines)."""
    raw = normalise_whitespace(raw, counters)
    lines = raw.splitlines()
    # R0 first: scrub single-char junk anywhere.
    lines = strip_single_char_junk(lines, counters)
    lines, dropped = strip_edge_garbage(lines, counters)
    lines, head = strip_running_head(lines, counters)
    # Apply edge stripping a second time to catch a second-line page number
    # exposed by R2 (e.g. "L\n150\n5.7 ..." -> "150\n5.7..." -> "5.7...").
    lines, more_dropped = strip_edge_garbage(lines, counters)
    dropped.extend(more_dropped)
    head2: str | None = None
    if head is None:
        lines, head2 = strip_running_head(lines, counters)
    # Tail edge garbage
    while lines:
        last = lines[-1].strip()
        if not last:
            lines.pop()
            continue
        if alpha_ratio(last) < 0.30 or len(last) < 3:
            counters["R1_edge_lines_dropped"] += 1
            lines.pop()
            continue
        break
    lines = tag_junk_blocks(lines, counters)
    text = "\n".join(lines).strip()
    text = heal_hyphens(text, counters)
    text = normalise_quotes(text, counters)
    text = tag_cjk(text, counters)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text, head or head2, dropped


def main() -> int:
    if not PAGES_CSV.exists():
        sys.exit(f"missing {PAGES_CSV}")
    if not GV_PATH.exists():
        sys.exit(f"missing {GV_PATH}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    RULES_LOG.parent.mkdir(parents=True, exist_ok=True)

    with PAGES_CSV.open() as f:
        meta = list(csv.DictReader(f))

    chunks = GV_PATH.read_text().split("\f")
    if len(chunks) != 326:
        print(f"WARN: expected 326 GV chunks, got {len(chunks)}", file=sys.stderr)

    # Pass 1: build compound evidence from raw GV chunks.
    raw_pages = [chunks[int(r["scan_page"]) - 1] for r in meta
                 if int(r["scan_page"]) - 1 < len(chunks)]
    build_compound_evidence(raw_pages)
    print(f"compound-evidence corpus: {len(COMPOUND_EVIDENCE)} forms")

    grand = Counter()
    report_rows: list[dict] = []
    concat_parts: list[str] = []

    for row in meta:
        scan = int(row["scan_page"])
        printed = row.get("printed_page") or ""
        section = row.get("section") or ""
        idx = scan - 1
        if idx >= len(chunks):
            print(f"  WARN scan {scan} beyond GV chunks", file=sys.stderr)
            continue
        raw = chunks[idx]
        per = Counter()
        cleaned, head, dropped = clean_page(raw, per)
        cjk_overlay = extract_tess_cjk(scan)
        if cjk_overlay:
            per["R8_cjk_overlay_pages"] += 1
            per["R8_cjk_overlay_runs"] += len(cjk_overlay)
        grand.update(per)

        body = (
            f"<!-- source: scan p. {scan:03d}, printed p. {printed or '-'}, "
            f"section: {section or '-'} -->\n"
            f"<!-- substrate: google-vision -->\n"
        )
        if head:
            body += f"<!-- running-head-removed: {head!r} -->\n"
        if dropped:
            body += f"<!-- edge-lines-dropped: {len(dropped)} -->\n"
        if cjk_overlay:
            joined = " ".join(cjk_overlay)
            body += f"<!-- cjk-tess-overlay: {joined} -->\n"
        body += "\n" + cleaned + "\n"

        out_file = OUT_DIR / f"p_{scan:04d}.md"
        out_file.write_text(body)
        concat_parts.append(body)

        report_rows.append({
            "scan_page": scan,
            "printed_page": printed,
            "section": section,
            "raw_chars": len(raw),
            "clean_chars": len(cleaned),
            "edge_dropped": per["R1_edge_lines_dropped"],
            "single_char_junk": per["R0_single_char_junk_dropped"],
            "running_head": 1 if head else 0,
            "hyphens_joined": per["R3_hyphen_breaks_joined"]
                             + per["R3_hyphen_breaks_joined_default"],
            "cjk_runs": per["R6_cjk_runs_tagged"],
            "cjk_overlay_runs": per["R8_cjk_overlay_runs"],
            "junk_blocks": per["R7_junk_blocks_tagged"],
        })

    CONCAT.write_text("\n\n".join(concat_parts))

    with REPORT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(report_rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(report_rows)

    log = ["# OCR cleanup rules applied (Google Vision substrate)", "",
           "Rules defined in `scripts/04b_clean_gv.py`. Per-page detail in",
           "`build/qa/ocr_cleanup_report_gv.tsv`.",
           "", "## Total rule counts across pages", ""]
    for rule, n in sorted(grand.items()):
        log.append(f"- **{rule}**: {n}")
    log += ["", "## Pages with most CJK overlay runs (Tesseract supplement)", ""]
    top_overlay = sorted(report_rows, key=lambda r: -r["cjk_overlay_runs"])[:15]
    for r in top_overlay:
        log.append(f"- scan p. {r['scan_page']:3d}  printed {r['printed_page'] or '-':>4}  "
                   f"section {r['section'] or '-':<25}  cjk_overlay={r['cjk_overlay_runs']}")
    log += ["", "## Pages with most CHECK-OCR junk markers", ""]
    top = sorted(report_rows, key=lambda r: -r["junk_blocks"])[:10]
    for r in top:
        log.append(f"- scan p. {r['scan_page']:3d}  printed {r['printed_page'] or '-':>4}  "
                   f"section {r['section'] or '-':<25}  junk_blocks={r['junk_blocks']}")
    RULES_LOG.write_text("\n".join(log) + "\n")

    print(f"cleaned {len(report_rows)} pages -> {OUT_DIR}")
    print(f"rules log: {RULES_LOG}")
    print(f"report:    {REPORT}")
    print(f"totals:    {dict(grand)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
