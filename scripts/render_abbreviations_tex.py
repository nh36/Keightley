#!/usr/bin/env python3
"""Render a bibliography-style LaTeX version of Bibliography A from YAML."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "abbreviations.yml"
OUTPUT = ROOT / "tex" / "backmatter" / "abbreviations_live.tex"

FIELD_RE = re.compile(r"^\s{4}(body|body_tesseract|gv_excerpt|gv_cjk|cjk):\s*(.*)$")
ABBR_RE = re.compile(r"^\s{2}- abbr:\s*(.*)$")
INITIAL_RE = re.compile(r"\b([A-Z])\.")
SENTENCE_SPLIT_RE = re.compile(r"(?<=\.)\s+(?=(?:\[[A-Z]|[A-Z0-9]))")
SERIAL_PATTERNS = (
    re.compile(r"^(?P<title>Journal of Oriental Studies)(?P<rest> .+)$"),
    re.compile(r"^(?P<title>Guoli Taiwan daxue kaogu renlei xuekan)(?P<rest> .+)$"),
    re.compile(r"^(?P<title>Tōhō gakuhō)(?P<rest> .+)$"),
    re.compile(r"^(?P<title>Qida jikan)(?P<rest> .+)$"),
    re.compile(r"^(?P<title>Occasional Papers in Archaeology)(?P<rest>, .+)$"),
    re.compile(r"^(?P<title>BIHP)(?P<rest> .+)$"),
)
PROTECTED_LITERALS = (
    "N.p.",
    "n.d.",
    "Vol.",
    "vols.",
    "Pt.",
    "pt.",
    "pp.",
    "no.",
    "Rev.",
    "rev.",
)
SENTINEL = "<<DOT>>"
TITLE_NOTE_RE = re.compile(r"^(?P<title>.+?)\s+\[(?P<note>[^\[\]]+)\]$")


def parse_scalar(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {"'", '"'}:
        raw = raw[1:-1]
        if raw and raw[0] == raw[-1] == "'":
            raw = raw[1:-1]
        raw = raw.replace("''", "'").replace('\\"', '"')
    return " ".join(raw.split())


def escape_tex(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def protect_sentence_periods(text: str) -> str:
    protected = text
    for literal in PROTECTED_LITERALS:
        protected = protected.replace(literal, literal.replace(".", SENTINEL))
    protected = INITIAL_RE.sub(r"\1" + SENTINEL, protected)
    return protected


def restore_sentence_periods(text: str) -> str:
    return text.replace(SENTINEL, ".")


def split_sentences(text: str) -> list[str]:
    protected = protect_sentence_periods(text)
    parts = [part.strip() for part in SENTENCE_SPLIT_RE.split(protected) if part.strip()]
    return [restore_sentence_periods(part) for part in parts]


def strip_period(text: str) -> str:
    return text[:-1] if text.endswith(".") else text


def ensure_period(text: str) -> str:
    if text.endswith(".") or text.endswith(".]"):
        return text
    if text.endswith("]"):
        return f"{text}."
    return f"{text}."


def wrap_booktitle(text: str) -> str:
    return rf"\booktitle{{{escape_tex(text)}}}"


def format_container_sentence(sentence: str) -> str:
    core = strip_period(sentence)
    if core.startswith("In "):
        return f"In {wrap_booktitle(core[3:])}."

    for pattern in SERIAL_PATTERNS:
        match = pattern.match(core)
        if match:
            title = wrap_booktitle(match.group("title"))
            rest = escape_tex(match.group("rest"))
            return f"{title}{rest}."

    return escape_tex(sentence)


def looks_like_publication(sentence: str) -> bool:
    return bool(
        re.match(
            r"^(?:\[[A-Za-z]+\]|[A-Z][A-Za-z&.' -]+|N\.p\.)[, ].*\d{4}|"
            r"^(?:Reprint|Edited by|Rev\. ed\.|Volume|Vols?\.|Pt\.|2 vols\.|Unpublished|Shakubun\.|Sakuin\.)",
            sentence,
        )
    )


def split_author_and_title(parts: list[str]) -> tuple[str, str, list[str]] | None:
    if len(parts) < 2:
        return None

    author = parts[0]
    title = parts[1]
    rest = parts[2:]

    if title.startswith("["):
        return None

    if looks_like_publication(title) and ". " in author:
        author, title = author.rsplit(". ", 1)
        author += "."
        rest = [parts[1], *rest]

    return author, title, rest


def split_title_note(title: str) -> tuple[str, str]:
    match = TITLE_NOTE_RE.match(title)
    if not match:
        return title, ""
    return match.group("title"), f"[{match.group('note')}]"


def format_structured_body(body: str, cjk: str) -> str:
    parts = split_sentences(body)
    split_body = split_author_and_title(parts)
    if split_body is None:
        rendered = escape_tex(body)
        if cjk:
            rendered += f" {wrap_booktitle(f'[{cjk}]')}"
        return rendered

    author_text, title_text, rest_parts = split_body
    author = escape_tex(author_text)
    title, title_note = split_title_note(strip_period(title_text))
    if cjk:
        title = f"{title} [{cjk}]"

    formatted_parts = [author, f"{wrap_booktitle(title)}."]
    if title_note:
        formatted_parts.append(escape_tex(ensure_period(title_note) if not rest_parts else title_note))
    formatted_parts.extend(format_container_sentence(part) for part in rest_parts)
    return " ".join(part for part in formatted_parts if part)


def load_entries() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for line in INPUT.read_text(encoding="utf-8").splitlines():
        abbr_match = ABBR_RE.match(line)
        if abbr_match:
            if current:
                entries.append(current)
            current = {"abbr": parse_scalar(abbr_match.group(1))}
            continue

        field_match = FIELD_RE.match(line)
        if field_match and current is not None:
            current[field_match.group(1)] = parse_scalar(field_match.group(2))

    if current:
        entries.append(current)

    return entries


def render_entry(entry: dict[str, str]) -> str:
    body = entry.get("body") or entry.get("body_tesseract") or entry.get("gv_excerpt") or "[description pending]"
    cjk = entry.get("cjk", "")
    gv_cjk = entry.get("gv_cjk", "")

    rendered_body = format_structured_body(body, cjk)
    rendered = f"  \\item[{escape_tex(entry['abbr'])}] {rendered_body}"
    if cjk:
        return rendered
    if gv_cjk and "body" not in entry:
        rendered += rf" \hfill\textit{{[CJK: {escape_tex(gv_cjk)}]}}"
    return rendered


def main() -> None:
    entries = load_entries()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "% Generated by scripts/render_abbreviations_tex.py.",
        r"\section*{Oracle-Bone Collections Cited and Their Abbreviations}",
        r"\addcontentsline{toc}{section}{Oracle-Bone Collections Cited and Their Abbreviations}",
        "",
        r"\newlength{\keightleyabbrevlabelwidth}",
        r"\settowidth{\keightleyabbrevlabelwidth}{\textbf{Jiabian kaoshi}}",
        r"\begin{list}{}{%",
        r"  \setlength{\labelwidth}{\keightleyabbrevlabelwidth}%",
        r"  \setlength{\labelsep}{1em}%",
        r"  \setlength{\leftmargin}{\labelwidth}%",
        r"  \addtolength{\leftmargin}{\labelsep}%",
        r"  \setlength{\itemindent}{0pt}%",
        r"  \setlength{\itemsep}{0.5\baselineskip}%",
        r"  \setlength{\parsep}{0pt}%",
        r"  \setlength{\topsep}{0.5\baselineskip}%",
        r"  \renewcommand{\makelabel}[1]{\textbf{##1}\hfill}%",
        r"}",
    ]
    lines.extend(render_entry(entry) for entry in entries if entry.get("abbr"))
    lines.append(r"\end{list}")
    lines.append("")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
