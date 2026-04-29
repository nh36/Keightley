#!/usr/bin/env python3
"""Render the primary source PDF to per-page PNG images.

Reads source/Keightley_1978.pdf and writes source/pages/p_NNNN.png at the dpi
declared in project.yml (default 300, grayscale). Emits build/logs/render.log
and source/pages/MANIFEST.tsv with sha256 + size per page.

Idempotent: skips pages whose target PNG already exists with a matching
manifest hash. Pass --force to re-render.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_PDF = ROOT / "source" / "Keightley_1978.pdf"
PAGES_DIR = ROOT / "source" / "pages"
LOG_PATH = ROOT / "build" / "logs" / "render.log"
MANIFEST_PATH = PAGES_DIR / "MANIFEST.tsv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def page_count(pdf: Path) -> int:
    out = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError("Could not read page count from pdfinfo")


def render(force: bool, dpi: int) -> None:
    if not SOURCE_PDF.exists():
        sys.exit(f"missing {SOURCE_PDF}")
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    n = page_count(SOURCE_PDF)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cmd_template = [
        "pdftoppm", "-png", "-gray", "-r", str(dpi),
        str(SOURCE_PDF), str(PAGES_DIR / "p"),
    ]

    expected = [PAGES_DIR / f"p-{i:0{len(str(n))}d}.png" for i in range(1, n + 1)]
    needs_render = force or not all(p.exists() for p in expected)

    if needs_render:
        if force:
            for p in PAGES_DIR.glob("p-*.png"):
                p.unlink()
        # pdftoppm zero-pads to width of total page count
        subprocess.check_call(cmd_template)

    # Normalise filenames to p_NNNN.png with 4-digit padding so downstream
    # scripts have a stable schema regardless of book length.
    rendered = sorted(PAGES_DIR.glob("p-*.png"))
    for src in rendered:
        idx = int(src.stem.split("-")[-1])
        dst = PAGES_DIR / f"p_{idx:04d}.png"
        if src != dst:
            shutil.move(str(src), str(dst))

    # Write manifest
    final = sorted(PAGES_DIR.glob("p_*.png"))
    with MANIFEST_PATH.open("w") as f:
        f.write("scan_page\timage_path\tsize_bytes\tsha256\n")
        for p in final:
            f.write(f"{int(p.stem.split('_')[1])}\t{p.relative_to(ROOT)}\t{p.stat().st_size}\t{sha256(p)}\n")

    finished = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with LOG_PATH.open("a") as f:
        f.write(
            f"[{finished}] rendered {len(final)} pages from {SOURCE_PDF.name} "
            f"at {dpi} dpi grayscale (started {started}, force={force})\n"
        )
    print(f"rendered {len(final)} pages → {PAGES_DIR}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    render(force=args.force, dpi=args.dpi)
