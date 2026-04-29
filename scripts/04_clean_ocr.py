#!/usr/bin/env python3
"""Phase 2: OCR cleanup of per-page Tesseract text.

Reads:
  build/ocr/pages/p_NNNN.txt           (Tesseract per-page output)
  data/pages.csv                       (scan↔printed↔section mapping)

Writes:
  build/ocr/cleaned/p_NNNN.md          (one markdown file per scan page)
  build/ocr/cleaned_page_aligned.md    (concatenation, with page-anchor comments)
  build/logs/ocr_cleanup_rules.md      (rule list + per-page application counts)
  build/qa/ocr_cleanup_report.tsv      (per-page diff metrics)

Cleanup rules (all conservative; logged to ocr_cleanup_rules.md):
  R1  Strip leading "edge garbage" lines: lines whose alphanumeric ratio is
      below 0.3 *and* which appear before any line of length >= 25 letters.
      These are the page-rule and CJK gutter artefacts that bleed into the
      top of nearly every scan.
  R2  Detect and remove a running header on the first surviving body line if
      it matches one of: ALL-CAPS short line; section number like "1.2.3 …";
      or is a bare integer (page number). Capture the removed line for QA.
  R3  Heal hyphenated line breaks: "scapu-\\nlimancy" → "scapulimancy" when
      the next line begins with a lowercase letter and the broken word is not
      already a recognised hyphenated form (preserve "Wade-Giles", "pyro-",
      etc. by only joining when the trailing fragment starts with a lowercase
      *letter* immediately after the newline).
  R4  Normalise unicode whitespace: NBSP, narrow NBSP, ZWNBSP → space.
  R5  Curly→straight only for paired double quotes when both ends present
      on the same line. Wade-Giles single apostrophes (curly ’) are kept and
      will be straightened in Phase 6 with proper Pinyin context.
  R6  Tag CJK runs in body text with `<!-- CJK: <chars> -->` markers (the
      glyphs are preserved verbatim — we only annotate so Phase 3 can find
      them).
  R7  Tag obvious Tesseract junk lines mid-paragraph (≥3 consecutive non-word
      characters mixed with very short tokens) with `<!-- CHECK OCR: ... -->`.

Each cleaned file starts with a YAML-style HTML comment block:

    <!-- source: scan p. 020, printed p. 3, section: chapter/1 -->

This is the deliverable specified in brief §5 (page-anchored intermediate).
"""
from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES_CSV = ROOT / "data" / "pages.csv"
OCR_PAGES = ROOT / "build" / "ocr" / "pages"
OUT_DIR = ROOT / "build" / "ocr" / "cleaned"
CONCAT = ROOT / "build" / "ocr" / "cleaned_page_aligned.md"
RULES_LOG = ROOT / "build" / "logs" / "ocr_cleanup_rules.md"
REPORT = ROOT / "build" / "qa" / "ocr_cleanup_report.tsv"

