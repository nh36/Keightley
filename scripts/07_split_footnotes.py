#!/usr/bin/env python3
"""Phase 4: footnote splitting.

For each chapter / appendix unit:

  1. Walk the Tesseract-cleaned pages of the unit (build/ocr/cleaned/p_NNNN.md).
     Split each page into PROSE (top) and NOTES-BLOCK (tail run of paragraphs
     each starting with `^\\d+[.,]\\s+[A-Z…]` whose numbers monotonically rise
     and continue the chapter's note sequence).

  2. Extract note bodies from each page tail. Concatenate per-unit into a dict
     {note_no -> {body, source_scan, source_printed}}.

  3. For each page, locate inline note markers in the **Google Vision** OCR
     of that scan (form-feed chunk N-1). GV is much better than Tesseract at
     preserving numeric superscripts. Filter candidate markers to those whose
     literal digit value equals one of the page's expected note numbers, in
     order of position.

  4. For each filtered GV marker, derive a 24-char ASCII signature from the
     preceding text and fuzzy-locate that signature in the Tesseract prose
     of the same page. If found, insert a sentinel
       <!-- FOOTNOTE:N -->BODY<!-- /FOOTNOTE -->
     at that position. If not found, append the note as
       <!-- FOOTNOTE-UNANCHORED:N -->BODY<!-- /FOOTNOTE -->
     at end of the page prose.

  5. Write the augmented page to build/ocr/cleaned_with_notes/p_NNNN.md.

After this script, scripts/06_emit_structure.py is run with
`--with-notes`, which converts the sentinels into LaTeX `\\footnote{...}` /
`\\footnotetext[N]{...}` calls.

Outputs:
  build/ocr/cleaned_with_notes/p_NNNN.md   (page-anchored, with sentinels)
  build/qa/footnote_inventory.tsv          (one row per detected note)
  build/logs/phase4_footnotes.md           (per-chapter / per-unit summary)
"""
from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES_CSV = ROOT / "data" / "pages.csv"
CLEAN_DIR = ROOT / "build" / "ocr" / "cleaned"
OUT_DIR = ROOT / "build" / "ocr" / "cleaned_with_notes"
GV_PATH = ROOT / "source" / "Keightley_1978.txt"
INVENTORY = ROOT / "build" / "qa" / "footnote_inventory.tsv"
LOG = ROOT / "build" / "logs" / "phase4_footnotes.md"


NOTE_BODY_START = re.compile(r"^(\d+)[\.,]\s+([\u201C\u201D\"A-Z][^\n]*)$", re.MULTILINE)
HEADING_NUM_RE = re.compile(r"^\d+\.\d+\s+[A-Z]", re.MULTILINE)
SOURCE_HDR_RE = re.compile(r"<!--\s*source:.+?-->", re.DOTALL)
COMMENT_RE = re.compile(r"<!--.+?-->", re.DOTALL)
WS_RE = re.compile(r"\s+")

# Units that have notes (chapters, appendices, preface, preamble).
# Restart-counts of note numbering: each chapter / each appendix / preface /
# preamble starts notes at 1 independently.
UNITS = (
    [("frontmatter/preface", "preface")] +
    [("frontmatter/preamble", "preamble")] +
    [(f"chapter/{n}", f"ch{n}") for n in range(1, 6)] +
    [(f"appendix/{n}", f"app{n}") for n in range(1, 6)]
)


def parse_page_md(md: str) -> tuple[str, str]:
    """Return (header_block, body) — header = leading <!-- ... --> chunk."""
    pos = 0
    while True:
        m = re.match(r"<!--.+?-->\s*", md[pos:], re.DOTALL)
        if not m:
            break
        pos += m.end()
    return md[:pos], md[pos:]


