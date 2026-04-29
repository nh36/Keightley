#!/usr/bin/env python3
"""Phase 5 step A (v2): re-OCR bibliography pages with --psm 6.

The bibliography uses a hanging-indent layout (author header + indented year
sub-entries).  --psm 6 ("single uniform block of text") preserves this layout
better than the default page-segmenter, which mangles reading order.

Output: build/ocr/bibliography/p_NNNN.txt (overwrites the v1 column-split outputs).
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT / "source" / "pages"
OUT_DIR = ROOT / "build" / "ocr" / "bibliography"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BIB_SCANS = list(range(275, 303))


def main() -> None:
    # Drop v1 column-split intermediate files
    for stale in OUT_DIR.glob("p_*_[LR].*"):
        stale.unlink()

    for scan in BIB_SCANS:
        src = PAGES_DIR / f"p_{scan:04d}.png"
        if not src.exists():
            print(f"missing: {src}")
            continue
        # Copy locally to avoid the long-path tesseract bug we hit earlier
        local = OUT_DIR / src.name
        shutil.copy(src, local)
        out_base = OUT_DIR / f"p_{scan:04d}"
        cmd = ["tesseract", local.name, out_base.name,
               "-l", "eng+chi_tra", "--psm", "6"]
        subprocess.run(cmd, cwd=str(OUT_DIR), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        local.unlink()
        size = (OUT_DIR / f"p_{scan:04d}.txt").stat().st_size
        print(f"[{scan}] {size} bytes")


if __name__ == "__main__":
    main()
