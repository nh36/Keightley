#!/usr/bin/env python3
"""Re-OCR each rendered page image with Tesseract.

Output structure:
  build/ocr/pages/p_NNNN.txt           (plain text, one per page)
  build/ocr/pages/p_NNNN.tsv           (Tesseract per-token TSV with confidence)
  build/ocr/MANIFEST.tsv               (page, text_chars, mean_conf, low_conf_tokens)
  build/ocr/Keightley_1978.tesseract.txt  (concatenated, form-feed separated, parallel
                                       to source/Keightley_1978.txt)

Languages: eng+chi_tra (the 1978 book uses traditional characters in CJK
quotations and the abbreviations list). Page segmentation mode 1 (auto with
orientation/script detection) handles mixed layouts.

Idempotent: skips pages whose .txt and .tsv already exist (use --force to
re-run).
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT / "source" / "pages"
OUT_DIR = ROOT / "build" / "ocr" / "pages"
MANIFEST = ROOT / "build" / "ocr" / "MANIFEST.tsv"
CONCAT = ROOT / "build" / "ocr" / "Keightley_1978.tesseract.txt"

LANGS = "eng+chi_tra"
PSM = "1"


def ocr_page(png: Path, force: bool) -> tuple[Path, Path]:
    txt = OUT_DIR / (png.stem + ".txt")
    tsv = OUT_DIR / (png.stem + ".tsv")
    if not force and txt.exists() and tsv.exists():
        return txt, tsv
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = OUT_DIR / png.stem
    # Plain text
    subprocess.check_call(
        ["tesseract", str(png), str(base), "-l", LANGS, "--psm", PSM, "txt"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    # TSV with per-token confidence
    subprocess.check_call(
        ["tesseract", str(png), str(base), "-l", LANGS, "--psm", PSM, "tsv"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return txt, tsv


def summarise(tsv: Path) -> tuple[int, float, int]:
    """Return (token_count, mean_confidence, low_conf_count)."""
    n, total, low = 0, 0.0, 0
    with tsv.open() as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for row in rdr:
            try:
                conf = float(row.get("conf", -1))
            except ValueError:
                continue
            if conf < 0:
                continue
            text = (row.get("text") or "").strip()
            if not text:
                continue
            n += 1
            total += conf
            if conf < 60:
                low += 1
    return n, (total / n if n else 0.0), low


def run_one(args_tuple) -> dict:
    png_str, force = args_tuple
    png = Path(png_str)
    txt, tsv = ocr_page(png, force)
    n, mean_conf, low = summarise(tsv)
    return {
        "scan_page": int(png.stem.split("_")[1]),
        "tokens": n,
        "mean_conf": f"{mean_conf:.1f}",
        "low_conf_tokens": low,
        "chars": len(txt.read_text(errors="replace")),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="OCR only the first N pages")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 4) - 1))
    args = ap.parse_args()

    pages = sorted(PAGES_DIR.glob("p_*.png"))
    if args.limit:
        pages = pages[: args.limit]
    if not pages:
        sys.exit("no rendered pages in source/pages/")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    done = 0
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(run_one, (str(p), args.force)): p for p in pages}
        for fut in as_completed(futs):
            rows.append(fut.result())
            done += 1
            if done % 25 == 0 or done == len(pages):
                print(f"  ocr {done}/{len(pages)}", flush=True)

    rows.sort(key=lambda r: r["scan_page"])
    concat = [(OUT_DIR / f"p_{r['scan_page']:04d}.txt").read_text(errors="replace") for r in rows]

    with MANIFEST.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(rows)

    CONCAT.write_text("\f".join(concat))
    print(f"manifest: {MANIFEST}")
    print(f"concat:   {CONCAT}  ({len(concat)} pages, {sum(len(c) for c in concat)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