def split_prose_and_notes(body: str, prev_max: int) -> tuple[str, list[tuple[int, str]], list[str]]:
    """Find note bodies at the page tail.

    A note body must start with `^N[.,]\\s+[A-Z…]` and N must continue the
    sequence (>= prev_max+1, or be a contiguous run starting somewhere >=1).

    Returns (prose, notes, warnings) where notes = [(note_no, body_text), ...]
    in order, and prose is everything above the first accepted note start.
    """
    warns: list[str] = []
    candidates = list(NOTE_BODY_START.finditer(body))
    if not candidates:
        return body, [], warns

    # Walk candidates from BOTTOM up: include them as long as the numbers form
    # a strictly-decreasing sequence of >0 integers in continued range.
    # Equivalently, find the longest tail-suffix where note numbers are
    # strictly increasing as we go down the page AND the first candidate's
    # number is >= prev_max+1 (allowing some slack of -1 for OCR mishaps).
    chosen: list[re.Match] = []
    last_n = -1
    for m in candidates:
        n = int(m.group(1))
        # Tentatively accept this candidate.
        if not chosen:
            # Anchor: must be a plausible continuation of the chapter sequence.
            if not (prev_max < n <= prev_max + 50):
                continue
            chosen = [m]
            last_n = n
            continue
        if n == last_n + 1:
            chosen.append(m)
            last_n = n
        elif n <= last_n:
            # Probably not a note (e.g. "23." inside a note body)
            continue
        else:
            # Gap. Could be missed OCR. Allow up to +5 gap; record warning.
            if n <= last_n + 5:
                warns.append(f"note-gap: {last_n} -> {n}")
                chosen.append(m)
                last_n = n
            # else: probably a different paragraph numbering scheme; stop.
            else:
                break

    if not chosen:
        return body, [], warns

    # Notes block starts at the first chosen match.
    notes_start = chosen[0].start()
    prose = body[:notes_start]

    # Slice each note body: from match.start() to next match.start() (or EOF).
    notes: list[tuple[int, str]] = []
    for i, m in enumerate(chosen):
        end = chosen[i + 1].start() if i + 1 < len(chosen) else len(body)
        # Strip the leading "N. " prefix.
        prefix_re = re.match(r"^\d+[\.,]\s+", body[m.start():end])
        text_start = m.start() + (prefix_re.end() if prefix_re else 0)
        note_text = body[text_start:end].strip()
        notes.append((int(m.group(1)), note_text))

    return prose, notes, warns


def gv_chunk_for_scan(scan: int) -> str:
    chunks = GV_PATH.read_text().split("\f")
    if scan - 1 >= len(chunks):
        return ""
    return chunks[scan - 1]


# Cache GV chunks for all 326 pages once.
_GV_CHUNKS: list[str] | None = None
def all_gv_chunks() -> list[str]:
    global _GV_CHUNKS
    if _GV_CHUNKS is None:
        _GV_CHUNKS = GV_PATH.read_text().split("\f")
    return _GV_CHUNKS


# Marker regex in GV: digit(s) attached to or following a word boundary,
# then space/comma/period/quote/EOL. We capture markers of value 1-300.
GV_MARKER_RE = re.compile(
    r"(?<=[a-z\)\u2019\u201d\.,;:])\s?(\d{1,3})(?=[\s,.\u201c\u201d\"\(\)\u2014\u2013\-—–\?!])"
)
# Also catch unicode superscript digits.
SUPERSCRIPT = {
    "\u2070": "0", "\u00b9": "1", "\u00b2": "2", "\u00b3": "3",
    "\u2074": "4", "\u2075": "5", "\u2076": "6", "\u2077": "7",
    "\u2078": "8", "\u2079": "9",
}
SUPER_MARKER_RE = re.compile(r"(?<=[a-z\)\u2019\u201d])([\u2070-\u2079\u00b9\u00b2\u00b3]+)")


def find_gv_markers(gv_prose: str, expected: set[int]) -> list[tuple[int, int]]:
    """Return [(note_no, char_pos_in_gv_prose), ...] in order."""
    found: list[tuple[int, int]] = []
    for m in GV_MARKER_RE.finditer(gv_prose):
        try:
            n = int(m.group(1))
        except ValueError:
            continue
        if n in expected:
            found.append((n, m.end()))
    for m in SUPER_MARKER_RE.finditer(gv_prose):
        digits = "".join(SUPERSCRIPT.get(c, "") for c in m.group(1))
        if not digits:
            continue
        try:
            n = int(digits)
        except ValueError:
            continue
        if n in expected:
            found.append((n, m.end()))
    found.sort(key=lambda x: x[1])

    # Filter: keep only an in-order, non-decreasing-by-position run that
    # matches the expected order (sorted ascending).
    expected_order = sorted(expected)
    result: list[tuple[int, int]] = []
    cursor = 0
    for n, pos in found:
        # Skip until we hit the next expected note.
        while cursor < len(expected_order) and expected_order[cursor] != n:
            if n > expected_order[cursor]:
                cursor += 1
            else:
                break
        if cursor >= len(expected_order):
            break
        if expected_order[cursor] == n:
            # Don't double-match same note.
            if result and result[-1][0] == n:
                continue
            result.append((n, pos))
            cursor += 1
    return result


