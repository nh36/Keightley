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
import os
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANCHORS = ROOT / "data" / "manual_footnote_anchors.tsv"
CWN = ROOT / "build" / "ocr" / os.environ.get("OUT_DIR", "cleaned_with_notes")

UNANCH_RE_TPL = r"<!-- FOOTNOTE-UNANCHORED:{n} -->(.*?)<!-- /FOOTNOTE -->"
SENT_RE = re.compile(r"<!-- /?FOOTNOTE(?:-UNANCHORED)?:?\d* ?-->")


def strip_sentinels(text: str) -> str:
    # Remove FOOTNOTE bodies entirely (tag-pair-bracketed) and stray tags
    text = re.sub(r"<!-- FOOTNOTE:\d+ -->.*?<!-- /FOOTNOTE -->", "", text, flags=re.DOTALL)
    text = re.sub(r"<!-- FOOTNOTE-UNANCHORED:\d+ -->.*?<!-- /FOOTNOTE -->", "", text, flags=re.DOTALL)
    return text


def fuzzy_find(needle: str, haystack: str, threshold: float = 0.70) -> tuple[int, int, float] | None:
    """Sliding-window fuzzy match. Returns (start, end, ratio) of best match in haystack
    if ratio >= threshold, else None. Window length = len(needle); step = ~1/4 needle len."""
    n = len(needle)
    if n < 5 or len(haystack) < n:
        return None
    step = max(1, n // 6)
    best = (-1, -1, 0.0)
    sm = SequenceMatcher(None, needle, "")
    for i in range(0, len(haystack) - n + 1, step):
        window = haystack[i:i + n]
        sm.set_seq2(window)
        r = sm.ratio()
        if r > best[2]:
            best = (i, i + n, r)
            if r >= 0.97:
                break
    if best[2] < threshold:
        return None
    # Refine with a smaller step around best position
    s0 = max(0, best[0] - step)
    s1 = min(len(haystack) - n, best[0] + step)
    for i in range(s0, s1 + 1):
        window = haystack[i:i + n]
        sm.set_seq2(window)
        r = sm.ratio()
        if r > best[2]:
            best = (i, i + n, r)
    return best


def apply_anchor(md_text: str, note_no: int, snippet: str) -> tuple[str, str]:
    """Returns (new_md, status). Phase 6: Added validation to reject implausible fuzzy
    matches (e.g., no marker nearby after fuzzy matching)."""
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

    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    needle = norm(snippet)
    haystack_norm = norm(stripped)

    matched_text: str | None = None
    fuzzy_used = False

    if needle in haystack_norm:
        # Match in original (un-normalized) md_text via tolerant whitespace regex.
        pattern = re.escape(snippet.strip())
        pattern = re.sub(r"(\\\s|\\ )+", r"\\s+", pattern)
        pattern = re.sub(r" +", r"\\s+", pattern)
        m2 = re.search(pattern, md_text)
        if m2:
            insert_pos = m2.end()
        else:
            return md_text, f"snippet-regex-failed: {snippet[:50]!r}"
    else:
        # Fuzzy fallback: search in `stripped` for a window most similar to `snippet`.
        # Phase 6: Increased threshold from 0.70 to 0.80 to reduce false matches.
        hit = fuzzy_find(snippet.strip(), stripped, threshold=0.80)
        if hit is None:
            # Try with normalized (collapsed-whitespace) variants
            hit2 = fuzzy_find(needle, haystack_norm, threshold=0.85)
            if hit2 is None:
                return md_text, f"snippet-not-found: {snippet[:50]!r}"
            # Translate haystack_norm position back to stripped
            return md_text, f"snippet-not-found-fuzzy-norm: {snippet[:50]!r} (best={hit2[2]:.2f})"
        s, e, ratio = hit
        matched_text = stripped[s:e]
        fuzzy_used = True
        
        # Phase 6: Validation — after fuzzy matching, check if there's a plausible
        # marker (superscript, *, #, or digit) within 150 chars BEFORE the match.
        # If not, reject this as a likely false positive — UNLESS the match ratio is
        # very high (>=0.90), indicating manual anchor precision.
        before_match = stripped[max(0, s-150):s]
        has_marker = bool(re.search(r'[⁰¹²³⁴⁵⁶⁷⁸⁹\*\#]|\b' + str(note_no) + r'\b', before_match))
        if not has_marker and len(before_match) > 30 and ratio < 0.90:
            # No marker found AND low confidence; likely a false positive. Reject.
            return md_text, f"fuzzy-rejected-no-marker: {snippet[:50]!r} (ratio={ratio:.2f})"
        
        # Now search for `matched_text` in `md_text`.
        idx = md_text.find(matched_text)
        if idx < 0:
            # Fall back: search for the last 24 chars (a unique tail signature).
            tail = matched_text[-24:].strip()
            tail_idx = md_text.find(tail)
            if tail_idx < 0:
                return md_text, f"snippet-fuzzy-found-but-untranslatable: {snippet[:40]!r}"
            insert_pos = tail_idx + len(tail)
        else:
            insert_pos = idx + len(matched_text)

    sentinel = f"<!-- FOOTNOTE:{note_no} -->{body}<!-- /FOOTNOTE -->"

    # Remove the unanchored block from the tail
    new_md = md_text[: m.start()] + md_text[m.end():]
    if m.start() < insert_pos:
        insert_pos -= (m.end() - m.start())
    new_md = new_md[:insert_pos] + sentinel + new_md[insert_pos:]
    return new_md, ("anchored-fuzzy" if fuzzy_used else "anchored")


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

    counts = {"anchored": 0, "anchored-fuzzy": 0, "already-anchored": 0, "skipped": 0}
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
            elif status == "anchored-fuzzy":
                counts["anchored-fuzzy"] += 1
                text = new_text
                print(f"scan {scan} note {note_no}: anchored-fuzzy")
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
