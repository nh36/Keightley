#!/usr/bin/env python3
"""Phase 3: Structural segmentation — emit a LaTeX skeleton.

Reads:
  data/pages.csv                    (scan → printed → section assignment)
  data/toc.yml                      (26 section anchors)
  build/ocr/cleaned/p_NNNN.md       (Phase 2 cleaned, page-anchored markdown)

Writes:
  tex/preamble.tex                  (xelatex + biblatex skeleton + \\origsecnum macro)
  tex/main.tex                      (root document; \\input{...} per unit)
  tex/frontmatter/*.tex             (halftitle, title, copyright, dedication, ...)
  tex/chapters/ch01.tex .. ch05.tex
  tex/appendices/app01.tex .. app05.tex
  tex/plates/{figures,tables}.tex   (stubs; real content rebuilt in Phases 7-8)
  tex/backmatter/{biblio_a,biblio_b,finding_list,index}.tex
  build/qa/structure_inventory.tsv  (per-emitted-heading audit row)
  build/logs/phase3_emit.md         (what was generated, with counts)

Body conversion is intentionally minimal:
  - Source page comments preserved as `% source: scan NNN, printed PPP`.
  - LaTeX special characters escaped (& % $ # _ { } ~ ^ and bare \\).
  - `<!-- CJK -->` markers dropped (CJK glyphs themselves are kept verbatim
    for xelatex to render once a CJK font is configured in Phase 10).
  - `<!-- CHECK OCR: ... -->` markers preserved as LaTeX `% TODO ...` lines.
  - Numbered headings X.Y / X.Y.Z / X.Y.Z.W → \\section / \\subsection /
    \\subsubsection, with `\\origsecnum{X.Y}` printed before the title and a
    label `\\label{sec:CHAPTER:X.Y}`.

Footnotes (Phase 4), bibliography citations (Phase 5), and Wade-Giles → Pinyin
(Phase 6) are deliberately deferred. Body text is preserved verbatim with all
its OCR-era footnote-marker characters and (Author Year) citation strings.
"""
from __future__ import annotations

import csv
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES_CSV = ROOT / "data" / "pages.csv"
CLEAN_DIR = ROOT / "build" / "ocr" / os.environ.get("OUT_DIR", "cleaned_with_notes")
if not CLEAN_DIR.exists():
    CLEAN_DIR = ROOT / "build" / "ocr" / "cleaned"
TEX_DIR = ROOT / "tex"
INVENTORY = ROOT / "build" / "qa" / "structure_inventory.tsv"
EMIT_LOG = ROOT / "build" / "logs" / "phase3_emit.md"