CJK_RE = re.compile(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+")
NBSP_RE = re.compile(r"[\u00a0\u202f\ufeff]")
HYPHEN_BREAK_RE = re.compile(r"([A-Za-z]{2,})-\n([a-z]{2,})")

# Wordlist for hyphen-healing fallback. Only used when corpus evidence
# is inconclusive.
_WORDLIST_PATH = Path("/usr/share/dict/words")
WORDS: set[str] = set()
if _WORDLIST_PATH.exists():
    WORDS = {w.strip().lower() for w in _WORDLIST_PATH.read_text().splitlines() if w.strip()}

# Built from a first pass over the cleaned corpus: lowercase forms of any
# "x-y" compound that appears not at end-of-line. Populated lazily.
COMPOUND_EVIDENCE: set[str] = set()


def build_compound_evidence(pages_text: list[str]) -> None:
    """Record every "foo-bar" form that appears mid-line (not as line-break
    hyphenation)."""
    pat = re.compile(r"\b([A-Za-z]{2,})-([A-Za-z]{2,})\b")
    for text in pages_text:
        # Mask end-of-line hyphens so we don't pick those up
        masked = re.sub(r"-\n", "\n", text)
        for m in pat.finditer(masked):
            COMPOUND_EVIDENCE.add(f"{m.group(1).lower()}-{m.group(2).lower()}")
RUNNING_HEAD_PATTERNS = [
    re.compile(r"^[IVXLC]+\.[IVXLC0-9.]*\s+[A-Z][A-Z \-,'’]{4,}$"),  # "I.I PYRO-SCAPULIMANCY..."
    re.compile(r"^\d+(?:\.\d+){0,3}\s+[A-Z][A-Z \-,'’]{3,}$"),         # "3.7 A PLASTRON SET"
    re.compile(r"^[A-Z][A-Z \-,'’]{4,}$"),                              # "PREFACE", "BIBLIOGRAPHY A"
    re.compile(r"^\d{1,3}$"),                                           # bare page number
    re.compile(r"^[A-Z][A-Z]+\s+\d+$"),                                  # "TABLES 38"
]


def alpha_ratio(s: str) -> float:
    if not s:
        return 0.0
    n = sum(1 for c in s if c.isalnum())
    return n / len(s)


def strip_edge_garbage(lines: list[str], counters: Counter) -> tuple[list[str], list[str]]:
    """R1: drop leading lines that are almost certainly scan-edge noise."""
    dropped: list[str] = []
    while lines:
        ln = lines[0].rstrip()
        if not ln.strip():
            dropped.append(ln)
            lines.pop(0)
            continue
        # If we're already past short-noise band, stop (long lines = body)
        letters = sum(1 for c in ln if c.isalpha())
        if letters >= 20 and alpha_ratio(ln) >= 0.55:
            break
        # Drop only if very junky (low alpha ratio OR all CJK/punct stack)
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
    """R3: glue end-of-line hyphenation.

    Decision tree per "foo-\\nbar":
      0. If "foo" is itself preceded by another hyphenated stem (i.e., the
         word looks like "X-foo-\\nbar"), this is part of a multi-part
         compound such as "mid-thirteenth-century" → keep hyphen.
      1. If "foo-bar" appears as a hyphenated compound elsewhere in the
         corpus → keep hyphen.
      2. Else if "foobar" is in the dictionary → join.
      3. Else → join (default; OCR overhyphenates more often than under).
    """
    def repl(m: re.Match) -> str:
        a, b = m.group(1), m.group(2)
        # Look at the 2 chars preceding the match for "-X" (i.e., this is the
        # tail of a multi-part compound).
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
    """R4: replace odd whitespace."""
    new, n = NBSP_RE.subn(" ", text)
    counters["R4_unicode_ws_normalised"] += n
    # Trim trailing whitespace per line
    new = "\n".join(ln.rstrip() for ln in new.splitlines())
    # Collapse 3+ blank lines to 2
    new = re.sub(r"\n{3,}", "\n\n", new)
    return new


def normalise_quotes(text: str, counters: Counter) -> str:
    """R5: ‘‘…’’ pairs around a single token → "…"."""
    pat = re.compile(r"‘‘([^’\n]{1,80})’’")
    new, n = pat.subn(lambda m: '"' + m.group(1) + '"', text)
    counters["R5_doubled_singles_paired"] += n
    return new


def tag_cjk(text: str, counters: Counter) -> str:
    """R6: append a marker after each CJK run so Phase 3 can audit."""
    def repl(m: re.Match) -> str:
        counters["R6_cjk_runs_tagged"] += 1
        return m.group(0) + " <!-- CJK -->"
    return CJK_RE.sub(repl, text)


def tag_junk_blocks(lines: list[str], counters: Counter) -> list[str]:
    """R7: flag short consecutive junk lines mid-document with CHECK OCR markers."""
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


def clean_page(raw: str, counters: Counter) -> tuple[str, str | None, list[str]]:
    """Return (cleaned_text, removed_running_head_or_None, dropped_top_lines)."""
    raw = normalise_whitespace(raw, counters)
    lines = raw.splitlines()
    lines, dropped = strip_edge_garbage(lines, counters)
    lines, head = strip_running_head(lines, counters)
    # Tail edge garbage too (page numbers/footer noise on last lines)
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
    return text, head, dropped


def main() -> int:
    if not PAGES_CSV.exists():
        sys.exit(f"missing {PAGES_CSV}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    RULES_LOG.parent.mkdir(parents=True, exist_ok=True)

    with PAGES_CSV.open() as f:
        meta = list(csv.DictReader(f))

    # Pass 1: build compound evidence from the raw per-page text.
    raw_pages: list[str] = []
    for row in meta:
        scan = int(row["scan_page"])
        src = OCR_PAGES / f"p_{scan:04d}.txt"
        if src.exists():
            raw_pages.append(src.read_text(errors="replace"))
    build_compound_evidence(raw_pages)
    print(f"compound-evidence corpus: {len(COMPOUND_EVIDENCE)} forms")

    grand = Counter()
    report_rows: list[dict] = []
    concat_parts: list[str] = []

    for row in meta:
        scan = int(row["scan_page"])
        printed = row.get("printed_page") or ""
        section = row.get("section") or ""
        src = OCR_PAGES / f"p_{scan:04d}.txt"
        if not src.exists():
            print(f"  WARN missing {src}", file=sys.stderr)
            continue
        raw = src.read_text(errors="replace")
        per = Counter()
        cleaned, head, dropped = clean_page(raw, per)
        grand.update(per)

        body = (
            f"<!-- source: scan p. {scan:03d}, printed p. {printed or '-'}, "
            f"section: {section or '-'} -->\n"
        )
        if head:
            body += f"<!-- running-head-removed: {head!r} -->\n"
        if dropped:
            body += f"<!-- edge-lines-dropped: {len(dropped)} -->\n"
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
            "running_head": 1 if head else 0,
            "hyphens_joined": per["R3_hyphen_breaks_joined"],
            "cjk_runs": per["R6_cjk_runs_tagged"],
            "junk_blocks": per["R7_junk_blocks_tagged"],
        })

    CONCAT.write_text("\n\n".join(concat_parts))

    # Report
    with REPORT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(report_rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(report_rows)

    # Rules log
    log = ["# OCR cleanup rules applied", "",
           "Rules are defined in `scripts/04_clean_ocr.py`. Each rule is logged",
           "with a counter; per-page detail is in `build/qa/ocr_cleanup_report.tsv`.",
           "", "## Total rule counts across 326 pages", ""]
    for rule, n in sorted(grand.items()):
        log.append(f"- **{rule}**: {n}")
    log += ["",
            "## Pages with the most CHECK-OCR markers (R7)",
            "(top 10 — investigate manually if pursuing further automation)",
            ""]
    top = sorted(report_rows, key=lambda r: -r["junk_blocks"])[:10]
    for r in top:
        log.append(f"- scan p. {r['scan_page']:3d}  printed {r['printed_page'] or '-':>4}  "
                   f"section {r['section'] or '-':<25}  junk_blocks={r['junk_blocks']}")
    log += ["", "## Pages with most CJK runs", ""]
    top_cjk = sorted(report_rows, key=lambda r: -r["cjk_runs"])[:10]
    for r in top_cjk:
        log.append(f"- scan p. {r['scan_page']:3d}  printed {r['printed_page'] or '-':>4}  "
                   f"section {r['section'] or '-':<25}  cjk_runs={r['cjk_runs']}")
    RULES_LOG.write_text("\n".join(log) + "\n")

    print(f"cleaned {len(report_rows)} pages -> {OUT_DIR}")
    print(f"rules log: {RULES_LOG}")
    print(f"report:    {REPORT}")
    print(f"totals:    {dict(grand)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
