#!/usr/bin/env python3
"""Generate TeX pinyin term registrations from a TSV source file."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


REQUIRED_COLUMNS = ["key", "category", "hanzi", "pinyin_plain", "pinyin_accented"]
VALID_CATEGORIES = {"person", "place", "title", "term"}
DEFAULT_INPUT = Path("data/pinyin_terms.tsv")
DEFAULT_OUTPUT = Path("tex/generated/pinyin_terms.tex")


def tex_escape(value: str) -> str:
    """Escape TeX-sensitive characters while preserving Unicode text."""
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "%": r"\%",
        "&": r"\&",
        "#": r"\#",
        "$": r"\$",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in value)


def read_rows(input_path: Path) -> list[dict[str, str]]:
    with input_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != REQUIRED_COLUMNS:
            raise ValueError(
                f"Expected TSV header {REQUIRED_COLUMNS}, found {reader.fieldnames}"
            )

        rows: list[dict[str, str]] = []
        seen_keys: set[str] = set()
        for line_no, row in enumerate(reader, start=2):
            clean = {key: (value or "").strip() for key, value in row.items()}
            key = clean["key"]
            category = clean["category"]

            if not key:
                raise ValueError(f"Row {line_no}: key must not be empty")
            if key in seen_keys:
                raise ValueError(f"Row {line_no}: duplicate key '{key}'")
            if category not in VALID_CATEGORIES:
                raise ValueError(
                    f"Row {line_no}: category '{category}' must be one of {sorted(VALID_CATEGORIES)}"
                )
            if not clean["hanzi"]:
                raise ValueError(f"Row {line_no}: hanzi must not be empty")
            if category in {"person", "place"} and not clean["pinyin_plain"]:
                raise ValueError(
                    f"Row {line_no}: {category} entries require pinyin_plain"
                )
            if category == "title" and not clean["pinyin_accented"]:
                raise ValueError(
                    f"Row {line_no}: title entries require pinyin_accented"
                )

            seen_keys.add(key)
            rows.append(clean)
        return rows


def render_rows(rows: list[dict[str, str]]) -> str:
    lines = [
        "% Auto-generated from data/pinyin_terms.tsv. Do not edit by hand.",
        "% Regenerate with scripts/generate_pinyin_terms_tex.py.",
        "",
    ]
    for row in rows:
        lines.append(
            "\\RegisterPinyinTerm"
            f"{{{tex_escape(row['key'])}}}"
            f"{{{tex_escape(row['category'])}}}"
            f"{{{tex_escape(row['hanzi'])}}}"
            f"{{{tex_escape(row['pinyin_plain'])}}}"
            f"{{{tex_escape(row['pinyin_accented'])}}}"
        )
    lines.append("")
    return "\n".join(lines)


def generate_terms_tex(input_path: Path, output_path: Path) -> None:
    rows = read_rows(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_rows(rows), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate TeX pinyin term registrations from TSV data."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    generate_terms_tex(args.input, args.output)
    print(f"Generated {args.output} from {args.input}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