# Canonical chapter / appendix / front-back unit titles. Source: the printed
# Contents (scan pages 7-9), supplemented by the chapter first-page heads.
# These are deliberately authoritative — auto-detection from OCR first pages
# is unreliable when first pages carry edge garbage (chapter 5, appendix 1).
UNITS: dict[str, dict] = {
    "frontmatter/half-title":            {"file": "frontmatter/halftitle.tex",       "kind": "verbatim"},
    "frontmatter/title":                 {"file": "frontmatter/title.tex",           "kind": "verbatim"},
    "frontmatter/copyright":             {"file": "frontmatter/copyright.tex",       "kind": "verbatim"},
    "frontmatter/dedication":            {"file": "frontmatter/dedication.tex",      "kind": "verbatim"},
    "frontmatter/epigraph":              {"file": "frontmatter/epigraph.tex",        "kind": "verbatim"},
    "frontmatter/contents":              {"file": "frontmatter/contents.tex",        "kind": "stub",
                                          "stub_note": "rebuilt by \\tableofcontents in Phase 10"},
    "frontmatter/list-of-figures-tables":{"file": "frontmatter/list-figures-tables.tex","kind": "stub",
                                          "stub_note": "rebuilt by \\listoffigures and \\listoftables in Phase 10"},
    "frontmatter/abbreviations":         {"file": "frontmatter/abbreviations.tex",   "kind": "verbatim"},
    "frontmatter/preface":               {"file": "frontmatter/preface.tex",         "kind": "named",
                                          "title": "Preface", "label": "fm:preface", "level": "chapter*"},
    "frontmatter/preamble":              {"file": "frontmatter/book-preamble.tex",   "kind": "named",
                                          "title": "Preamble", "label": "fm:preamble", "level": "chapter*"},
    "chapter/1": {"file": "chapters/ch01.tex", "kind": "chapter", "number": 1,
                  "title": "Shang Divination Procedures", "label": "ch:1"},
    "chapter/2": {"file": "chapters/ch02.tex", "kind": "chapter", "number": 2,
                  "title": "The Divination Inscriptions", "label": "ch:2"},
    "chapter/3": {"file": "chapters/ch03.tex", "kind": "chapter", "number": 3,
                  "title": "Deciphering the Inscriptions", "label": "ch:3"},
    "chapter/4": {"file": "chapters/ch04.tex", "kind": "chapter", "number": 4,
                  "title": "Dating the Inscriptions: Relative Chronology", "label": "ch:4"},
    "chapter/5": {"file": "chapters/ch05.tex", "kind": "chapter", "number": 5,
                  "title": "The Oracle-Bone Inscriptions as Historical Sources", "label": "ch:5"},
    "appendix/1": {"file": "appendices/app01.tex", "kind": "appendix", "letter": "1",
                   "title": "Identification of the Inscribed Turtle Shells of Shang",
                   "byline": "James F. Berry",  "label": "app:1"},
    "appendix/2": {"file": "appendices/app02.tex", "kind": "appendix", "letter": "2",
                   "title": "The Ratio of Scapulas to Plastrons", "label": "app:2"},
    "appendix/3": {"file": "appendices/app03.tex", "kind": "appendix", "letter": "3",
                   "title": "The Size of the Sample", "label": "app:3"},
    "appendix/4": {"file": "appendices/app04.tex", "kind": "appendix", "letter": "4",
                   "title": "Absolute Chronology: A Brief Note", "label": "app:4"},
    "appendix/5": {"file": "appendices/app05.tex", "kind": "appendix", "letter": "5",
                   "title": "Relative Chronology: The Periodicity of Divination Topics and Idioms",
                   "label": "app:5"},
    "plates/figures": {"file": "plates/figures.tex", "kind": "stub",
                       "stub_note": "regenerated in Phase 7 (figures pipeline)"},
    "plates/tables":  {"file": "plates/tables.tex",  "kind": "stub",
                       "stub_note": "regenerated in Phase 8 (tables pipeline)"},
    "backmatter/bibliography-a": {"file": "backmatter/biblio_a.tex", "kind": "stub",
                                  "stub_note": "regenerated in Phase 5 (biblio reconstruction)"},
    "backmatter/bibliography-b": {"file": "backmatter/biblio_b.tex", "kind": "stub",
                                  "stub_note": "regenerated in Phase 5 (biblio reconstruction)"},
    "backmatter/finding-list":   {"file": "backmatter/finding_list.tex", "kind": "stub",
                                  "stub_note": "regenerated in Phase 9"},
    "backmatter/index":          {"file": "backmatter/index.tex",        "kind": "stub",
                                  "stub_note": "regenerated by makeindex in Phase 9"},
}


HEADING_RE = re.compile(r"^(\d+(?:\.\d+){1,3})\s+([^\n]{2,160})$", re.MULTILINE)
COMMENT_OPEN_RE = re.compile(r"<!--\s*(.+?)\s*-->")
SOURCE_HDR_RE = re.compile(r"<!--\s*source:\s*scan p\.\s*(\d+),\s*printed p\.\s*([^,]+),\s*section:\s*([^ ]+)\s*-->")
PAGE_NUM_LINE_RE = re.compile(r"^\s*\d{1,3}\s*$")


def latex_escape(s: str) -> str:
    """Escape LaTeX-special characters in plain prose."""
    # Order matters: escape backslash first, then the rest.
    out = []
    for ch in s:
        if ch == "\\":
            out.append(r"\textbackslash{}")
        elif ch in "&%$#_{}":
            out.append("\\" + ch)
        elif ch == "~":
            out.append(r"\textasciitilde{}")
        elif ch == "^":
            out.append(r"\textasciicircum{}")
        else:
            out.append(ch)
    return "".join(out)


