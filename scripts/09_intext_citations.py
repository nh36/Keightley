#!/usr/bin/env python3
"""Phase 5 step C: scan tex/ for `Surname (YYYY)` style in-text citations.

For every match we emit one row of `data/citations.tsv` carrying the file,
line-number, raw match, candidate biblatex key (best-match from
`tex/bibliography/keightley.bib`), and a confidence score.

We do NOT rewrite the .tex files.  The conservative replacement pass is left
for Phase 11 proofing — the brief explicitly warns against damaging readability
during automated conversion.

The companion file `build/qa/unmatched_citations.tsv` lists matches with no
unique candidate.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX_DIR = ROOT / "tex"
DATA_DIR = ROOT / "data"
QA_DIR = ROOT / "build" / "qa"
BIB_FILE = TEX_DIR / "bibliography" / "keightley.bib"

CITATION_RE = re.compile(
    r"""(?P<surname>[A-Z][A-Za-z'\-]+(?:\s+(?:and|et\s+al\.?)\s+[A-Z][A-Za-z'\-]+)?)
        \s*
        \(
        (?P<year>(?:18|19|20)\d{2})(?P<suffix>[a-z]?)
        \)
        (?:\s*,?\s*pp?\.\s*(?P<pages>[\d\s,–\-]+))?
    """,
    re.VERBOSE,
)
KEY_RE = re.compile(r"^@\w+\{(?P<key>[^,]+),", re.MULTILINE)
BIB_AUTHOR_RE = re.compile(
    r"^@(?P<type>\w+)\{(?P<key>[^,]+),"
    r"(?:[^@]*?\bauthor\s*=\s*\{(?P<author>[^}]*)\})?"
    r"(?:[^@]*?\beditor\s*=\s*\{(?P<editor>[^}]*)\})?"
    r"[^@]*?\byear\s*=\s*\{(?P<year>\d{4})\}",
    re.MULTILINE | re.DOTALL,
)


def load_bib_index() -> list[dict]:
    """Return a list of {key, surname, year, suffix} dicts from the .bib."""
    if not BIB_FILE.exists():
        return []
    text = BIB_FILE.read_text(encoding="utf-8")
    out = []
    for m in BIB_AUTHOR_RE.finditer(text):
        author = (m.group("author") or m.group("editor") or "").strip()
        if not author:
            continue
        surname = re.split(r"[ ,]", author.strip())[0]
        key = m.group("key")
        # Year suffix is encoded in the key tail (e.g., Akatsuka1955a)
        suffix = ""
        ks = re.match(r"^[A-Za-z]+\d{4}([a-z])", key)
        if ks:
            suffix = ks.group(1)
        out.append({
            "key": key, "surname": surname, "year": m.group("year"),
            "suffix": suffix, "author": author,
        })
    return out


def find_candidates(bib: list[dict], surname: str, year: str,
                    suffix: str) -> list[dict]:
    sl = surname.lower()
    results = []
    for e in bib:
        if e["year"] != year:
            continue
        if suffix and e["suffix"] != suffix:
            continue
        es = e["surname"].lower()
        if es == sl:
            results.append((0, e))
        elif es.startswith(sl) or sl.startswith(es):
            results.append((1, e))
        elif sl in e["author"].lower():
            results.append((2, e))
    results.sort(key=lambda x: x[0])
    return [r[1] for r in results]


def main() -> None:
    bib = load_bib_index()
    QA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    matched_rows = []
    unmatched_rows = []
    for tex in sorted(TEX_DIR.rglob("*.tex")):
        if tex.name.startswith(".") or "bibliography" in tex.parts:
            continue
        text = tex.read_text(encoding="utf-8")
        for line_num, line in enumerate(text.splitlines(), start=1):
            for m in CITATION_RE.finditer(line):
                surname = m.group("surname")
                year = m.group("year")
                suffix = m.group("suffix") or ""
                pages = (m.group("pages") or "").strip()
                cands = find_candidates(bib, surname, year, suffix)
                row = {
                    "file": str(tex.relative_to(ROOT)),
                    "line": line_num,
                    "raw": m.group(0).replace("\t", " "),
                    "surname": surname,
                    "year": year + suffix,
                    "pages": pages,
                    "candidate_count": len(cands),
                    "candidate_key": cands[0]["key"] if cands else "",
                }
                if len(cands) == 1:
                    matched_rows.append(row)
                else:
                    unmatched_rows.append(row)

    fields = ["file", "line", "raw", "surname", "year", "pages",
              "candidate_count", "candidate_key"]

    citations_tsv = DATA_DIR / "citations.tsv"
    with citations_tsv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t",
                           lineterminator="\n")
        w.writeheader()
        for r in matched_rows:
            w.writerow(r)

    unmatched_tsv = QA_DIR / "unmatched_citations.tsv"
    with unmatched_tsv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t",
                           lineterminator="\n")
        w.writeheader()
        for r in unmatched_rows:
            w.writerow(r)

    print(f"matched 1:1 in-text citations: {len(matched_rows)}")
    print(f"ambiguous / unmatched          : {len(unmatched_rows)}")
    print(f"bib entries indexed             : {len(bib)}")


if __name__ == "__main__":
    main()
