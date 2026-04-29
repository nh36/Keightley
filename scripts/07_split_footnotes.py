#!/usr/bin/env python3
"""Phase 4 (rev. 4b): footnote splitting — Google-Vision-driven.

Phase 4a (the original implementation) used Tesseract for both prose AND
note-block extraction.  Two pathologies emerged in the rendered output:

  * Tesseract OCR confuses note-numbers with letters: "9." → "g.",
    "1." → "l.", "8." → "B.".  The original regex
        ^\\d+[.,]\\s+[A-Z…]
    silently rejected these, gluing the rejected note's body onto the
    PREVIOUS accepted note.  E.g. note 8 absorbed note 9 on scan 21.
  * Anchor placement landed mid-word ("centu\\footnote{...}ry") because
    fuzzy_locate returned a bare letter-end position.

Phase 4b switches the note-block source to **Google Vision OCR**, which
reproduces digit prefixes cleanly (5.,6.,7.,8.,9.,10. — not 5.,6.,7.,8.,g.,10.),
preserves macrons / en-dashes, and only struggles with multi-column bodies
(which the bibliography uses but body chapters do not).

Tesseract is still used for the **prose substrate** because the column-aware
cleanup pipeline in Phase 2 ran against Tesseract output, and we don't want
to redo that.  GV is used for:

  1. note-block extraction          (note numbering + body text)
  2. marker detection in prose      (digit superscripts / suffixes)

Anchor placement:

  * Build a 24-char ASCII-letter signature from GV prose ending at the marker.
  * fuzzy-locate that signature in Tesseract prose.
  * **snap the position forward to the next word boundary** so the
    \\footnote{} marker doesn't land inside an OCR'd word.

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


# Note bodies in GV are dependably "<digit(s)>. <Capital>" or, occasionally,
# "<digit(s)>, <Capital>".  We accept comma as well to absorb GV's rare
# comma/period confusion.
NOTE_BODY_START = re.compile(
    r"^(\d{1,3})[\.,]\s+([\u201C\u201D\"A-Z\u00C0-\u017F][^\n]*)$",
    re.MULTILINE,
)
HEADING_NUM_RE = re.compile(r"^\d+\.\d+\s+[A-Z]", re.MULTILINE)
SOURCE_HDR_RE = re.compile(r"<!--\s*source:.+?-->", re.DOTALL)
COMMENT_RE = re.compile(r"<!--.+?-->", re.DOTALL)
WS_RE = re.compile(r"\s+")

# Units that have notes (chapters, appendices, preface, preamble).
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


def extract_notes_from_gv(gv_chunk: str, prev_max: int
                          ) -> tuple[int, list[tuple[int, str]], list[str]]:
    """From a GV page chunk, find the trailing notes block and return
    (split_position_in_gv, notes, warnings).

    `split_position_in_gv` is the char offset where the note block starts
    (so gv_chunk[:split_position_in_gv] is the prose half).  `notes` is a
    list of (note_no, body_text) in order.

    Strategy: walk match candidates in the LAST N chars of the chunk and
    pick the longest contiguous tail-suffix whose numbers are strictly
    increasing AND continue the chapter sequence (>= prev_max + 1, allowing
    a small slack of -1 for OCR mishaps in either direction).
    """
    warns: list[str] = []
    candidates = list(NOTE_BODY_START.finditer(gv_chunk))
    if not candidates:
        return len(gv_chunk), [], warns

    # Identify the tail-run: starting from the last candidate, walk
    # backwards while numbers are strictly decreasing.
    tail: list[re.Match] = []
    for m in reversed(candidates):
        n = int(m.group(1))
        if not tail:
            tail.append(m)
            continue
        prev_n = int(tail[-1].group(1))
        if n < prev_n:
            tail.append(m)
        elif n == prev_n:
            # Duplicate digit — skip.
            continue
        else:
            # Increase as we walk backwards = wrong direction; stop.
            break
    tail.reverse()

    # Validate: first number must be a plausible continuation of the
    # chapter's note sequence.
    if not tail:
        return len(gv_chunk), [], warns

    first_n = int(tail[0].group(1))
    if not (prev_max < first_n <= prev_max + 50):
        # The "tail" is probably a numbered list inside prose, not notes.
        return len(gv_chunk), [], warns

    # Validate sequence continuity; allow one-step gaps with a warning.
    chosen: list[re.Match] = [tail[0]]
    for m in tail[1:]:
        prev_n = int(chosen[-1].group(1))
        n = int(m.group(1))
        if n == prev_n + 1:
            chosen.append(m)
        elif n <= prev_n + 5:
            warns.append(f"note-gap: {prev_n} -> {n}")
            chosen.append(m)
        else:
            warns.append(f"note-block-break: {prev_n} -> {n} (not appended)")
            break

    notes: list[tuple[int, str]] = []
    for i, m in enumerate(chosen):
        end = chosen[i + 1].start() if i + 1 < len(chosen) else len(gv_chunk)
        prefix_re = re.match(r"^\d+[\.,]\s+", gv_chunk[m.start():end])
        text_start = m.start() + (prefix_re.end() if prefix_re else 0)
        body = gv_chunk[text_start:end].strip()
        # GV preserves hard line breaks within a note; collapse them.
        body = re.sub(r"-\n", "", body)         # de-hyphenate line wraps
        body = re.sub(r"\s*\n\s*", " ", body)   # join soft wraps
        body = re.sub(r"\s{2,}", " ", body)
        notes.append((int(m.group(1)), body))

    return chosen[0].start(), notes, warns


# Cache GV chunks for all 326 pages once.
_GV_CHUNKS: list[str] | None = None
def all_gv_chunks() -> list[str]:
    global _GV_CHUNKS
    if _GV_CHUNKS is None:
        _GV_CHUNKS = GV_PATH.read_text().split("\f")
    return _GV_CHUNKS


# Marker regex in GV: a closing-letter-or-punct, optional whitespace, then
# the digit, then a non-letter terminator.  The preceding char is captured
# as part of the match (not via lookbehind) because Python's re module
# only allows FIXED-WIDTH lookbehind, which would prevent us from accepting
# "century. 6 Far" (space between '.' and '6').  m.end() still points
# correctly to the position just after the digit.
GV_MARKER_RE = re.compile(
    r"[a-z\)\u2019\u201d\u201c\"\.,;:!?][ \t\u00a0]{0,2}(\d{1,3})"
    r"(?=[\s,.\u201c\u201d\"\(\)\u2014\u2013\-—–\?!]|$)"
)
# Also match line-break markers: a digit alone on its own line, between
# two prose lines.  Captures notes whose marker GV represented as
# "text\nN\ntext".  Only single-line-isolated digits to avoid colliding
# with the note-block (which is pruned out of gv_prose anyway).
GV_NEWLINE_MARKER_RE = re.compile(
    r"(?:^|\n)(\d{1,3})\n(?=[A-Za-z\d])"
)
# Mixed superscript+digit: "³9" or "¹⁰0" → "39", "100".  Preceded by
# closing letter/punct.
GV_MIXED_SUPER_RE = re.compile(
    r"(?<=[a-z\)\u2019\u201d\.,;:!?\"])"
    r"([\u00b9\u00b2\u00b3\u2070-\u2079][\u00b9\u00b2\u00b3\u2070-\u2079\d]*)"
)
# Reverse mixed: "7¹" = "71" — regular digit followed by superscript(s).
# Used by GV when the trailing digit was rendered as superscript.
GV_MIXED_TRAIL_RE = re.compile(
    r"(?<=[a-z\)\u2019\u201d\.,;:!?\" ])"
    r"(\d[\u00b9\u00b2\u00b3\u2070-\u2079]+)"
)
# Also catch unicode superscript digits.
SUPERSCRIPT = {
    "\u2070": "0", "\u00b9": "1", "\u00b2": "2", "\u00b3": "3",
    "\u2074": "4", "\u2075": "5", "\u2076": "6", "\u2077": "7",
    "\u2078": "8", "\u2079": "9",
}
SUPER_MARKER_RE = re.compile(r"(?<=[a-z\)\u2019\u201d\.,;:!?\"])([\u2070-\u2079\u00b9\u00b2\u00b3]+)")


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
    for m in GV_MIXED_SUPER_RE.finditer(gv_prose):
        digits = "".join(SUPERSCRIPT.get(c, c) for c in m.group(1))
        if not digits.isdigit():
            continue
        try:
            n = int(digits)
        except ValueError:
            continue
        if n in expected:
            found.append((n, m.end()))
    for m in GV_MIXED_TRAIL_RE.finditer(gv_prose):
        digits = "".join(SUPERSCRIPT.get(c, c) for c in m.group(1))
        if not digits.isdigit():
            continue
        try:
            n = int(digits)
        except ValueError:
            continue
        if n in expected:
            found.append((n, m.end()))
    for m in GV_NEWLINE_MARKER_RE.finditer(gv_prose):
        try:
            n = int(m.group(1))
        except ValueError:
            continue
        if n in expected:
            # Position the marker just after the digit (m.end() is the
            # newline after the digit, which is fine for snap_to_word_boundary)
            found.append((n, m.start(1) + len(m.group(1))))
    found.sort(key=lambda x: x[1])

    # Filter: keep only an in-order, non-decreasing-by-position run that
    # matches the expected order (sorted ascending).
    expected_order = sorted(expected)
    result: list[tuple[int, int]] = []
    cursor = 0
    for n, pos in found:
        while cursor < len(expected_order) and expected_order[cursor] != n:
            if n > expected_order[cursor]:
                cursor += 1
            else:
                break
        if cursor >= len(expected_order):
            break
        if expected_order[cursor] == n:
            if result and result[-1][0] == n:
                continue
            result.append((n, pos))
            cursor += 1
    return result


def signature(text: str, end_pos: int, n: int = 32) -> str:
    """ASCII-letter signature of length ~n from text[end_pos-n*3:end_pos]."""
    seg = text[max(0, end_pos - n * 3): end_pos]
    s = re.sub(r"[^a-zA-Z]", "", seg).lower()
    return s[-n:]


def fuzzy_locate(prose: str, sig: str) -> int:
    """Return char position in `prose` where the ASCII-letter prefix-up-to-here
    ends with `sig` (best fuzzy match), or -1 if no good match.

    The returned position is right after the last matched letter; callers
    are expected to call snap_to_word_boundary() before using it.
    """
    if len(sig) < 8:
        return -1
    letter_chars: list[int] = []
    letter_str_parts: list[str] = []
    for i, ch in enumerate(prose):
        if "a" <= ch.lower() <= "z":
            letter_chars.append(i)
            letter_str_parts.append(ch.lower())
    letter_str = "".join(letter_str_parts)

    pos = letter_str.find(sig)
    if pos >= 0:
        end_letter_idx = pos + len(sig) - 1
        if end_letter_idx >= len(letter_chars):
            return -1
        return letter_chars[end_letter_idx] + 1

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


def snap_to_word_boundary(prose: str, pos: int) -> int:
    """Move `pos` forward past any in-word letters, then past any closing
    punctuation that should naturally precede a footnote-marker.

    Examples (| marks the resulting position):
        "centu|ry was..."           -> "century|. was..."  (advance through "ry")
        "scapulas|. The custom"     -> "scapulas.|" + footnote-marker -> ".|"
        "(1879)|, p. 431"           -> kept at "(1879)|" since `)` is non-letter
    """
    n = len(prose)
    # Step 1: advance through any remaining alphabetics in the current word.
    while pos < n and prose[pos].isalpha():
        pos += 1
    # Step 2: prefer to put the marker AFTER trailing closing-punctuation
    # (period, comma, semicolon, colon, closing-quote, closing-paren) so
    # superscript-like behaviour reads naturally.  But not whitespace.
    while pos < n and prose[pos] in ".,;:!?\u2019\u201d)\u00bb":
        pos += 1
    return pos


def insert_sentinels(prose: str, page_notes: list[tuple[int, str]],
                     gv_prose: str) -> tuple[str, list[dict]]:
    """Return (annotated_prose, audit_rows) for one page.

    Note BODIES come from GV (page_notes); marker POSITIONS come from GV
    (gv_prose); placement happens against Tesseract `prose` via fuzzy match.
    """
    expected = {n for n, _ in page_notes}
    note_text_by_no = {n: t for n, t in page_notes}
    gv_markers = find_gv_markers(gv_prose, expected)

    audit: list[dict] = []
    placements: list[tuple[int, int]] = []
    placed: set[int] = set()
    for n, gv_end in gv_markers:
        sig = signature(gv_prose, gv_end)
        raw_pos = fuzzy_locate(prose, sig)
        if raw_pos > 0:
            pos = snap_to_word_boundary(prose, raw_pos)
            placements.append((pos, n))
            placed.add(n)
            audit.append({"note_no": n, "anchor": "matched", "sig_excerpt": sig[-12:]})
        else:
            audit.append({"note_no": n, "anchor": "no-fuzzy-match", "sig_excerpt": sig[-12:]})

    placements.sort()
    out: list[str] = []
    last = 0
    for pos, n in placements:
        out.append(prose[last:pos])
        body = note_text_by_no[n].replace("<!--", "<! --").replace("-->", "-- >")
        out.append(f"<!-- FOOTNOTE:{n} -->{body}<!-- /FOOTNOTE -->")
        last = pos
    out.append(prose[last:])

    for n, t in page_notes:
        if n in placed:
            continue
        body = t.replace("<!--", "<! --").replace("-->", "-- >")
        out.append(f"\n<!-- FOOTNOTE-UNANCHORED:{n} -->{body}<!-- /FOOTNOTE -->\n")
        if not any(a["note_no"] == n for a in audit):
            audit.append({"note_no": n, "anchor": "no-marker", "sig_excerpt": ""})
    return "".join(out), audit


def strip_tesseract_notes_block(body: str, prev_max: int) -> str:
    """Return Tesseract `body` with its trailing notes-block removed.

    We can't trust Tesseract digit recognition for the first character, so
    we tolerate digit / letter look-alikes (g↔9, l↔1, B↔8, S↔5, O↔0).
    The block-start is the FIRST line in the page tail that:
      * begins with one of those tokens followed by `.` or `,`
      * has a parseable canonical number `>= prev_max + 1`
      * is followed (anywhere later in the tail) by another such token with
        canonical value `+1`, OR is the only note on the page
    """
    LETTER_TO_DIGIT = {
        "O": "0", "o": "0",
        "l": "1", "I": "1", "i": "1", "|": "1",
        "S": "5", "s": "5",
        "B": "8",
        "g": "9", "q": "9",
    }
    def canon(tok: str) -> int | None:
        digits = []
        for ch in tok:
            if ch.isdigit():
                digits.append(ch)
            elif ch in LETTER_TO_DIGIT:
                digits.append(LETTER_TO_DIGIT[ch])
            else:
                return None
        if not digits:
            return None
        try:
            return int("".join(digits))
        except ValueError:
            return None

    candidate_re = re.compile(
        r"^([0-9gqlIiBSosO|]{1,3})[\.,]\s+([\u201C\u201D\"A-Z\u00C0-\u017F])",
        re.MULTILINE,
    )
    matches = list(candidate_re.finditer(body))
    if not matches:
        return body

    chosen_start: int | None = None
    last_n = prev_max
    for m in matches:
        n = canon(m.group(1))
        if n is None:
            continue
        if chosen_start is None:
            if prev_max < n <= prev_max + 50:
                chosen_start = m.start()
                last_n = n
        else:
            if n == last_n + 1 or n <= last_n + 5:
                last_n = n
    return body[:chosen_start] if chosen_start is not None else body


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
            header, tess_body = parse_page_md(md)

            gv = gv_chunks[scan - 1] if scan - 1 < len(gv_chunks) else ""
            gv_split, notes, warns = extract_notes_from_gv(gv, prev_max)
            if not notes:
                continue
            gv_prose = gv[:gv_split]

            # Strip Tesseract's notes-block — but use canonical-number
            # detection so e.g. "g. Satow" (=9.) is recognised as a note
            # boundary and gets dropped along with its body.
            tess_prose = strip_tesseract_notes_block(tess_body, prev_max)

            unit_notes_total += len(notes)
            new_prose, audit = insert_sentinels(tess_prose, notes, gv_prose)
            page_path.write_text(header + new_prose.rstrip() + "\n")

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

    LOG.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Phase 4: footnote splitting log (rev 4b)", ""]
    grand_total = sum(r["total"] for r in log_rows)
    grand_anch = sum(r["anchored"] for r in log_rows)
    lines.append(f"Detected **{grand_total}** note bodies across {len(log_rows)} units; "
                 f"**{grand_anch}** anchored inline ({grand_anch * 100 // max(grand_total,1)}%), "
                 f"**{grand_total - grand_anch}** placed as unanchored end-of-page footnotes.")
    lines.append("")
    lines.append("Note BODIES sourced from Google Vision OCR; marker positions also from GV; "
                 "anchor placement against Tesseract prose with word-boundary snap.")
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

    print(f"phase 4b: {grand_total} notes detected, {grand_anch} anchored "
          f"({grand_anch * 100 // max(grand_total,1)}%); "
          f"output → {OUT_DIR.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