def parse_page(md: str) -> dict:
    """Return a dict with the page header info and the body text (with all
    intra-page <!-- ... --> comments processed)."""
    out = {"scan": None, "printed": None, "section": None,
           "running_head": None, "edge_dropped": 0, "body": ""}
    lines = md.splitlines()
    body_start = 0
    for i, ln in enumerate(lines):
        m = SOURCE_HDR_RE.match(ln.strip())
        if m:
            out["scan"] = int(m.group(1))
            out["printed"] = m.group(2).strip()
            out["section"] = m.group(3).strip()
            body_start = i + 1
            continue
        cm = COMMENT_OPEN_RE.match(ln.strip())
        if cm:
            txt = cm.group(1)
            if txt.startswith("running-head-removed:"):
                out["running_head"] = txt.split(":", 1)[1].strip().strip("'\"")
                body_start = i + 1
            elif txt.startswith("edge-lines-dropped:"):
                try:
                    out["edge_dropped"] = int(txt.split(":", 1)[1].strip())
                except ValueError:
                    pass
                body_start = i + 1
            else:
                # Phase 6: Skip all leading metadata comments (substrate, cjk-tess-overlay, etc.)
                # These should not appear in the body. Only keep comments that appear
                # mid-body (CJK, CHECK-OCR, FOOTNOTE).
                body_start = i + 1
        # First non-comment, non-blank line is start of body
        if ln.strip() and not cm:
            break
    body = "\n".join(lines[body_start:]).strip("\n")
    out["body"] = body
    return out


FOOTNOTE_RE = re.compile(
    r"<!--\s*FOOTNOTE(?:-UNANCHORED)?:(\d+)\s*-->(.*?)<!--\s*/FOOTNOTE\s*-->",
    re.DOTALL,
)


def process_body_text(body: str) -> str:
    """Convert page body markdown to LaTeX-ready text:
       - drop <!-- CJK --> markers (keep CJK chars themselves)
       - convert <!-- CHECK OCR: ... --> to `% TODO CHECK OCR: ...` lines
       - convert <!-- FOOTNOTE:N -->...<!-- /FOOTNOTE --> to a sentinel
         that emit_chapter() unfolds into \\footnote{...}
       - escape LaTeX specials
       - drop bare-page-number residue lines
       - drop any remaining HTML comments (phase 6 safeguard)
       Headings are preserved as-is so emit_chapter() can find them.
    """
    body = re.sub(r"\s*<!--\s*CJK\s*-->\s*", "", body)

    def check_repl(m: re.Match) -> str:
        return f"\n% TODO CHECK OCR: {m.group(1)}\n"
    body = re.sub(r"<!--\s*CHECK OCR:\s*(.+?)\s*-->", check_repl, body)

    # Replace FOOTNOTE sentinels with @@FOOTNOTE@@N@@TYPE@@BODY@@/FOOTNOTE@@
    # marker. Detect "UNANCHORED" by re-checking the source spelling.
    def fn_repl(m: re.Match) -> str:
        is_unanchored = m.group(0).startswith("<!-- FOOTNOTE-UNANCHORED")
        n = m.group(1)
        body_txt = m.group(2).strip()
        kind = "U" if is_unanchored else "A"
        # Encode body for safe carry-through escape: replace "@" with placeholder
        encoded = body_txt.replace("@", "\u0001AT\u0001")
        return f"@@FOOTNOTE@@{n}@@{kind}@@{encoded}@@/FOOTNOTE@@"
    body = FOOTNOTE_RE.sub(fn_repl, body)

    # Phase 6: Drop any remaining HTML comments (e.g., substrate, cjk-tess-overlay)
    # that weren't caught by parse_page. These should not appear in LaTeX output.
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)

    # Drop bare-page-number lines that survived edge-strip
    out_lines = []
    for ln in body.splitlines():
        if PAGE_NUM_LINE_RE.match(ln) and len(ln.strip()) <= 3:
            continue
        out_lines.append(ln)
    body = "\n".join(out_lines)

    # Escape, but preserve heading and footnote markers.
    # Strategy: find all heading + footnote spans, escape only the gaps.
    # IMPORTANT: footnote bodies may contain heading-like patterns
    # (e.g., note 43 in ch1 contains "4.54.4 and 4.54.5..."). Headings
    # inside footnote spans must be ignored.
    fn_spans: list[tuple[int, int, str]] = []
    for m in re.finditer(r"@@FOOTNOTE@@(\d+)@@([AU])@@(.*?)@@/FOOTNOTE@@", body, re.DOTALL):
        decoded = m.group(3).replace("\u0001AT\u0001", "@")
        esc_body = latex_escape(decoded)
        repl = f"@@FN@@{m.group(1)}@@{m.group(2)}@@{esc_body}@@/FN@@"
        fn_spans.append((m.start(), m.end(), repl))

    def _inside_fn(pos: int) -> bool:
        for s, e, _ in fn_spans:
            if s <= pos < e:
                return True
        return False

    spans: list[tuple[int, int, str]] = list(fn_spans)
    for m in HEADING_RE.finditer(body):
        if _inside_fn(m.start()):
            continue
        repl = f"@@HEADING@@{m.group(1)}@@{latex_escape(m.group(2).rstrip(' .'))}@@"
        spans.append((m.start(), m.end(), repl))
    spans.sort()

    parts: list[str] = []
    pos = 0
    for s, e, repl in spans:
        parts.append(latex_escape(body[pos:s]))
        parts.append(repl)
        pos = e
    parts.append(latex_escape(body[pos:]))
    return "".join(parts)


