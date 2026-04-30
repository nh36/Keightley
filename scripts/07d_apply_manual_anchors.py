#!/usr/bin/env python3
"""Apply manual footnote anchor placements to cleaned_with_notes/*.md.

Reads data/manual_footnote_anchors.tsv (scan, note_no, anchor_snippet)
and, for each row, finds the matching <!-- FOOTNOTE-UNANCHORED:N --> body
in the corresponding page md, removes it from the tail, and inserts an
inline <!-- FOOTNOTE:N -->...<!-- /FOOTNOTE --> sentinel immediately
after the first occurrence of anchor_snippet in the prose substrate.

Idempotent: running twice produces the same result (snippet match is
done against the prose with sentinels stripped, so re-running on
already-converted output won't re-trigger).
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANCHORS = ROOT / "data" / "manual_footnote_anchors.tsv"
CWN = ROOT / "build" / "ocr" / "cleaned_with_notes"

UNANCH_RE_TPL = r"<!-- FOOTNOTE-UNANCHORED:{n} -->(.*?)<!-- /FOOTNOTE -->"
SENT_RE = re.compile(r"<!-- /?FOOTNOTE(?:-UNANCHORED)?:?\d* ?-->")


def strip_sentinels(text: str) -> str:
    # Remove FOOTNOTE bodies entirely (tag-pair-bracketed) and stray tags
    text = re.sub(r"<!-- FOOTNOTE:\d+ -->.*?<!-- /FOOTNOTE -->", "", text, flags=re.DOTALL)
    text = re.sub(r"<!-- FOOTNOTE-UNANCHORED:\d+ -->.*?<!-- /FOOTNOTE -->", "", text, flags=re.DOTALL)
    return text


def apply_anchor(md_text: str, note_no: int, snippet: str) -> tuple[str, str]:
    """Returns (new_md, status)."""
    unre = re.compile(UNANCH_RE_TPL.format(n=note_no), re.DOTALL)
    m = unre.search(md_text)
    if not m:
        # Maybe already anchored — confirm
        if re.search(rf"<!-- FOOTNOTE:{note_no} -->", md_text):
            return md_text, "already-anchored"
        return md_text, "no-unanchored-body-found"
    body = m.group(1)

    # Strip sentinels from prose to do snippet match cleanly
    stripped = strip_sentinels(md_text)
    # Normalize whitespace for matching: collapse runs of whitespace
    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    needle = norm(snippet)
    haystack_norm = norm(stripped)
    if needle not in haystack_norm:
        return md_text, f"snippet-not-found: {snippet[:50]!r}"

    # Now find snippet in the original (un-normalized) md_text.  We try
    # tolerant whitespace matching by building a regex from the snippet.
    pattern = re.escape(snippet.strip())
    # Replace escaped whitespace with \s+
    pattern = re.sub(r"(\\\s|\\ )+", r"\\s+", pattern)
    # Also normalize plain spaces in original snippet
    pattern = re.sub(r" +", r"\\s+", pattern)
    m2 = re.search(pattern, md_text)
    if not m2:
        return md_text, f"snippet-regex-failed: {snippet[:50]!r}"

    insert_pos = m2.end()
    sentinel = f"<!-- FOOTNOTE:{note_no} -->{body}<!-- /FOOTNOTE -->"

    # Remove the unanchored block from the tail
    new_md = md_text[: m.start()] + md_text[m.end():]
    # Account for shifted insert_pos if unanchored block was BEFORE insert_pos
    # (it shouldn't be, since unanchored bodies are appended to end, but be safe)
    if m.start() < insert_pos:
        insert_pos -= (m.end() - m.start())
    new_md = new_md[:insert_pos] + sentinel + new_md[insert_pos:]
    return new_md, "anchored"


def main() -> int:
    rows: list[tuple[int, int, str]] = []
    with ANCHORS.open() as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                print(f"BAD ROW (need 3 tab-separated fields): {line!r}", file=sys.stderr)
                continue
            scan, note_no, snippet = parts[0], parts[1], "\t".join(parts[2:])
            # Interpret backslash-n as a newline (allows TSV-friendly literal escapes)
            snippet = snippet.replace("\\n", "\n").replace("\\t", "\t")
            rows.append((int(scan), int(note_no), snippet))

    counts = {"anchored": 0, "already-anchored": 0, "skipped": 0}
    by_scan: dict[int, list[tuple[int, str]]] = {}
    for scan, note_no, snippet in rows:
        by_scan.setdefault(scan, []).append((note_no, snippet))

    for scan, items in by_scan.items():
        path = CWN / f"p_{scan:04d}.md"
        if not path.exists():
            print(f"scan {scan}: md missing")
            counts["skipped"] += len(items)
            continue
        text = path.read_text()
        for note_no, snippet in items:
            new_text, status = apply_anchor(text, note_no, snippet)
            if status == "anchored":
                counts["anchored"] += 1
                text = new_text
            elif status == "already-anchored":
                counts["already-anchored"] += 1
            else:
                print(f"scan {scan} note {note_no}: {status}")
                counts["skipped"] += 1
        path.write_text(text)

    print(f"Total: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
