#!/usr/bin/env python3
"""Phase 5 step B: extract bibliography entries.

Inputs
------
- build/ocr/bibliography/p_NNNN.txt — psm 6 Tesseract OCR of scans 275–302.
- source/Keightley_1978.txt           — Google-Vision OCR (form-feed delimited),
                                         used as a CJK / disambiguation cross-check.

Outputs
-------
- data/bibliography_raw.tsv           — one row per parsed (author, year) sub-entry.
- data/abbreviations.yml              — Bibliography A oracle-bone collection abbrevs.
- tex/bibliography/keightley.bib      — best-effort biblatex emission of bibliography B.
- tex/backmatter/abbreviations.tex    — typeset abbreviations table for Bibliography A.
- build/qa/bibliography_extraction.md — counts + caveats.

Heuristics (Bibliography B)
---------------------------
A bibliography entry has hanging-indent layout:

    Author Surname [CJK]                  ← header line (col 0)
        1955  "Title."  Container ...     ← year sub-entry (indented)
        1977  Title.    Place: Publisher. ← year sub-entry
            wrapped continuation ...      ← continuation

OCR introduces leading garbage on many lines (`|`, `i`, `a`, etc.).  The parser
strips that prefix, then classifies each cleaned line as:

    YEAR        line starts with 19\d{2}[a-z]?
    AUTHOR      line is short, has no year, looks like a Name
    CONTINUATION otherwise
"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
BIB_DIR = ROOT / "build" / "ocr" / "bibliography"
GV_TXT = ROOT / "source" / "Keightley_1978.txt"
DATA_DIR = ROOT / "data"
TEX_DIR = ROOT / "tex"
QA_DIR = ROOT / "build" / "qa"
LOG_DIR = ROOT / "build" / "logs"

BIB_A_SCANS = list(range(275, 278))   # 275-277
BIB_B_SCANS = list(range(278, 303))   # 278-302

CJK_RE = re.compile(r"[\u3000-\u9FFF\uF900-\uFAFF]+")
LEADING_GARBAGE_RE = re.compile(
    r"^(?:[|\\/_,.\-‘’“”\"'\s]|[\u3000-\u303F\u4E00-\u9FFF])+"
)
YEAR_RE = re.compile(r"^(?P<year>(?:18|19|20)\d{2})(?P<suffix>[a-z]?)\b\s*(?P<rest>.*)$")
AUTHOR_RE = re.compile(
    r"""^
        (?P<name>[A-Z][\w'’\-]+(?:[ ,]+(?:and\s+)?[A-Z][\w'’\-\.]*)*?)
        (?:\s+\((?P<role>ed|eds|comp)\.\))?
        (?:\s+(?P<cjk>[\u3000-\u9FFF\uF900-\uFAFF].*))?
        \s*$
    """,
    re.VERBOSE,
)


def load_lines(scan: int) -> list[str]:
    p = BIB_DIR / f"p_{scan:04d}.txt"
    return p.read_text(encoding="utf-8").splitlines() if p.exists() else []


# --- Google Vision cross-reference ----------------------------------------
_GV_CACHE: dict[int, str] = {}


def gv_page(scan: int) -> str:
    """Return the Google Vision OCR text for the given scan number.

    GV text is significantly cleaner than Tesseract for CJK glyphs and
    Romaji diacritics (e.g. "Kōhon", "Chūgoku", "Itō") but its column
    reading-order is more scrambled.  We use it as a lookup pool to upgrade
    Tesseract entries with proper Unicode characters."""
    if not _GV_CACHE:
        chunks = GV_TXT.read_text(encoding="utf-8").split("\f")
        for i, c in enumerate(chunks, start=1):
            _GV_CACHE[i] = c
    return _GV_CACHE.get(scan, "")


def gv_candidates_for_year(scan: int, year: str, suffix: str) -> list[str]:
    """Return GV lines that plausibly correspond to a (year, suffix) sub-entry
    on the given scan.  Returned lines are stripped and deduped, ordered by
    their proximity to the year token in the GV stream."""
    text = gv_page(scan)
    if not text:
        return []
    target = f"{year}{suffix}"
    lines = text.splitlines()
    # Find indices of the year+suffix token
    hits: list[int] = []
    pat = re.compile(rf"(?:^|\b){re.escape(target)}\b")
    for i, ln in enumerate(lines):
        if pat.search(ln):
            hits.append(i)
    if not hits:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for h in hits:
        # Capture the line itself plus the next 4 lines as candidate title text
        for j in range(h, min(h + 5, len(lines))):
            cand = lines[j].strip()
            if not cand or cand in seen:
                continue
            if YEAR_RE.match(cand):
                continue
            seen.add(cand)
            out.append(cand)
    return out


def gv_candidates_near_author(scan: int, author: str) -> list[str]:
    """Return CJK-rich GV lines near where the author surname appears."""
    text = gv_page(scan)
    if not text:
        return []
    surname = re.split(r"[ ,]", author.strip())[0]
    if len(surname) < 3:
        return []
    lines = text.splitlines()
    out: list[str] = []
    for i, ln in enumerate(lines):
        if surname in ln:
            for j in range(max(0, i - 1), min(i + 4, len(lines))):
                cand = lines[j].strip()
                if cand and CJK_RE.search(cand):
                    out.append(cand)
    return out


def best_gv_title(candidates: list[str]) -> str:
    """Pick the most likely full title from GV candidate lines.  Prefer lines
    that contain CJK glyphs and are reasonably long."""
    if not candidates:
        return ""
    scored = []
    for c in candidates:
        cjk_count = len(CJK_RE.findall(c))
        # Penalise lines that are bare year tokens / page-numbers
        if re.fullmatch(r"\d+[a-z]?", c):
            continue
        score = len(c) + cjk_count * 8
        # Prefer lines that look like titles (quoted, contain '.', etc.)
        if '"' in c or "“" in c or "”" in c:
            score += 20
        if "." in c:
            score += 10
        scored.append((score, c))
    scored.sort(reverse=True)
    return scored[0][1] if scored else ""


def gv_cjk_chunks(candidates: list[str]) -> str:
    """Concatenate distinct CJK substrings from a list of GV candidate lines."""
    seen: list[str] = []
    for c in candidates:
        for m in CJK_RE.findall(c):
            m = m.strip()
            if m and m not in seen:
                seen.append(m)
    return " ".join(seen)
# --------------------------------------------------------------------------


def clean_line(s: str) -> str:
    # Strip OCR margin noise like leading "| ", "i ", ". ", etc.
    s = s.rstrip()
    s = LEADING_GARBAGE_RE.sub("", s)
    # Common OCR substitutions in pure noise
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def looks_like_author(line: str) -> bool:
    """Heuristic: an author header is a short line (a name + optional CJK
    transliteration) appearing at column 0.  We do NOT require a trailing
    end-of-line anchor because Tesseract often appends garbage glyphs."""
    if not line:
        return False
    if YEAR_RE.match(line):
        return False
    if len(line) > 70:
        return False
    if not line[0].isupper():
        return False
    if line.upper().startswith(("BIBLIOGRAPHY", "OTHER WORKS")):
        return False
    if re.search(r"\b(pp?\.|vol\.|Press|edited by|Reprint|N\.p\.|Mimeographed)\b", line):
        return False
    if re.search(r"\d{2,}", line) and not re.search(r"[\u4E00-\u9FFF]", line):
        return False
    if "," in line and re.search(r",\s+\d", line):
        return False
    tokens = line.split()
    if not tokens:
        return False
    first = tokens[0].rstrip(",.")
    # Reject obvious OCR junk prefixes (short all-caps that aren't real names).
    if first.isupper() and len(first) <= 2:
        return False
    if re.fullmatch(r"[A-Z][a-z]?", first):
        return False  # single letter like "A" or "Ce"
    # Single-token "names" are usually OCR fallout from tail-of-entry words
    # like "Peiping." or "Hong" — only accept if the token is hyphenated
    # (suggesting Wade-Giles) or has a CJK suffix.
    if len(tokens) == 1 and "-" not in first and not CJK_RE.search(line):
        return False
    if line.rstrip().endswith(".") and len(tokens) <= 2 and "-" not in first:
        return False
    # Reject bare place-name-like tokens
    if first in {"Peiping", "Tokyo", "Peking", "Shanghai", "Taipei", "Hong",
                 "London", "Paris", "Berlin", "Stanford", "Berkeley", "Kyoto",
                 "Reprint", "Mimeographed", "Bibliography"}:
        return False
    # Count "name-like" leading tokens
    name_tokens = 0
    for t in tokens:
        if t and t[0].isupper() and re.match(r"^[A-Z][\w'’\-\.,]*$", t):
            name_tokens += 1
        else:
            break
    if name_tokens < 1 or name_tokens > 5:
        return False
    # First token must look like a real surname (≥ 3 chars)
    if len(first) < 3:
        return False
    return True


def is_indented_orig(raw: str) -> bool:
    # Heuristic: detect column-0 vs indented in the raw OCR
    lstrip = raw.lstrip(" \t|.,'_-‘’\"")
    return raw.startswith(("    ", "\t")) or (len(raw) - len(lstrip)) >= 4


def parse_bibliography_b() -> list[dict]:
    entries: list[dict] = []
    cur_author: Optional[dict] = None
    cur_subentry: Optional[dict] = None

    def flush_subentry():
        nonlocal cur_subentry
        if cur_subentry and cur_author:
            cur_subentry["author"] = cur_author["name"]
            cur_subentry["author_cjk"] = cur_author.get("cjk", "")
            cur_subentry["author_role"] = cur_author.get("role", "")
            entries.append(cur_subentry)
        cur_subentry = None

    for scan in BIB_B_SCANS:
        for raw in load_lines(scan):
            line = clean_line(raw)
            if not line:
                continue
            # Skip running heads / page numbers
            if re.fullmatch(r"\d{3}", line):
                continue
            if line.upper().startswith("BIBLIOGRAPHY") or line == "Other Works Cited":
                continue

            ym = YEAR_RE.match(line)
            if ym:
                flush_subentry()
                cur_subentry = {
                    "scan": scan,
                    "year": ym.group("year"),
                    "suffix": ym.group("suffix"),
                    "body_lines": [ym.group("rest").strip()],
                }
                continue

            if looks_like_author(line) and not is_indented_orig(raw):
                flush_subentry()
                # Split: leading roman tokens form the name, trailing CJK
                # (if any) is the transliteration.
                cjk_match = CJK_RE.search(line)
                if cjk_match:
                    name_part = line[:cjk_match.start()].rstrip(" ,")
                    cjk_part = cjk_match.group(0).strip()
                else:
                    # Strip trailing OCR garbage (single-letter / lowercase tokens)
                    parts = line.split()
                    keep = []
                    for t in parts:
                        if re.match(r"^[A-Z]", t) or t.lower() in ("and", "et", "al."):
                            keep.append(t)
                        else:
                            break
                    name_part = " ".join(keep) if keep else line
                    cjk_part = ""
                # Detect editor / role suffix
                role = ""
                role_match = re.search(r"\((ed|eds|comp)\.\)", line)
                if role_match:
                    role = role_match.group(1)
                cur_author = {
                    "name": name_part.strip(),
                    "role": role,
                    "cjk": cjk_part,
                    "scan": scan,
                }
                continue

            # Continuation
            if cur_subentry is not None:
                cur_subentry["body_lines"].append(line)
            elif cur_author is not None:
                # Could be a CJK addendum to author
                cjk_match = CJK_RE.search(line)
                if cjk_match and not cur_author.get("cjk"):
                    cur_author["cjk"] = cjk_match.group(0)

    flush_subentry()
    # Cross-reference each sub-entry against Google Vision
    for e in entries:
        cands = gv_candidates_for_year(e["scan"], e["year"], e["suffix"])
        e["gv_candidates"] = cands
        e["gv_title"] = best_gv_title(cands)
        e["gv_cjk"] = gv_cjk_chunks(cands)
        if not e.get("author_cjk") and e.get("author"):
            ac = gv_candidates_near_author(e["scan"], e["author"])
            cjk = gv_cjk_chunks(ac)
            if cjk:
                e["author_cjk"] = cjk.split()[0]  # first CJK run
    return entries


def parse_bibliography_a() -> list[dict]:
    """Each line of Bib A has format: 'Abbreviation  Author. Title. Place, Year.'

    The abbreviation is a short hyphenated/dotted token at the start of the line.
    Some entries span two physical lines.
    """
    entries: list[dict] = []
    cur: Optional[dict] = None

    def flush():
        nonlocal cur
        if cur:
            entries.append(cur)
        cur = None

    SKIP_LINES = {
        "Abbreviations", "and Their Abbreviations", "Oracle-Bone Collections",
        "Oracle-Bone Collections Cited", "Oracle-Bone Collections Cited and Their Abbreviations",
    }
    for scan in BIB_A_SCANS:
        for raw in load_lines(scan):
            line = clean_line(raw)
            if not line or line.upper().startswith("BIBLIOGRAPHY"):
                continue
            if line in SKIP_LINES:
                continue
            if re.match(r"^(Oracle-Bone Collections|and Their Abbreviations)", line):
                continue
            if re.fullmatch(r"\d{3}", line):
                continue
            # Abbreviation tokens follow a tight typology:
            #   - hyphenated Wade-Giles ("Cheng-chai", "Chia-pien", "Hai-wai")
            #   - apostrophed Wade-Giles ("Ts'ui-pien", "Ts'un-chen")
            #   - all-caps acronym ("AYFC", "USB", "CCC")
            #   - a few plain English ones ("Bone", "White") that we list
            #     explicitly because plain capitalised words otherwise collide
            #     with bibliography continuation text.
            ENGLISH_ABBRS = {"Bone", "White"}
            tok_match = re.match(r"^(\S+)\s+(.+)$", line)
            if not tok_match or YEAR_RE.match(line):
                if cur:
                    cur["body_lines"].append(line)
                continue
            tok, rest = tok_match.group(1), tok_match.group(2)
            tok_clean = tok.rstrip(",.;")
            is_hyphenated = ("-" in tok_clean
                              and tok_clean[0].isupper()
                              and 4 <= len(tok_clean) <= 18)
            is_acronym = tok_clean.isupper() and 2 <= len(tok_clean) <= 5
            is_known_eng = tok_clean in ENGLISH_ABBRS
            if not (is_hyphenated or is_acronym or is_known_eng):
                if cur:
                    cur["body_lines"].append(line)
                continue
            # Skip continuation tokens that look like abbrs but are textual
            # ("Oracle Bone}." closing a bracketed phrase).
            if rest.lstrip().startswith(("Bone}", "Bone].")):
                if cur:
                    cur["body_lines"].append(line)
                continue
            flush()
            cur = {"scan": scan, "abbr": tok_clean, "body_lines": [rest.strip()]}
    flush()
    # GV cross-reference: for each abbreviation, search the GV page text for
    # CJK runs near the abbreviation token (or near the romanised author name
    # in the body).
    for e in entries:
        body = " ".join(e["body_lines"])
        cands = []
        # Look up by abbr token first
        text = gv_page(e["scan"])
        if text and e["abbr"] in text:
            idx = text.find(e["abbr"])
            cands.extend(text[idx:idx + 600].splitlines())
        # Plus search for the first author-name token in the body
        first_author = re.match(r"^([A-Z][\w'’\-]+)", body)
        if first_author and text:
            tok = first_author.group(1)
            if tok in text:
                idx = text.find(tok)
                cands.extend(text[idx:idx + 400].splitlines())
        e["gv_cjk"] = gv_cjk_chunks(cands)
        e["gv_excerpt"] = best_gv_title(cands)
    return entries


def make_key(author: str, year: str, suffix: str, body: str) -> str:
    surname = re.split(r"[ ,]", author.strip())[0]
    surname = re.sub(r"[^A-Za-z]", "", surname) or "Anon"
    # First substantial word from the body becomes the short title
    body_clean = re.sub(r"^\W+", "", body)
    body_clean = re.sub(r'^"[A-Za-z]', "", body_clean)
    word_match = re.search(r"[A-Z][A-Za-z]{2,}", body_clean)
    short = word_match.group(0) if word_match else "Work"
    short = short[:14]
    return f"{surname}{year}{suffix}{short}"


def emit_bib(entries: list[dict]) -> str:
    out: list[str] = [
        "% Generated by scripts/08_extract_bibliography.py — DO NOT EDIT BY HAND.",
        "% Source: Keightley 1978, Bibliography B (scans 278–302).",
        "% Each entry contains `note = {RAW: ...; GV: ...}` capturing both the",
        "% Tesseract OCR (clean layout) and the Google Vision OCR (clean glyphs)",
        "% as CHECK markers for Phase 11 proofing.",
        "",
    ]
    seen_keys: dict[str, int] = {}
    for e in entries:
        body = " ".join(e["body_lines"]).strip()
        if not body:
            continue
        gv_title = e.get("gv_title", "").strip()
        gv_cjk = e.get("gv_cjk", "").strip()
        # Prefer the GV title when it is appreciably longer than what Tesseract
        # extracted (and contains CJK or proper diacritics).
        title_match = re.match(r'^["“‘]+(.+?)["”’\.]+', body)
        if title_match:
            tess_title = title_match.group(1).strip()
        else:
            tm2 = re.match(r"^([^.]+)\.", body)
            tess_title = tm2.group(1).strip() if tm2 else body[:80]
        chosen_title = tess_title
        if gv_title and (len(gv_title) > len(tess_title) * 0.8) and (
            CJK_RE.search(gv_title) or re.search(r"[āēīōūĀĒĪŌŪ]", gv_title)
        ):
            chosen_title = gv_title

        key = make_key(e["author"], e["year"], e["suffix"], chosen_title or body)
        seen_keys[key] = seen_keys.get(key, 0) + 1
        if seen_keys[key] > 1:
            key = f"{key}_{seen_keys[key]}"

        # Combine CJK from Tesseract body and GV cross-reference
        cjk_in_body = CJK_RE.findall(body)
        titleaddon_pieces = []
        for piece in cjk_in_body + [gv_cjk]:
            if piece and piece.strip() and piece.strip() not in titleaddon_pieces:
                titleaddon_pieces.append(piece.strip())
        titleaddon = " ".join(titleaddon_pieces)

        type_guess = "@article" if re.search(
            r"\b(pp\.|vol\.|Journal|Bulletin)\b", body) else "@book"
        author_field = e["author"]
        if e["author_role"] in ("ed", "eds"):
            entrytype = type_guess.replace("@book", "@collection")
            author_line = f"  editor      = {{{author_field}}},"
        else:
            entrytype = type_guess
            author_line = f"  author      = {{{author_field}}},"
        lines = [
            f"{entrytype}{{{key},",
            author_line,
            f"  year        = {{{e['year']}}},",
            f"  title       = {{{chosen_title.replace('{', '').replace('}', '')}}}",
        ]
        if titleaddon:
            lines[-1] += ","
            lines.append(f"  titleaddon  = {{{titleaddon}}}")
        if e.get("author_cjk"):
            lines[-1] += ","
            lines.append(f"  nameaddon   = {{{e['author_cjk']}}}")
        # Always include both raw OCR streams for proofing.  Strip braces and
        # backslashes to keep the bib file valid even when the OCR contains
        # accidental TeX-looking sequences.
        lines[-1] += ","
        def _bibsafe(s: str) -> str:
            return s.replace("\\", "/").replace("{", "(").replace("}", ")")
        raw_safe = _bibsafe(body)
        gv_safe = _bibsafe(gv_title)
        if gv_safe:
            lines.append(f"  note        = {{RAW: {raw_safe} ; GV: {gv_safe}}}")
        else:
            lines.append(f"  note        = {{RAW: {raw_safe}}}")
        lines.append("}\n")
        out.extend(lines)
    return "\n".join(out) + "\n"


def emit_abbreviations_yml(entries: list[dict]) -> str:
    lines = [
        "# Generated by scripts/08_extract_bibliography.py.",
        "# Bibliography A: oracle-bone collection abbreviations (scans 275–277).",
        "# `gv_cjk` and `gv_excerpt` are sourced from the Google Vision OCR for",
        "# proofing — Tesseract is cleaner on layout, GV on CJK glyphs.",
        "abbreviations:",
    ]
    for e in entries:
        body = " ".join(e["body_lines"]).strip().replace('"', "'")
        lines.append(f"  - abbr: {e['abbr']!r}")
        lines.append(f"    body_tesseract: {body!r}")
        if e.get("gv_excerpt"):
            lines.append(f"    gv_excerpt: {e['gv_excerpt']!r}")
        if e.get("gv_cjk"):
            lines.append(f"    gv_cjk: {e['gv_cjk']!r}")
        lines.append(f"    scan: {e['scan']}")
    return "\n".join(lines) + "\n"


def _latex_escape(s: str) -> str:
    """Escape LaTeX-special characters in raw OCR text.

    OCR output may contain stray backslashes, braces, tildes, etc., which would
    be interpreted as control sequences if dropped into a TeX file verbatim.
    Order matters: backslash first, then the others.
    """
    if not s:
        return s
    s = s.replace("\\", "\\textbackslash{}")
    s = s.replace("{", "\\{").replace("}", "\\}")
    s = s.replace("&", "\\&").replace("#", "\\#").replace("%", "\\%")
    s = s.replace("_", "\\_").replace("$", "\\$")
    s = s.replace("^", "\\^{}").replace("~", "\\~{}")
    return s


def emit_abbreviations_tex(entries: list[dict]) -> str:
    out = [
        "% Generated by scripts/08_extract_bibliography.py.",
        "\\section*{Oracle-Bone Collections Cited and Their Abbreviations}",
        "\\addcontentsline{toc}{section}{Oracle-Bone Collections Cited and Their Abbreviations}",
        "",
        "\\begin{description}",
    ]
    for e in entries:
        body = " ".join(e["body_lines"]).strip()
        body = _latex_escape(body)
        abbr_safe = _latex_escape(e["abbr"]).replace("'", "\\textquotesingle{}")
        cjk_note = ""
        if e.get("gv_cjk"):
            cjk_note = f" \\hfill\\textit{{[CJK: {e['gv_cjk']}]}}"
        out.append(f"  \\item[{abbr_safe}] {body}{cjk_note}")
    out.append("\\end{description}")
    return "\n".join(out) + "\n"


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    (TEX_DIR / "bibliography").mkdir(parents=True, exist_ok=True)
    (TEX_DIR / "backmatter").mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    bib_b = parse_bibliography_b()
    bib_a = parse_bibliography_a()

    # bibliography_raw.tsv (Bib B sub-entries)
    raw_tsv = DATA_DIR / "bibliography_raw.tsv"
    with raw_tsv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["scan", "author", "author_cjk", "author_role",
                    "year", "suffix", "body_tesseract", "gv_title", "gv_cjk"])
        for e in bib_b:
            w.writerow([
                e["scan"], e["author"], e["author_cjk"], e["author_role"],
                e["year"], e["suffix"], " ".join(e["body_lines"]),
                e.get("gv_title", ""), e.get("gv_cjk", ""),
            ])

    bib_text = emit_bib(bib_b)
    (TEX_DIR / "bibliography" / "keightley.bib").write_text(bib_text, encoding="utf-8")

    # Bibliography A
    yml = emit_abbreviations_yml(bib_a)
    (DATA_DIR / "abbreviations.yml").write_text(yml, encoding="utf-8")
    abbr_tex = emit_abbreviations_tex(bib_a)
    (TEX_DIR / "backmatter" / "abbreviations.tex").write_text(abbr_tex, encoding="utf-8")

    # QA / log
    log_lines = [
        "# Phase 5 — Bibliography extraction",
        "",
        f"- Bibliography B sub-entries parsed: {len(bib_b)}",
        f"- Bibliography A abbreviations parsed: {len(bib_a)}",
        f"- Output bib file: tex/bibliography/keightley.bib",
        f"- Output abbreviations: data/abbreviations.yml + tex/backmatter/abbreviations.tex",
        "",
        "## Authors detected (Bib B)",
        "",
    ]
    seen_authors: dict[str, int] = {}
    for e in bib_b:
        seen_authors[e["author"]] = seen_authors.get(e["author"], 0) + 1
    for name, n in sorted(seen_authors.items()):
        log_lines.append(f"- {name}: {n} entr{'y' if n == 1 else 'ies'}")
    (LOG_DIR / "phase5_bibliography.md").write_text("\n".join(log_lines) + "\n",
                                                    encoding="utf-8")

    print(f"bibliography B sub-entries: {len(bib_b)}")
    print(f"bibliography A abbreviations: {len(bib_a)}")
    print(f"distinct authors (Bib B): {len(seen_authors)}")


if __name__ == "__main__":
    main()