FN_MARKER_RE = re.compile(r"@@FN@@(\d+)@@([AU])@@(.*?)@@/FN@@", re.DOTALL)


def expand_footnotes(text: str, count: list[int] | None = None) -> str:
    """Replace @@FN@@N@@A|U@@body@@/FN@@ sentinels with LaTeX footnote calls.

    For 'A' (anchored): emit \\footnote[N]{body}.
    For 'U' (unanchored): emit \\footnote[N]{body}\\unanchorednote{N} so the
      audit comment is visible in the source. The visible result in the PDF
      is identical to anchored (\\footnote[N]{}); only the audit-marker comment
      differs so a reader can tell which footnotes lack a confirmed in-text
      anchor and may sit at a non-ideal position.
    """
    def repl(m: re.Match) -> str:
        n = m.group(1)
        kind = m.group(2)
        body = m.group(3).strip()
        if count is not None:
            count[0 if kind == "A" else 1] += 1
        if kind == "A":
            return f"\\footnote[{n}]{{{body}}}"
        else:
            return f"\\footnote[{n}]{{{body}}}% phase4: unanchored note {n}\n"
    return FN_MARKER_RE.sub(repl, text)


def collapse_paragraphs(s: str) -> str:
    """Collapse runs of >2 newlines, drop trailing whitespace per line."""
    s = "\n".join(ln.rstrip() for ln in s.splitlines())
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip() + "\n"


def emit_unit_header(unit: dict, page_range: tuple[int, int]) -> str:
    a, b = page_range
    return (
        f"% Auto-generated by scripts/06_emit_structure.py\n"
        f"% Source: scans {a:03d}–{b:03d}\n"
        f"% Section id: {unit.get('id')}\n"
        f"% Phase 3 deliverable. Footnotes (Phase 4), citations (Phase 5),\n"
        f"% and Wade-Giles → Pinyin (Phase 6) are not yet applied here.\n"
    )


def emit_verbatim(unit: dict, pages: list[dict], inventory: list[dict]) -> str:
    body = []
    body.append(emit_unit_header(unit, (pages[0]["scan"], pages[-1]["scan"])))
    for p in pages:
        body.append(f"\n% source: scan {p['scan']:03d}, printed {p['printed']}\n")
        body.append(collapse_paragraphs(process_body_text(p["body"]).replace("@@HEADING@@", "% HEADING@@").replace("@@", "@@")))
    inventory.append({"unit": unit["id"], "kind": "verbatim", "scan_first": pages[0]["scan"],
                      "scan_last": pages[-1]["scan"], "headings": 0})
    return "".join(body)


def emit_named(unit: dict, pages: list[dict], inventory: list[dict]) -> str:
    """Preface / Preamble: titled but unnumbered."""
    body = [emit_unit_header(unit, (pages[0]["scan"], pages[-1]["scan"]))]
    title = unit["title"]
    label = unit["label"]
    level = unit.get("level", "chapter*")
    body.append(f"\n\\{level}{{{title}}}\n\\label{{{label}}}\n\n")
    for p in pages:
        body.append(f"% source: scan {p['scan']:03d}, printed {p['printed']}\n")
        text = process_body_text(p["body"])
        # Strip a leading title echo ("Preface" / "Preamble" on first page)
        first_line = text.split("\n", 1)[0].strip()
        if first_line.lower() == title.lower():
            text = text.split("\n", 1)[1] if "\n" in text else ""
        body.append(collapse_paragraphs(text))
        body.append("\n")
    inventory.append({"unit": unit["id"], "kind": "named", "scan_first": pages[0]["scan"],
                      "scan_last": pages[-1]["scan"], "headings": 0})
    return "".join(body)


