#!/usr/bin/env python3
"""Wire raw in-text author-year citations to live \\citeyear references.

This complements scripts/09_intext_citations.py by rewriting the matched
citation forms in-place. It handles:

* Surname (1975)
* Surname [1975]
* \\pinyinterm{person} (1975)
* \\pinyinterm{person} [1975]
* \\pinyinterm{person} ([1975], pp. 55-56)
* same-author continuation years such as:
  * Keightley (1973a) and (1975c)
  * Tung [1945]; [1951]
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TEX_DIR = ROOT / "tex"
SCAN_SCRIPT_PATH = ROOT / "scripts" / "09_intext_citations.py"

SPEC = importlib.util.spec_from_file_location("intext_citations", SCAN_SCRIPT_PATH)
intext_citations = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(intext_citations)

YEAR_PATTERN = r"(?P<year>(?:18|19|20)\d{2})(?P<suffix>[a-z]?)"
ASCII_NAME = r"[A-ZÀ-ÖØ-ÞĀ-ſ][A-Za-zÀ-ÖØ-öø-ÿĀ-ſ'’\-.]+"
PLAIN_LEADER = rf"{ASCII_NAME}(?:\s+(?:(?:and|et\s+al\.?)\s+)?{ASCII_NAME})*"
PLAIN_NAME_PATTERN = rf"(?P<leader>{PLAIN_LEADER})"
CONTEXT_LEADER_PATTERN = rf"(?P<leader>\\pinyinterm\{{[^}}]+\}}|{PLAIN_LEADER})"

PLAIN_PAREN_RE = re.compile(
    rf"{PLAIN_NAME_PATTERN}\s*\({YEAR_PATTERN}\)"
    rf"(?:\s*,?\s*(?:\d+(?:\.\d+)?,\s*)?pp?\.\s*(?P<pages>{intext_citations.PAGE_PATTERN}))?"
)

PLAIN_BRACKET_RE = re.compile(
    rf"{PLAIN_NAME_PATTERN}\s*\[{YEAR_PATTERN}\]"
    rf"(?:\s*,?\s*(?:\d+(?:\.\d+)?,\s*)?pp?\.\s*(?P<pages>{intext_citations.PAGE_PATTERN}))?"
)

PLAIN_PAREN_BRACKET_RE = re.compile(
    rf"{PLAIN_NAME_PATTERN}\s*\(\[{YEAR_PATTERN}\](?P<inner>[^)]*)\)"
)

PINYINTERM_DIRECT_BRACKET_RE = re.compile(
    rf"(?P<leader>\\pinyinterm\{{(?P<term_key>[^}}]+)\}})\s*\[{YEAR_PATTERN}\]"
    rf"(?:\s*,?\s*(?:\d+(?:\.\d+)?,\s*)?pp?\.\s*(?P<pages>{intext_citations.PAGE_PATTERN}))?"
)

PINYINTERM_PAREN_BRACKET_RE = re.compile(
    rf"(?P<leader>\\pinyinterm\{{(?P<term_key>[^}}]+)\}})\s*\(\[{YEAR_PATTERN}\](?P<inner>[^)]*)\)"
)

CONTINUATION_PAREN_RE = re.compile(rf"\({YEAR_PATTERN}\)")
CONTINUATION_BRACKET_RE = re.compile(rf"\[{YEAR_PATTERN}\]")
WIRED_PAREN_CONTEXT_RE = re.compile(
    rf"{CONTEXT_LEADER_PATTERN}\s*\(\\citeyear\{{(?P<key>[^}}]+)\}}\)"
)
WIRED_BRACKET_CONTEXT_RE = re.compile(
    rf"{CONTEXT_LEADER_PATTERN}\s*\[\\citeyear\{{(?P<key>[^}}]+)\}}\]"
)
WIRED_PAREN_BRACKET_CONTEXT_RE = re.compile(
    rf"{CONTEXT_LEADER_PATTERN}\s*\(\[\\citeyear\{{(?P<key>[^}}]+)\}}[^)]*\)"
)
BARE_PINYINTERM_CONTEXT_RE = re.compile(r"(?P<leader>\\pinyinterm\{(?P<term_key>[^}]+)\})")
BARE_PINYINPOSS_CONTEXT_RE = re.compile(r"(?P<leader>\\pinyinposs\{(?P<term_key>[^}]+)\})")
KEYED_CITECMD_CONTEXT_RE = re.compile(r"\\(?:textcite|Textcite)\{(?P<key>[^}]+)\}")

TARGET_DIRS = [
    TEX_DIR / "frontmatter",
    TEX_DIR / "chapters",
    TEX_DIR / "appendices",
    TEX_DIR / "plates",
]

SPECIAL_CITATION_KEYS = {
    ("Keightley", "1975", "c"): "Keightley1975Legitimation",
    ("Biot", "1969", ""): "Biot1969Tcheouli",
    ("Couvreur", "1950", ""): "Couvreur1950Liki",
    ("Goodycar", "1971", ""): "Goodyear1971Archaeological",
    ("Blackith and Reyment", "1971", ""): "BlackithReyment1971Morphometrics",
    ("Sneath and Sokal", "1973", ""): "SneathSokal1973Numerical",
    ("Ji Yun", "1974", ""): "Ji1974Kaocheng",
    ("Tian Qianjun", "1973", ""): "Tian1973Study",
    ("Wu Qichang", "1971", ""): "Wu1971Study",
    ("Wu Ch'i-ch'ang", "1971", ""): "Wu1971Study",
    ("Itō", "1962", ""): "Ito1962Indai",
    ("Itō", "1962", "a"): "Ito1962aInizen",
    ("Hayashi Taisuke", "1909", ""): "Hayashi1909Shinkoku",
    ("Kuo Mo-jo", "1972", ""): "Kuo1972Anyang",
    ("Dong", "1964", ""): "Tung1964Fifty",
    ("Kaizuka and Itō", "1953", ""): "KaizukaIto1953Kokotsubun",
}
SPECIAL_CITATION_KEYS = {
    (intext_citations.normalize_token(name), year, suffix): key
    for (name, year, suffix), key in SPECIAL_CITATION_KEYS.items()
}


class Token:
    def __init__(
        self,
        *,
        start: int,
        end: int,
        kind: str,
        raw: str,
        surname: str,
        year: str,
        suffix: str,
        pages: str,
        term_key: str = "",
        term_category: str = "",
        term_hanzi: str = "",
        explicit: bool = True,
        context_only: bool = False,
        key: str = "",
    ) -> None:
        self.start = start
        self.end = end
        self.kind = kind
        self.raw = raw
        self.surname = surname
        self.year = year
        self.suffix = suffix
        self.pages = pages
        self.term_key = term_key
        self.term_category = term_category
        self.term_hanzi = term_hanzi
        self.explicit = explicit
        self.context_only = context_only
        self.key = key


PINYIN_TERMS = intext_citations.load_pinyin_terms()
BIB_INDEX = intext_citations.load_bib_index()
BIB_BY_KEY = {entry["key"]: entry for entry in BIB_INDEX}


def target_tex_files() -> list[Path]:
    files: list[Path] = []
    for base in TARGET_DIRS:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.tex")):
            files.append(path)
    return files


def split_comment(line: str) -> tuple[str, str]:
    escaped = False
    for idx, char in enumerate(line):
        if char == "\\" and not escaped:
            escaped = True
            continue
        if char == "%" and not escaped:
            return line[:idx], line[idx:]
        escaped = False
    return line, ""


def pinyin_term_context(term_key: str) -> tuple[str, str, str]:
    term = PINYIN_TERMS.get(term_key, {})
    surname = (
        term.get("pinyin_plain")
        or term.get("pinyin_accented")
        or term_key.replace("-", " ")
    )
    return surname, term.get("category", ""), term.get("hanzi", "")


def raw_year(value: str, suffix: str) -> str:
    return f"{value}{suffix}"


def collect_explicit_tokens(segment: str) -> list[Token]:
    tokens: list[Token] = []

    for match in PLAIN_PAREN_RE.finditer(segment):
        tokens.append(
            Token(
                start=match.start(),
                end=match.end(),
                kind="plain-paren",
                raw=match.group(0),
                surname=match.group("leader"),
                year=match.group("year"),
                suffix=match.group("suffix") or "",
                pages=intext_citations.clean_pages(match.group("pages") or ""),
            )
        )

    for match in PLAIN_BRACKET_RE.finditer(segment):
        tokens.append(
            Token(
                start=match.start(),
                end=match.end(),
                kind="plain-bracket",
                raw=match.group(0),
                surname=match.group("leader"),
                year=match.group("year"),
                suffix=match.group("suffix") or "",
                pages=intext_citations.clean_pages(match.group("pages") or ""),
            )
        )

    for match in PLAIN_PAREN_BRACKET_RE.finditer(segment):
        tokens.append(
            Token(
                start=match.start(),
                end=match.end(),
                kind="plain-paren-bracket",
                raw=match.group(0),
                surname=match.group("leader"),
                year=match.group("year"),
                suffix=match.group("suffix") or "",
                pages="",
            )
        )

    for match in intext_citations.PINYINTERM_CITATION_RE.finditer(segment):
        term_key = match.group("term_key")
        surname, category, hanzi = pinyin_term_context(term_key)
        tokens.append(
            Token(
                start=match.start(),
                end=match.end(),
                kind="pinyinterm-paren",
                raw=match.group(0),
                surname=surname,
                year=match.group("year"),
                suffix=match.group("suffix") or "",
                pages=intext_citations.clean_pages(match.group("pages") or ""),
                term_key=term_key,
                term_category=category,
                term_hanzi=hanzi,
            )
        )

    for match in PINYINTERM_DIRECT_BRACKET_RE.finditer(segment):
        term_key = match.group("term_key")
        surname, category, hanzi = pinyin_term_context(term_key)
        tokens.append(
            Token(
                start=match.start(),
                end=match.end(),
                kind="pinyinterm-bracket",
                raw=match.group(0),
                surname=surname,
                year=match.group("year"),
                suffix=match.group("suffix") or "",
                pages=intext_citations.clean_pages(match.group("pages") or ""),
                term_key=term_key,
                term_category=category,
                term_hanzi=hanzi,
            )
        )

    for match in PINYINTERM_PAREN_BRACKET_RE.finditer(segment):
        term_key = match.group("term_key")
        surname, category, hanzi = pinyin_term_context(term_key)
        tokens.append(
            Token(
                start=match.start(),
                end=match.end(),
                kind="pinyinterm-paren-bracket",
                raw=match.group(0),
                surname=surname,
                year=match.group("year"),
                suffix=match.group("suffix") or "",
                pages="",
                term_key=term_key,
                term_category=category,
                term_hanzi=hanzi,
            )
        )

    tokens.sort(key=lambda token: (token.start, -(token.end - token.start), token.kind))
    filtered: list[Token] = []
    cursor = -1
    for token in tokens:
        if token.start < cursor:
            continue
        filtered.append(token)
        cursor = token.end
    return filtered


def collect_context_tokens(segment: str) -> list[Token]:
    tokens: list[Token] = []

    for regex in (
        WIRED_PAREN_CONTEXT_RE,
        WIRED_BRACKET_CONTEXT_RE,
        WIRED_PAREN_BRACKET_CONTEXT_RE,
    ):
        for match in regex.finditer(segment):
            leader = match.group("leader")
            key = match.group("key")
            term_key = ""
            category = ""
            hanzi = ""
            surname = leader
            if leader.startswith(r"\pinyinterm{"):
                term_key = leader[len(r"\pinyinterm{"):-1]
                surname, category, hanzi = pinyin_term_context(term_key)
            tokens.append(
                Token(
                    start=match.start(),
                    end=match.end(),
                    kind="wired-context",
                    raw=match.group(0),
                    surname=surname,
                    year="",
                    suffix="",
                    pages="",
                    term_key=term_key,
                    term_category=category,
                    term_hanzi=hanzi,
                    explicit=False,
                    context_only=True,
                    key=key,
                )
            )

    for regex in (BARE_PINYINTERM_CONTEXT_RE, BARE_PINYINPOSS_CONTEXT_RE):
        for match in regex.finditer(segment):
            term_key = match.group("term_key")
            surname, category, hanzi = pinyin_term_context(term_key)
            tokens.append(
                Token(
                    start=match.start(),
                    end=match.end(),
                    kind="bare-pinyin-context",
                    raw=match.group(0),
                    surname=surname,
                    year="",
                    suffix="",
                    pages="",
                    term_key=term_key,
                    term_category=category,
                    term_hanzi=hanzi,
                    explicit=False,
                    context_only=True,
                )
            )

    for match in KEYED_CITECMD_CONTEXT_RE.finditer(segment):
        key = match.group("key")
        entry = BIB_BY_KEY.get(key)
        if not entry:
            continue
        surname = entry.get("shortauthor") or entry.get("surname") or entry.get("author") or ""
        tokens.append(
            Token(
                start=match.start(),
                end=match.end(),
                kind="keyed-cite-context",
                raw=match.group(0),
                surname=surname,
                year="",
                suffix="",
                pages="",
                explicit=False,
                context_only=True,
                key=key,
                term_hanzi=entry.get("usera", ""),
            )
        )

    tokens.sort(key=lambda token: (token.start, -(token.end - token.start), token.kind))
    filtered: list[Token] = []
    cursor = -1
    for token in tokens:
        if token.start < cursor:
            continue
        filtered.append(token)
        cursor = token.end
    return filtered


def collect_continuation_tokens(segment: str, explicit_tokens: list[Token]) -> list[Token]:
    occupied = [(token.start, token.end) for token in explicit_tokens]
    continuations: list[Token] = []
    for regex, kind in (
        (CONTINUATION_PAREN_RE, "continuation-paren"),
        (CONTINUATION_BRACKET_RE, "continuation-bracket"),
    ):
        for match in regex.finditer(segment):
            start, end = match.span()
            if any(start < occ_end and end > occ_start for occ_start, occ_end in occupied):
                continue
            continuations.append(
                Token(
                    start=start,
                    end=end,
                    kind=kind,
                    raw=match.group(0),
                    surname="",
                    year=match.group("year"),
                    suffix=match.group("suffix") or "",
                    pages="",
                    explicit=False,
                )
            )
    continuations.sort(key=lambda token: (token.start, token.end))
    return continuations


def replace_year(raw: str, year: str, suffix: str, key: str, opener: str, closer: str) -> str:
    literal = f"{opener}{raw_year(year, suffix)}{closer}"
    wired = f"{opener}\\citeyear{{{key}}}{closer}"
    return raw.replace(literal, wired, 1)


def wire_token(token: Token, key: str) -> str:
    if token.kind in {"plain-paren", "pinyinterm-paren", "continuation-paren"}:
        return replace_year(token.raw, token.year, token.suffix, key, "(", ")")
    if token.kind in {"plain-bracket", "pinyinterm-bracket", "continuation-bracket"}:
        return replace_year(token.raw, token.year, token.suffix, key, "[", "]")
    if token.kind in {"plain-paren-bracket", "pinyinterm-paren-bracket"}:
        return replace_year(token.raw, token.year, token.suffix, key, "[", "]")
    raise ValueError(f"Unsupported token kind: {token.kind}")


def resolve_key(token: Token, bib: list[dict], context: Token | None) -> str | None:
    if token.explicit:
        surname = token.surname
        term_hanzi = token.term_hanzi
    else:
        if context is None:
            return None
        surname = context.surname
        term_hanzi = context.term_hanzi
    normalized_surname = intext_citations.normalize_token(surname)
    if token.kind == "continuation-paren" and context and context.key:
        special = SPECIAL_CITATION_KEYS.get((normalized_surname, token.year, token.suffix))
        if special:
            return special
    if not token.explicit and context and context.key:
        context_entry = BIB_BY_KEY.get(context.key)
        if context_entry and context_entry.get("year") == token.year:
            context_suffix = context_entry.get("suffix", "")
            if token.suffix == context_suffix or (not token.suffix and context_suffix):
                return context.key
    special = SPECIAL_CITATION_KEYS.get((normalized_surname, token.year, token.suffix))
    if special:
        return special
    candidates = intext_citations.find_candidates(
        bib,
        surname,
        token.year,
        token.suffix,
        term_hanzi=term_hanzi,
    )
    candidates = intext_citations.filter_candidates_by_pages(candidates, token.pages)
    if len(candidates) != 1:
        return None
    return candidates[0]["key"]


def rewrite_segment(segment: str, bib: list[dict]) -> tuple[str, list[tuple[str, str]]]:
    explicit_tokens = collect_explicit_tokens(segment)
    context_tokens = collect_context_tokens(segment)
    tokens = explicit_tokens + context_tokens + collect_continuation_tokens(segment, explicit_tokens + context_tokens)
    tokens.sort(key=lambda token: (token.start, -(token.end - token.start), token.kind))

    out: list[str] = []
    cursor = 0
    changes: list[tuple[str, str]] = []
    last_context: Token | None = None

    for token in tokens:
        if token.start < cursor:
            continue
        key = resolve_key(token, bib, last_context)
        out.append(segment[cursor:token.start])
        if token.context_only:
            out.append(token.raw)
        elif key is None:
            out.append(token.raw)
        else:
            replacement = wire_token(token, key)
            out.append(replacement)
            if replacement != token.raw:
                changes.append((token.raw, replacement))
        cursor = token.end
        if token.context_only:
            if key is not None:
                token.key = key
            last_context = token
        elif token.explicit and key is not None:
            token.key = key
            last_context = token
    out.append(segment[cursor:])
    return "".join(out), changes


def rewrite_file(path: Path, bib: list[dict]) -> list[tuple[int, str, str]]:
    text = path.read_text(encoding="utf-8")
    updated_lines: list[str] = []
    file_changes: list[tuple[int, str, str]] = []
    changed = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        segment, comment = split_comment(line)
        rewritten, changes = rewrite_segment(segment, bib)
        if changes:
            changed = True
            for before, after in changes:
                file_changes.append((line_number, before, after))
        updated_lines.append(rewritten + comment)
    if changed:
        path.write_text("\n".join(updated_lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
    return file_changes


def should_ignore_scan_hit(segment: str, token: Token) -> bool:
    before = segment[max(0, token.start - 100) : token.start]
    after = segment[token.end : token.end + 80]
    if re.search(
        r"(?i)\b(?:vol\.|volume|edition|reprint(?:ed)?|reissued|published|preface|introduction|digs?)\b",
        before,
    ):
        return True
    if re.search(
        r"(?i)(?:Harvard Journal of Asiatic Studies|Journal of Oriental Studies|RBS\b|Dalu zazhi|Zhonghua renmin)",
        before,
    ):
        return True
    if re.search(r"\b\d+(?:\.\d+)?\s*$", before) and token.raw.startswith(("(", "[")):
        return True
    if re.search(r"(?i)^\s*,?\s*plates?\b", after):
        return True
    return False


def scan_remaining_raw_citations(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    findings: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        segment, _comment = split_comment(line)
        explicit = collect_explicit_tokens(segment)
        contexts = collect_context_tokens(segment)
        continuations = collect_continuation_tokens(segment, explicit + contexts)
        for token in explicit:
            if not should_ignore_scan_hit(segment, token):
                findings.append((line_number, token.raw))
        ordered = sorted(explicit + contexts + continuations, key=lambda token: (token.start, -(token.end - token.start), token.kind))
        last_context: Token | None = None
        for token in ordered:
            if token.context_only:
                last_context = token
            elif token.explicit:
                last_context = token
            elif last_context is not None:
                if not should_ignore_scan_hit(segment, token):
                    findings.append((line_number, token.raw))
    return findings


def main() -> int:
    bib = BIB_INDEX
    all_changes = 0
    unresolved: list[tuple[str, int, str]] = []

    for tex_path in target_tex_files():
        changes = rewrite_file(tex_path, bib)
        all_changes += len(changes)
        unresolved.extend((str(tex_path.relative_to(ROOT)), line, raw) for line, raw in scan_remaining_raw_citations(tex_path))

    print(f"rewired citation fragments: {all_changes}")
    print(f"remaining raw citation fragments: {len(unresolved)}")
    for file, line, raw in unresolved[:200]:
        print(f"{file}:{line}: {raw}")
    return 1 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