def signature(text: str, end_pos: int, n: int = 32) -> str:
    """ASCII-letter signature of length ~n from text[end_pos-n*2:end_pos]."""
    seg = text[max(0, end_pos - n * 3): end_pos]
    s = re.sub(r"[^a-zA-Z]", "", seg).lower()
    return s[-n:]


def fuzzy_locate(prose: str, sig: str) -> int:
    """Return char position in `prose` whose ASCII-letter prefix-up-to-here
    ends with `sig` (best fuzzy match), or -1 if no good match."""
    if len(sig) < 8:
        return -1
    # Build mapping of [letters-only-index] -> [char-index-in-prose].
    letter_chars: list[int] = []
    letter_str_parts: list[str] = []
    for i, ch in enumerate(prose):
        if "a" <= ch.lower() <= "z":
            letter_chars.append(i)
            letter_str_parts.append(ch.lower())
    letter_str = "".join(letter_str_parts)

    # Try exact match first.
    pos = letter_str.find(sig)
    if pos >= 0:
        # Position in prose AFTER the matched letter run.
        end_letter_idx = pos + len(sig) - 1
        if end_letter_idx >= len(letter_chars):
            return -1
        return letter_chars[end_letter_idx] + 1

    # Fall back to SequenceMatcher: scan windows of length len(sig) and find
    # the highest-ratio window. Cap windows at 400 to keep runtime bounded.
    if not letter_str:
        return -1
    best_ratio = 0.0
    best_letter_end = -1
    sm = SequenceMatcher(autojunk=False, b=sig)
    step = max(1, len(letter_str) // 400)
    for start in range(0, max(1, len(letter_str) - len(sig) + 1), step):
        window = letter_str[start:start + len(sig)]
        sm.set_seq1(window)
        r = sm.quick_ratio()
        if r > best_ratio:
            best_ratio = r
            best_letter_end = start + len(sig) - 1
    if best_ratio < 0.78 or best_letter_end < 0:
        return -1
    if best_letter_end >= len(letter_chars):
        return -1
    return letter_chars[best_letter_end] + 1


def insert_sentinels(prose: str, page_notes: list[tuple[int, str]],
                     gv_prose: str) -> tuple[str, list[dict]]:
    """Return (annotated_prose, audit_rows) for one page."""
    expected = {n for n, _ in page_notes}
    note_text_by_no = {n: t for n, t in page_notes}
    gv_markers = find_gv_markers(gv_prose, expected)

    audit: list[dict] = []
    placements: list[tuple[int, int]] = []  # (insert_pos_in_prose, note_no)
    placed: set[int] = set()
    for n, gv_end in gv_markers:
        sig = signature(gv_prose, gv_end)
        pos = fuzzy_locate(prose, sig)
        if pos > 0:
            placements.append((pos, n))
            placed.add(n)
            audit.append({"note_no": n, "anchor": "matched", "sig_excerpt": sig[-12:]})
        else:
            audit.append({"note_no": n, "anchor": "no-fuzzy-match", "sig_excerpt": sig[-12:]})

    # Build new prose with sentinels.
    placements.sort()
    out: list[str] = []
    last = 0
    for pos, n in placements:
        out.append(prose[last:pos])
        body = note_text_by_no[n].replace("<!--", "<! --").replace("-->", "-- >")
        out.append(f"<!-- FOOTNOTE:{n} -->{body}<!-- /FOOTNOTE -->")
        last = pos
    out.append(prose[last:])

    # Append unanchored notes at end of prose.
    for n, t in page_notes:
        if n in placed:
            continue
        body = t.replace("<!--", "<! --").replace("-->", "-- >")
        out.append(f"\n<!-- FOOTNOTE-UNANCHORED:{n} -->{body}<!-- /FOOTNOTE -->\n")
        if not any(a["note_no"] == n for a in audit):
            audit.append({"note_no": n, "anchor": "no-marker", "sig_excerpt": ""})
    return "".join(out), audit


def main() -> int:
    rows = list(csv.DictReader(PAGES_CSV.open()))
    sec_rows: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        sec_rows[r["section"]].append(r)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inventory: list[dict] = []
    log_rows: list[dict] = []

    # Copy ALL cleaned pages first (so unchanged units pass-through unchanged).
    for r in rows:
        scan = int(r["scan_page"])
        src = CLEAN_DIR / f"p_{scan:04d}.md"
        dst = OUT_DIR / f"p_{scan:04d}.md"
        dst.write_text(src.read_text())

    gv_chunks = all_gv_chunks()

    for sec_id, label in UNITS:
        if sec_id not in sec_rows:
            continue
        prev_max = 0
        unit_notes_total = 0
        unit_anchored = 0
        unit_unanchored = 0
        page_summaries: list[str] = []

        for r in sec_rows[sec_id]:
            scan = int(r["scan_page"])
            page_path = OUT_DIR / f"p_{scan:04d}.md"
            md = page_path.read_text()
            header, body = parse_page_md(md)
            prose, notes, warns = split_prose_and_notes(body, prev_max)
            if not notes:
                continue
            # Strip notes-block heading-numbers that may have been mistaken
            # for note bodies (e.g. start-of-page "1.1 Title" inside chapter).
            # Already excluded by the prev_max anchor; sanity check below.
            for n, _ in notes:
                if n in (1, 2) and prev_max == 0 and HEADING_NUM_RE.search(body):
                    # Could be a heading mis-detected as a note. Don't fail —
                    # just record a warning.
                    warns.append(f"low-n note at chapter start: {n}")
            unit_notes_total += len(notes)

            # Get GV prose (everything before its own first note-body match).
            gv = gv_chunks[scan - 1] if scan - 1 < len(gv_chunks) else ""
            mm = NOTE_BODY_START.search(gv)
            gv_prose = gv[:mm.start()] if mm else gv

            new_prose, audit = insert_sentinels(prose, notes, gv_prose)
            new_body = new_prose + body[len(prose):]  # keep notes-block-tail-text dropped: we want it gone
            # Actually: drop the original notes-block from new_body, since we
            # have spliced the notes into the prose as sentinels.
            new_body = new_prose
            page_path.write_text(header + new_body.rstrip() + "\n")

            # Inventory rows + counters
            for a in audit:
                anchored = a["anchor"] == "matched"
                if anchored:
                    unit_anchored += 1
                else:
                    unit_unanchored += 1
                inventory.append({
                    "unit": sec_id,
                    "note_no": a["note_no"],
                    "source_scan": scan,
                    "source_printed": r["printed_page"],
                    "anchor_status": a["anchor"],
                    "sig_excerpt": a["sig_excerpt"],
                })
            page_summaries.append(
                f"  - scan {scan:03d} (p. {r['printed_page']}): "
                f"{len(notes)} notes "
                f"({sum(1 for a in audit if a['anchor']=='matched')} anchored, "
                f"{sum(1 for a in audit if a['anchor']!='matched')} unanchored)"
                + (f"  warnings: {warns}" if warns else "")
            )
            prev_max = max(prev_max, max(n for n, _ in notes))

        log_rows.append({
            "unit": sec_id, "label": label,
            "total": unit_notes_total,
            "anchored": unit_anchored,
            "unanchored": unit_unanchored,
            "details": page_summaries,
        })

    # Write inventory
    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    with INVENTORY.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["unit", "note_no", "source_scan", "source_printed",
                        "anchor_status", "sig_excerpt"],
            delimiter="\t",
        )
        w.writeheader()
        w.writerows(inventory)

    # Write log
    LOG.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Phase 4: footnote splitting log", ""]
    grand_total = sum(r["total"] for r in log_rows)
    grand_anch = sum(r["anchored"] for r in log_rows)
    lines.append(f"Detected **{grand_total}** note bodies across {len(log_rows)} units; "
                 f"**{grand_anch}** anchored inline ({grand_anch * 100 // max(grand_total,1)}%), "
                 f"**{grand_total - grand_anch}** placed as unanchored end-of-page footnotes.")
    lines.append("")
    lines.append("| unit | total | anchored | unanchored |")
    lines.append("|------|-------|----------|------------|")
    for r in log_rows:
        lines.append(f"| {r['unit']} | {r['total']} | {r['anchored']} | {r['unanchored']} |")
    lines.append("")
    lines.append("## Per-page detail")
    for r in log_rows:
        lines.append(f"### {r['unit']}")
        for d in r["details"]:
            lines.append(d)
        lines.append("")
    LOG.write_text("\n".join(lines) + "\n")

    print(f"phase 4: {grand_total} notes detected, {grand_anch} anchored "
          f"({grand_anch * 100 // max(grand_total,1)}%); "
          f"output → {OUT_DIR.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