def strip_chapter_intro(first_page_body: str, unit: dict) -> tuple[str, list[str]]:
    """Strip leading title-echo and OCR-junk lines from a chapter's first page,
    up to the first numbered heading or first plausible prose paragraph.

    Returns (cleaned_body, dropped_lines) so the dropped lines can be retained
    as audit comments in the LaTeX output.
    """
    title_words = set(re.findall(r"[A-Za-z]+", unit["title"].lower()))
    # Only treat *short* head lines (<= 3 words) as candidate echoes; never
    # consume real prose paragraphs that happen to share vocabulary.
    intro_pat = re.compile(r"^(CHAPTER|APPENDIX)\s+[IVX0-9]+\.?$", re.IGNORECASE)
    dropped: list[str] = []
    lines = first_page_body.splitlines()
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        # Stop if we hit a numbered heading marker (already encoded as @@HEADING@@)
        if s.startswith("@@HEADING@@") or re.match(r"^\d+\.\d+", s):
            break
        words = re.findall(r"[A-Za-z]+", s)
        # Heuristic 1: "CHAPTER N" / "APPENDIX N" line
        if intro_pat.match(s):
            dropped.append(s); i += 1; continue
        # Heuristic 2: short line whose words are all in the chapter title
        if 0 < len(words) <= 4 and all(w.lower() in title_words for w in words):
            dropped.append(s); i += 1; continue
        # Heuristic 3: low-alpha junk (figure-stub OCR debris)
        alpha = sum(1 for ch in s if "a" <= ch.lower() <= "z")
        if len(s) >= 3 and alpha / len(s) < 0.4:
            dropped.append(s); i += 1; continue
        # Heuristic 4: very short alpha line (1-2 chars) — junk
        if len(s) <= 2:
            dropped.append(s); i += 1; continue
        break
    return "\n".join(lines[i:]), dropped


def emit_chapter(unit: dict, pages: list[dict], inventory: list[dict]) -> str:
    """Chapter / appendix with numbered subsections."""
    is_appendix = unit["kind"] == "appendix"
    out = [emit_unit_header(unit, (pages[0]["scan"], pages[-1]["scan"]))]
    title = unit["title"]
    label = unit["label"]
    if is_appendix:
        # Title already includes subtitle. Prefix appendix letter.
        letter = unit["letter"]
        out.append(f"\n\\chapter{{{title}}}\n\\label{{{label}}}\n")
        if "byline" in unit:
            out.append(f"\\authorbyline{{{unit['byline']}}}\n")
    else:
        out.append(f"\n\\chapter{{{title}}}\n\\label{{{label}}}\n")
    out.append("\n")

    # Concatenate processed page bodies with page-anchor comments.
    chunks: list[str] = []
    for idx, p in enumerate(pages):
        chunks.append(f"% source: scan {p['scan']:03d}, printed {p['printed']}")
        text = process_body_text(p["body"])
        if idx == 0:
            text, dropped = strip_chapter_intro(text, unit)
            for d in dropped:
                chunks.append(f"% intro-echo-dropped: {d}")
        chunks.append(text)
    full = "\n".join(chunks)

    # Now split on heading markers and emit them at the right level.
    # @@HEADING@@N.M[.O[.P]]@@TITLE@@
    head_re = re.compile(r"@@HEADING@@(\d+(?:\.\d+){1,3})@@(.+?)@@")
    out_text = []
    pos = 0
    headings_emitted = 0

    # Determine the chapter prefix expected (e.g. chapter 1 → headings start with "1.")
    if not is_appendix:
        chapter_prefix = f"{unit['number']}."
    else:
        # Appendices: most have "1.", "2." numbering inside (per scan 178, 182, 188).
        # Treat any depth-1 heading as a section.
        chapter_prefix = None

    for m in head_re.finditer(full):
        out_text.append(full[pos:m.start()])
        pos = m.end()
        num = m.group(1)
        htitle = m.group(2)
        depth = num.count(".")
        # Filter: skip ALL-CAPS heading echoes (running heads from later pages
        # that survived stripping).
        letters_only = re.sub(r"[^A-Za-z]", "", htitle)
        if letters_only and letters_only.upper() == letters_only and len(letters_only) > 4:
            # ALL CAPS — likely a running head; keep as a comment for audit.
            out_text.append(f"% running-head-echo: {num} {htitle}\n")
            continue
        # For chapters, ignore any heading whose number doesn't begin with our prefix
        # (defensive: catches OCR mis-segmented page numbers like "134" or "1.6"
        # appearing in the middle of chapter 4 due to a stray running head).
        if chapter_prefix and not num.startswith(chapter_prefix):
            out_text.append(f"% out-of-scope-heading: {num} {htitle}\n")
            continue
        # Emit heading
        cmd = {1: "section", 2: "subsection", 3: "subsubsection"}[depth]
        sec_label = f"sec:{unit['file'].replace('/', '-').replace('.tex', '')}:{num}"
        out_text.append(
            f"\n\n\\{cmd}[{htitle}]"
            f"{{\\origsecnum{{{num}}}{htitle}}}\n"
            f"\\label{{{sec_label}}}\n\n"
        )
        headings_emitted += 1
    out_text.append(full[pos:])

    body_str = "".join(out_text)
    body_str = collapse_paragraphs(body_str)
    out.append(body_str)

    inventory.append({"unit": unit["id"], "kind": unit["kind"],
                      "scan_first": pages[0]["scan"], "scan_last": pages[-1]["scan"],
                      "headings": headings_emitted})
    return "".join(out)


