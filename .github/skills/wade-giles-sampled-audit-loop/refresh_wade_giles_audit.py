#!/usr/bin/env python3
"""Refresh data/wade_giles_audit.tsv while preserving curated notes."""

from __future__ import annotations

import argparse
import csv
import io
import subprocess
import tempfile
from pathlib import Path

FIELDNAMES = [
    "wade_giles",
    "frequency",
    "type",
    "chapters",
    "first_context",
    "pinyin",
    "notes",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise RuntimeError(f"Missing TSV header in {path}")
        missing = {"wade_giles"} - set(reader.fieldnames)
        if missing:
            raise RuntimeError(f"{path} is missing required columns: {sorted(missing)}")
        return list(reader)


def render_rows(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=FIELDNAMES,
        delimiter="\t",
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def merge_rows(
    old_rows: list[dict[str, str]], new_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    old_map = {row["wade_giles"]: row for row in old_rows}
    merged: list[dict[str, str]] = []
    for row in new_rows:
        old = old_map.get(row["wade_giles"], {})
        merged.append(
            {
                "wade_giles": row.get("wade_giles", ""),
                "frequency": row.get("frequency", ""),
                "type": row.get("type", ""),
                "chapters": row.get("chapters", ""),
                "first_context": row.get("first_context", ""),
                "pinyin": old.get("pinyin", ""),
                "notes": old.get("notes", ""),
            }
        )
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refresh data/wade_giles_audit.tsv from current chapter text"
    )
    parser.add_argument(
        "--root",
        default=Path(__file__).resolve().parents[3],
        type=Path,
        help="Repository root",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and merge the refreshed TSV without writing it",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    audit_path = root / "data" / "wade_giles_audit.tsv"
    audit_script = root / "scripts" / "audit_wade_giles.py"
    if not audit_path.exists():
        raise SystemExit(f"Missing audit TSV: {audit_path}")
    if not audit_script.exists():
        raise SystemExit(f"Missing audit script: {audit_script}")

    old_rows = read_rows(audit_path)
    with tempfile.NamedTemporaryFile(suffix=".tsv", delete=False) as handle:
        temp_path = Path(handle.name)

    subprocess.run(
        ["python3", str(audit_script), "--output", str(temp_path)],
        check=True,
        cwd=root,
    )

    try:
        new_rows = read_rows(temp_path)
        merged_rows = merge_rows(old_rows, new_rows)
        merged_text = render_rows(merged_rows)
        old_text = audit_path.read_text(encoding="utf-8")

        if args.dry_run:
            status = "changed" if merged_text != old_text else "unchanged"
            print(
                f"Dry run complete: {status}; old rows={len(old_rows)}, new rows={len(new_rows)}"
            )
            return 0

        audit_path.write_text(merged_text, encoding="utf-8")
        print(
            f"Refreshed {audit_path} (old rows={len(old_rows)}, new rows={len(new_rows)})"
        )
        return 0
    finally:
        temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
