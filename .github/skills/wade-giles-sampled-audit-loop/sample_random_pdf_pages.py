#!/usr/bin/env python3
"""Sample random pages from the built PDF and print page extracts."""

from __future__ import annotations

import argparse
import random
import re
import subprocess
from pathlib import Path


def get_page_count(pdf_path: Path) -> int:
    info = subprocess.check_output(
        ["pdfinfo", str(pdf_path)],
        text=True,
        stderr=subprocess.STDOUT,
    )
    match = re.search(r"^Pages:\s+(\d+)", info, re.M)
    if not match:
        raise RuntimeError(f"Could not determine page count for {pdf_path}")
    return int(match.group(1))


def extract_page_text(pdf_path: Path, page: int, max_chars: int) -> str:
    text = subprocess.check_output(
        ["pdftotext", "-f", str(page), "-l", str(page), str(pdf_path), "-"],
        text=True,
        stderr=subprocess.DEVNULL,
    )
    lines = [line.rstrip() for line in text.splitlines()]
    compacted: list[str] = []
    blank_run = 0
    for line in lines:
        if line.strip():
            compacted.append(line)
            blank_run = 0
        else:
            blank_run += 1
            if blank_run == 1:
                compacted.append("")
    return "\n".join(compacted).strip()[:max_chars]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sample random pages from build/output/main.pdf"
    )
    parser.add_argument(
        "--pdf",
        default="build/output/main.pdf",
        help="Path to the PDF to sample",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=6,
        help="Number of random pages to sample",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional random seed for reproducible sampling",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=3500,
        help="Maximum characters to print per page",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        raise SystemExit(f"Missing PDF: {pdf_path}")
    if args.count <= 0:
        raise SystemExit("--count must be positive")

    pages = get_page_count(pdf_path)
    if args.count > pages:
        raise SystemExit(f"--count {args.count} exceeds total page count {pages}")

    rng = random.Random(args.seed)
    sample = sorted(rng.sample(range(1, pages + 1), args.count))

    print(f"PAGES {pages}")
    print("SAMPLE", " ".join(map(str, sample)))
    for page in sample:
        print(f"===== PAGE {page} =====")
        print(extract_page_text(pdf_path, page, args.max_chars))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