def emit_stub(unit: dict, pages: list[dict], inventory: list[dict]) -> str:
    note = unit.get("stub_note", "")
    out = [emit_unit_header(unit, (pages[0]["scan"], pages[-1]["scan"]))]
    out.append(f"\n% STUB — {note}\n\n")
    for p in pages:
        out.append(f"% source: scan {p['scan']:03d}, printed {p['printed']}\n")
    inventory.append({"unit": unit["id"], "kind": "stub",
                      "scan_first": pages[0]["scan"], "scan_last": pages[-1]["scan"], "headings": 0})
    return "".join(out)


PREAMBLE_TEX = r"""% Auto-generated by scripts/06_emit_structure.py — Phase 3.
% This is a minimal placeholder. Phase 10 (LaTeX assembly) will refine it.
\documentclass[11pt,a4paper]{book}

\usepackage{fontspec}
\usepackage{xunicode}
\usepackage{xeCJK}
% Noto Serif CJK SC ships glyph coverage across Simplified, Traditional, JP, KR
% — single font avoids missing-glyph issues with simplified-only fonts.
\setCJKmainfont{Noto Serif CJK SC}
\usepackage{polyglossia}
\setdefaultlanguage{english}
\usepackage{microtype}
\usepackage[margin=1in]{geometry}
\usepackage[backend=biber,style=authoryear,natbib]{biblatex}
\usepackage{csquotes}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{makeidx}
\makeindex

% Phase 3 macros
\newcommand{\origsecnum}[1]{\textup{#1}\quad}
\newcommand{\authorbyline}[1]{\par\noindent\emph{by #1}\par\bigskip}
\newcommand{\ednote}[1]{\textsuperscript{[#1]}}

% Bibliography (Phase 5)
\addbibresource{bibliography/keightley.bib}
"""


def emit_main_tex() -> str:
    out = [r"% Auto-generated by scripts/06_emit_structure.py — Phase 3.",
           r"% Root document; \input{} order matches the printed book.",
           r"\frontmatter"]
    fm_order = [
        "frontmatter/half-title", "frontmatter/title", "frontmatter/copyright",
        "frontmatter/dedication", "frontmatter/epigraph", "frontmatter/contents",
        "frontmatter/list-of-figures-tables", "frontmatter/abbreviations",
        "frontmatter/preface", "frontmatter/preamble",
    ]
    for s in fm_order:
        f = UNITS[s]["file"]
        out.append(f"\\input{{{f.replace('.tex','')}}}")
    out.append(r"\mainmatter")
    for n in range(1, 6):
        out.append(f"\\input{{chapters/ch{n:02d}}}")
    out.append(r"\appendix")
    for n in range(1, 6):
        out.append(f"\\input{{appendices/app{n:02d}}}")
    out.append(r"\backmatter")
    out.append(r"\input{plates/figures}")
    out.append(r"\input{plates/tables}")
    out.append(r"\input{backmatter/biblio_a}")
    out.append(r"\input{backmatter/biblio_b}")
    out.append(r"\input{backmatter/finding_list}")
    out.append(r"\input{backmatter/index}")
    return "\n".join(out) + "\n"


