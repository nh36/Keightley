#!/usr/bin/env python3
"""Refresh the live Wade-Giles audit and retire resolved rows into history."""

from __future__ import annotations

import argparse
import csv
import io
import re
import subprocess
import tempfile
from datetime import datetime
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

HISTORY_FIELDNAMES = [
    "replacement_id",
    "provenance_ref",
    "pass_summary",
    "source_form",
    "resolved_form",
    "resolution_type",
    "occurrence_index",
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


def read_history_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise RuntimeError(f"Missing TSV header in {path}")
        missing = {"replacement_id", "source_form"} - set(reader.fieldnames)
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


def render_history_rows(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=HISTORY_FIELDNAMES,
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


def retired_rows(
    old_rows: list[dict[str, str]], new_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    live_terms = {row["wade_giles"] for row in new_rows}
    return [row for row in old_rows if row["wade_giles"] not in live_terms]


def next_replacement_id(provenance_ref: str, existing_rows: list[dict[str, str]]) -> str:
    pattern = re.compile(rf"^{re.escape(provenance_ref)}-(\d+)$")
    max_seen = 0
    for row in existing_rows:
        replacement_id = row.get("replacement_id", "")
        match = pattern.match(replacement_id)
        if match:
            max_seen = max(max_seen, int(match.group(1)))
    return f"{provenance_ref}-{max_seen + 1:03d}"


def map_retired_row(
    row: dict[str, str],
    provenance_ref: str,
    pass_summary: str,
    existing_rows: list[dict[str, str]],
) -> dict[str, str]:
    notes = []
    if row.get("notes"):
        notes.append(row["notes"])
    notes.append(
        "Retired from data/wade_giles_audit.tsv after disappearing from the live chapter audit."
    )
    if row.get("frequency"):
        notes.append(f"Previous live frequency={row['frequency']}.")
    if row.get("chapters"):
        notes.append(f"Previous chapters={row['chapters']}.")
    if row.get("first_context"):
        notes.append(f"Previous first_context={row['first_context']}.")

    replacement_id = next_replacement_id(provenance_ref, existing_rows)
    history_row = {
        "replacement_id": replacement_id,
        "provenance_ref": provenance_ref,
        "pass_summary": pass_summary,
        "source_form": row.get("wade_giles", ""),
        "resolved_form": row.get("pinyin", ""),
        "resolution_type": "retired-from-live-audit",
        "occurrence_index": "1",
        "notes": " ".join(notes),
    }
    existing_rows.append(history_row)
    return history_row


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
    parser.add_argument(
        "--provenance-ref",
        help="History provenance for rows retired from the live audit",
    )
    parser.add_argument(
        "--pass-summary",
        default="sampled audit refresh",
        help="History pass summary for rows retired from the live audit",
    )
    parser.add_argument(
        "--skip-history-retirement",
        action="store_true",
        help="Refresh the live audit without appending disappeared rows into history",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    audit_path = root / "data" / "wade_giles_audit.tsv"
    history_path = root / "data" / "wade_giles_resolved_history.tsv"
    audit_script = root / "scripts" / "audit_wade_giles.py"
    if not audit_path.exists():
        raise SystemExit(f"Missing audit TSV: {audit_path}")
    if not audit_script.exists():
        raise SystemExit(f"Missing audit script: {audit_script}")

    old_rows = read_rows(audit_path)
    history_rows = read_history_rows(history_path)
    provenance_ref = args.provenance_ref or datetime.now().strftime("worktree-%Y%m%d-%H%M%S")
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
        removed_rows = retired_rows(old_rows, new_rows)
        merged_text = render_rows(merged_rows)
        old_text = audit_path.read_text(encoding="utf-8")

        if args.dry_run:
            status = "changed" if merged_text != old_text else "unchanged"
            print(
                f"Dry run complete: {status}; old rows={len(old_rows)}, new rows={len(new_rows)}, retired rows={len(removed_rows)}"
            )
            return 0

        audit_path.write_text(merged_text, encoding="utf-8")
        if removed_rows and not args.skip_history_retirement:
            for row in removed_rows:
                map_retired_row(row, provenance_ref, args.pass_summary, history_rows)
            history_path.write_text(render_history_rows(history_rows), encoding="utf-8")
        print(
            f"Refreshed {audit_path} (old rows={len(old_rows)}, new rows={len(new_rows)}, retired rows={0 if args.skip_history_retirement else len(removed_rows)})"
        )
        return 0
    finally:
        temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
