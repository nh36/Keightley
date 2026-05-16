#!/usr/bin/env python3
"""Phase 5 step C: scan tex/ for `Surname (YYYY)` style in-text citations.

For every match we emit one row of `data/citations.tsv` carrying the file,
line-number, raw match, candidate biblatex key (best-match from the
`tex/bibliography/*.bib` resources), and a confidence score.

We do NOT rewrite the .tex files.  The conservative replacement pass is left
for Phase 11 proofing — the brief explicitly warns against damaging readability
during automated conversion.

The companion file `build/qa/unmatched_citations.tsv` lists matches with no
unique candidate.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX_DIR = ROOT / "tex"
DATA_DIR = ROOT / "data"
QA_DIR = ROOT / "build" / "qa"
BIB_DIR = TEX_DIR / "bibliography"
PINYIN_TERMS_TSV = DATA_DIR / "pinyin_terms.tsv"
PAGE_PATTERN = (
    r"\d+[A-Za-z]?"
    r"(?:\s*[-–]+\s*\d+[A-Za-z]?)?"
    r"(?:\s*,\s*\d+[A-Za-z]?(?:\s*[-–]+\s*\d+[A-Za-z]?)?)*"
)

CITATION_RE = re.compile(
    rf"""(?P<surname>[A-Z][A-Za-z'\-]+(?:\s+(?:(?:and|et\s+al\.?)\s+)?[A-Z][A-Za-z'\-]+)*)
         \s*
         \(
         (?P<year>(?:18|19|20)\d{{2}})(?P<suffix>[a-z]?)
         \)
         (?:\s*,?\s*pp?\.\s*(?P<pages>{PAGE_PATTERN}))?
     """,
    re.VERBOSE,
)
PINYINTERM_CITATION_RE = re.compile(
    rf"""\\pinyinterm\{{(?P<term_key>[^}}]+)\}}
         \s*
         \(
         (?P<year>(?:18|19|20)\d{{2}})(?P<suffix>[a-z]?)
         \)
         (?:\s*,?\s*(?:\d+(?:\.\d+)?,\s*)?pp?\.\s*(?P<pages>{PAGE_PATTERN}))?
     """,
    re.VERBOSE,
)
PINYINTERM_BRACKETED_CITATION_RE = re.compile(
    rf"""\\pinyinterm\{{(?P<term_key>[^}}]+)\}}
         \s*
         (?:\(\[(?P<year_in_parens>(?:18|19|20)\d{{2}})(?P<suffix_in_parens>[a-z]?)\]
           |\[(?P<year_bracketed>(?:18|19|20)\d{{2}})(?P<suffix_bracketed>[a-z]?)\])
         (?:\s*,?\s*(?:\d+(?:\.\d+)?,\s*)?pp?\.\s*(?P<pages>{PAGE_PATTERN}))?
     """,
    re.VERBOSE,
)
KEY_RE = re.compile(r"^@\w+\{(?P<key>[^,]+),", re.MULTILINE)
ENTRY_RE = re.compile(
    r"^@(?P<type>\w+)\{(?P<key>[^,]+),(?P<body>.*?)^}\s*$",
    re.MULTILINE | re.DOTALL,
)
PAGE_FRAGMENT_RE = re.compile(
    r"^\s*("
    r"[0-9A-Za-z]+(?:\s*[-–]+\s*[0-9A-Za-z]+)?"
    r"(?:\s*,\s*[0-9A-Za-z]+(?:\s*[-–]+\s*[0-9A-Za-z]+)?)*"
    r")"
)


def normalize_token(value: str) -> str:
    ascii_value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def normalize_hanzi(value: str) -> str:
    return re.sub(r"\s+", "", (value or "").strip())


def citation_aliases(value: str) -> list[tuple[int, str]]:
    tokens = value.split()
    aliases: list[tuple[int, str]] = []
    seen: set[str] = set()

    def add(priority: int, raw: str) -> None:
        normalized = normalize_token(raw)
        if normalized and normalized not in seen:
            aliases.append((priority, normalized))
            seen.add(normalized)

    add(0, value)
    if len(tokens) > 1:
        add(1, " ".join(tokens[1:]))
        add(2, tokens[-1])
    return aliases


def key_stem(key: str) -> str:
    match = re.match(r"^([A-Za-z]+)\d{4}[a-z]?", key)
    return match.group(1) if match else key


def extract_field(body: str, name: str) -> str:
    match = re.search(
        rf"^\s*{name}\s*=\s*\{{(?P<value>.+?)\}}\s*,?\s*$",
        body,
        re.MULTILINE,
    )
    return (match.group("value") if match else "").strip()


def load_pinyin_terms() -> dict[str, dict[str, str]]:
    if not PINYIN_TERMS_TSV.exists():
        return {}
    with PINYIN_TERMS_TSV.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return {row["key"]: row for row in reader if row.get("key")}


def pinyin_term_citation_name(term: dict[str, str]) -> str:
    return (term.get("pinyin_plain") or term.get("pinyin_accented") or "").strip()


def clean_pages(value: str) -> str:
    match = PAGE_FRAGMENT_RE.match((value or "").strip())
    return (match.group(1) if match else "").strip()


def entry_aliases(entry: dict) -> set[str]:
    aliases = set()
    primary_name = entry.get("author", "")
    if " and " not in primary_name.lower():
        aliases.add(normalize_token(entry.get("surname", "")))
    for raw in (
        entry.get("shortauthor", ""),
        entry.get("userd", ""),
        primary_name,
        key_stem(entry["key"]),
        entry.get("title", ""),
    ):
        normalized = normalize_token(raw)
        if normalized:
            aliases.add(normalized)
    return aliases


def load_bib_index() -> list[dict]:
    """Return a list of {key, surname, year, suffix} dicts from the .bib."""
    if not BIB_DIR.exists():
        return []
    out = []
    for bib_file in sorted(BIB_DIR.glob("*.bib")):
        text = bib_file.read_text(encoding="utf-8")
        for m in ENTRY_RE.finditer(text):
            body = m.group("body")
            author = extract_field(body, "author") or extract_field(body, "editor")
            if not author:
                continue
            shortauthor = extract_field(body, "shortauthor")
            surname = re.split(r"[ ,]", author.strip())[0]
            key = m.group("key")
            # Year suffix is encoded in the key tail (e.g., Akatsuka1955a)
            suffix = ""
            ks = re.match(r"^[A-Za-z]+\d{4}([a-z])", key)
            if ks:
                suffix = ks.group(1)
            year = extract_field(body, "year")
            if not year:
                continue
            out.append({
                "key": key,
                "surname": surname,
                "year": year,
                "suffix": suffix,
                "author": author,
                "usera": extract_field(body, "usera"),
                "userd": extract_field(body, "userd"),
                "shortauthor": shortauthor,
                "pages": extract_field(body, "pages"),
                "title": extract_field(body, "title"),
            })
    return out


def filter_candidates_by_pages(candidates: list[dict], cited_pages: str) -> list[dict]:
    if len(candidates) <= 1 or not cited_pages:
        return candidates
    cited_numbers = [int(part) for part in re.findall(r"\d+", cited_pages)]
    if not cited_numbers:
        return candidates

    filtered = []
    for entry in candidates:
        entry_pages = entry.get("pages", "")
        if not entry_pages:
            filtered.append(entry)
            continue
        entry_numbers = [int(part) for part in re.findall(r"\d+", entry_pages)]
        if not entry_numbers:
            filtered.append(entry)
            continue
        if min(cited_numbers) >= min(entry_numbers) and max(cited_numbers) <= max(entry_numbers):
            filtered.append(entry)

    return filtered or candidates


def find_candidates(
    bib: list[dict], surname: str, year: str, suffix: str, term_hanzi: str = ""
) -> list[dict]:
    citation_forms = citation_aliases(surname)
    normalized_term_hanzi = normalize_hanzi(term_hanzi)
    results = []
    for e in bib:
        if e["year"] != year:
            continue
        if suffix and e["suffix"] != suffix:
            continue
        aliases = entry_aliases(e)
        best_score = None
        if normalized_term_hanzi and normalize_hanzi(e.get("usera", "")) == normalized_term_hanzi:
            best_score = -1
        for priority, citation in citation_forms:
            if citation in aliases:
                score = priority * 10
            elif any(alias.startswith(citation) or citation.startswith(alias) for alias in aliases):
                if not any(len(alias) >= 4 and (alias.startswith(citation) or citation.startswith(alias)) for alias in aliases):
                    continue
                score = priority * 10 + 1
            elif len(citation) >= 4 and any(citation in alias for alias in aliases):
                score = priority * 10 + 2
            else:
                continue
            if best_score is None or score < best_score:
                best_score = score
        if best_score is not None:
            results.append((best_score, e))
    results.sort(key=lambda x: x[0])
    if not results:
        return []
    best = results[0][0]
    best_entries = [entry for score, entry in results if score == best]
    if not suffix:
        unsuffixed = [entry for entry in best_entries if not entry.get("suffix")]
        if unsuffixed:
            return unsuffixed
    return best_entries


def iter_plain_citation_matches(line: str) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    for m in CITATION_RE.finditer(line):
        matches.append({
            "raw": m.group(0),
            "surname": m.group("surname"),
            "year": m.group("year"),
            "suffix": m.group("suffix") or "",
            "pages": clean_pages(m.group("pages") or ""),
            "source_kind": "plain",
            "term_key": "",
            "term_category": "",
        })
    return matches


def iter_pinyinterm_citation_matches(
    line: str, pinyin_terms: dict[str, dict[str, str]]
) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    patterns = [
        PINYINTERM_CITATION_RE,
        PINYINTERM_BRACKETED_CITATION_RE,
    ]
    for pattern in patterns:
        for m in pattern.finditer(line):
            term_key = m.group("term_key")
            term = pinyin_terms.get(term_key, {})
            year = (
                m.groupdict().get("year")
                or m.groupdict().get("year_in_parens")
                or m.groupdict().get("year_bracketed")
                or ""
            )
            suffix = (
                m.groupdict().get("suffix")
                or m.groupdict().get("suffix_in_parens")
                or m.groupdict().get("suffix_bracketed")
                or ""
            )
            matches.append({
                "raw": m.group(0),
                "surname": pinyin_term_citation_name(term) or term_key.replace("-", " "),
                "year": year,
                "suffix": suffix,
                "pages": clean_pages(m.group("pages") or ""),
                "source_kind": "pinyinterm",
                "term_key": term_key,
                "term_category": term.get("category", ""),
            })
    return matches


def iter_line_citation_matches(
    line: str, pinyin_terms: dict[str, dict[str, str]]
) -> list[dict[str, str]]:
    return iter_plain_citation_matches(line) + iter_pinyinterm_citation_matches(
        line, pinyin_terms
    )


def main() -> None:
    bib = load_bib_index()
    pinyin_terms = load_pinyin_terms()
    QA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    matched_rows = []
    unmatched_rows = []
    for tex in sorted(TEX_DIR.rglob("*.tex")):
        if tex.name.startswith(".") or "bibliography" in tex.parts:
            continue
        if "backmatter" in tex.parts:
            continue
        text = tex.read_text(encoding="utf-8")
        for line_num, line in enumerate(text.splitlines(), start=1):
            for match in iter_line_citation_matches(line, pinyin_terms):
                surname = match["surname"]
                year = match["year"]
                suffix = match["suffix"]
                pages = match["pages"]
                term_hanzi = ""
                if match["source_kind"] == "pinyinterm":
                    term_hanzi = pinyin_terms.get(match["term_key"], {}).get("hanzi", "")
                cands = find_candidates(bib, surname, year, suffix, term_hanzi=term_hanzi)
                cands = filter_candidates_by_pages(cands, pages)
                row = {
                    "file": str(tex.relative_to(ROOT)),
                    "line": line_num,
                    "raw": match["raw"].replace("\t", " "),
                    "surname": surname,
                    "year": year + suffix,
                    "pages": pages,
                    "source_kind": match["source_kind"],
                    "term_key": match["term_key"],
                    "term_category": match["term_category"],
                    "candidate_count": len(cands),
                    "candidate_key": cands[0]["key"] if cands else "",
                }
                if len(cands) == 1:
                    matched_rows.append(row)
                else:
                    unmatched_rows.append(row)

    fields = [
        "file",
        "line",
        "raw",
        "surname",
        "year",
        "pages",
        "source_kind",
        "term_key",
        "term_category",
        "candidate_count",
        "candidate_key",
    ]

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