def main() -> int:
    rows = list(csv.DictReader(PAGES_CSV.open()))
    sec_to_pages: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        scan = int(r["scan_page"])
        md = (CLEAN_DIR / f"p_{scan:04d}.md").read_text(errors="replace")
        page = parse_page(md)
        sec_to_pages[r["section"]].append(page)

    # Make sure all 26 sections in UNITS are present.
    missing = [k for k in UNITS if k not in sec_to_pages]
    if missing:
        sys.exit(f"missing pages for sections: {missing}")
    extra = [k for k in sec_to_pages if k not in UNITS]
    if extra:
        sys.exit(f"unknown sections in pages.csv: {extra}")

    TEX_DIR.mkdir(parents=True, exist_ok=True)
    inventory: list[dict] = []
    files_written: list[str] = []

    for sec_id, unit_def in UNITS.items():
        unit = {**unit_def, "id": sec_id}
        pages = sec_to_pages[sec_id]
        if unit["kind"] == "verbatim":
            text = emit_verbatim(unit, pages, inventory)
        elif unit["kind"] == "named":
            text = emit_named(unit, pages, inventory)
        elif unit["kind"] in ("chapter", "appendix"):
            text = emit_chapter(unit, pages, inventory)
        elif unit["kind"] == "stub":
            text = emit_stub(unit, pages, inventory)
        else:
            sys.exit(f"unknown unit kind {unit['kind']!r} for {sec_id}")
        out_path = TEX_DIR / unit["file"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fn_count = [0, 0]  # [anchored, unanchored]
        text = expand_footnotes(text, fn_count)
        if fn_count[0] or fn_count[1]:
            for r in inventory:
                if r["unit"] == sec_id:
                    r["footnotes_anchored"] = fn_count[0]
                    r["footnotes_unanchored"] = fn_count[1]
                    break
        out_path.write_text(text)
        files_written.append(str(out_path.relative_to(ROOT)))

    # Preamble + main
    (TEX_DIR / "preamble.tex").write_text(PREAMBLE_TEX)
    (TEX_DIR / "main_body.tex").write_text(emit_main_tex())
    # main.tex hosts the document environment; preamble.tex is preamble-only
    (TEX_DIR / "main.tex").write_text(
        "% Auto-generated by scripts/06_emit_structure.py — Phase 3.\n"
        "% Root document.  Preamble in preamble.tex; body in main_body.tex.\n"
        "\\input{preamble}\n\n"
        "\\begin{document}\n"
        "\\input{main_body}\n"
        "\\printindex\n"
        "\\end{document}\n"
    )
    files_written.extend(["tex/preamble.tex", "tex/main_body.tex", "tex/main.tex"])

    # Inventory
    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    with INVENTORY.open("w", newline="") as f:
        fieldnames = []
        for r in inventory:
            for k in r.keys():
                if k not in fieldnames:
                    fieldnames.append(k)
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        w.writerows(inventory)

    # Log
    log = ["# Phase 3 emit log", "",
           f"Wrote {len(files_written)} files under `tex/`. "
           f"Per-unit heading counts in `build/qa/structure_inventory.tsv`.", ""]
    log.append("| unit | kind | scans | headings |")
    log.append("|------|------|-------|----------|")
    for r in inventory:
        log.append(f"| {r['unit']} | {r['kind']} | "
                   f"{r['scan_first']:03d}–{r['scan_last']:03d} | {r['headings']} |")
    EMIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    EMIT_LOG.write_text("\n".join(log) + "\n")

    print(f"emitted {len(files_written)} tex files; "
          f"{sum(r['headings'] for r in inventory)} numbered headings; "
          f"inventory: {INVENTORY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
