# Copilot instructions: Keightley LaTeX edition

## What this repository is

A scholarly digital-edition project to rebuild David N. Keightley, *Sources of Shang History: The Oracle-Bone Inscriptions of Bronze Age China* (1978) as a clean, cross-referenced LaTeX edition from OCR text and page scans, with Wade-Giles romanisation modernised to Hanyu Pinyin.

The repository is currently at **inception stage**. It contains:

- `Keightley, D. 1978.pdf` / `.txt` — primary source (the 1978 book) and its OCR.
- `Keightley, D. 2012 Working for His Majesty.pdf` / `.txt` — secondary source.
- `keightley_latex_agent_pipeline.md` — the **authoritative project brief**. Read this before doing anything substantive. It defines the repo layout, toolchain, phases, deliverables, and editorial policy.

There is no code, build, or git history yet. Treat the brief as the spec.

## Workflow rule (project-specific override of the brief)

The brief mentions human review gates between phases. **This project does not
use human-in-the-loop gates.** Replace any "stop for review" / "ask the
reviewer" step with an automated verification harness (see `scripts/12_qa.py`)
that fails the build on inconsistencies. Spend tokens on writing better
software rather than on ceremony around manual checks.

## Two OCRs are available — use both

The book has been OCR'd twice and both versions are kept:

- **Google Vision** (supplied) — `source/Keightley_1978.txt`. Form-feed
  delimited (one chunk per scan page; 326 chunks for 326 pages).
- **Tesseract 5.5.2** with `eng+chi_tra` (Phase 2 re-OCR) —
  `build/ocr/pages/p_NNNN.txt`, plus per-token confidence in
  `p_NNNN.tsv` and a summary in `build/ocr/MANIFEST.tsv`.

Tesseract is the primary source for clean prose. Google Vision is the
fallback / cross-check for: low-confidence Tesseract regions, CJK glyphs,
italics, dense layouts (tables, the Bibliography A abbreviations list).
**Downstream phases (esp. 5 bibliography, 7 figures, 8 tables, 11 proofing)
should consult both and prefer the more plausible reading per token.** Use
`scripts/05_dual_ocr_lookup.py NNN [--diff]` to compare a page side-by-side.

Note: `data/pages.csv` columns `ocr_start_offset` / `ocr_end_offset` are
**character** offsets into the decoded Google Vision string, not byte
offsets. Either slice the `.read_text()` result with them, or just split
`source/Keightley_1978.txt` on `\f` and index by scan page (what
`05_dual_ocr_lookup.py` does). `scripts/12_qa.py` enforces a round-trip
between the two so this can't drift.

## Read first, then act

Before proposing changes, open `keightley_latex_agent_pipeline.md`. Specifically consult:

- §3 Repository layout — the canonical directory structure to create (`source/`, `build/`, `data/`, `scripts/`, `tex/`, `proofs/`).
- §4 Toolchain — Python 3.11+, XeLaTeX/LuaLaTeX, `biblatex` + `biber`, `latexmk`.
- §6 Phases 1–12 — work proceeds in order; each phase has a human review gate.
- §9 Editorial decisions — values must be recorded in `project.yml` before downstream work.
- §11 First actions — page render, `data/pages.csv`, source audit, then stop for review.

## Build and run (target state)

Once the `tex/` tree exists, the build is:

```bash
latexmk -xelatex tex/main.tex
biber main
latexmk -xelatex tex/main.tex
```

Compile chapter-by-chapter before assembling the whole book (brief §5, §7). Configure `latexmkrc` to drive biber automatically. Builds must fail on undefined citations, undefined references, and duplicate labels (§11, §12).

Scripts under `scripts/` are numbered `00_…` through `12_…` and are expected to be **idempotent** and reproducible from raw `source/` inputs.

## Non-negotiable conventions (project-specific)

These are easy to violate and are explicitly forbidden by the brief:

1. **Never overwrite source files.** `source/` is read-only input; outputs go to `build/`, `data/`, `tex/`, `proofs/`.
2. **No silent global edits.** Every systematic change (especially Wade-Giles → Pinyin) must produce a row in a log TSV (`data/romanisation_decisions.tsv`, etc.).
3. **Every generated `.tex` file carries a source-page comment**, e.g. `% source: printed p. 57, scan page 76, OCR lines approx. 11240-11320`. Keep these in working source.
4. **Wade-Giles → Pinyin is gated by confidence levels** in `data/romanisation_map.tsv`:
   - `A` apply automatically; `B` apply only after review; `C` never auto-apply; `D` do not change.
   - Do not convert Japanese, Korean, Sanskrit, Tibetan, Mongolian, Vietnamese, or European names. Do not strip Wade-Giles aspiration apostrophes globally.
5. **Two distinct bibliographies.** Bibliography A = oracle-bone collection abbreviations (treated as sigla, often via macros like `\obref`, `\shimaref`); Bibliography B = ordinary works in `tex/bibliography/keightley.bib`. Do not feed oracle-bone references into author-year citation conversion.
6. **BibLaTeX keys** follow `SurnameYYYYShortTitle` (e.g. `Keightley1978Sources`). Never invent missing bibliographic data — use `note = {CHECK: ...}` instead.
7. **Uncertain readings are marked, not guessed.** Use `\ednote{CHECK OCR: ...}` in LaTeX or `<!-- CHECK OCR: ... -->` in intermediate Markdown. The build should fail on unresolved markers in non-draft mode.
8. **Page references** in the original text refer to the 1978 pagination. Do not blindly convert to `\pageref{}` — preserve as literal references unless cross-ref is provably safe (§11, risk §8).
9. **Tables are reconstructed as real LaTeX** (`booktabs`/`longtable`/`threeparttable`), not screenshots. Figures are cropped from scans unless redrawing is explicitly approved.
10. **Commit per phase.** Suggested commit granularity is in §7 of the brief (ingest, segment chapter N, reconstruct chapter N footnotes, …). Use git from the start.

## Editorial defaults (from §9)

Romanisation: Pinyin. Bibliography: `biblatex` + `biber`, authoryear style. CJK: preserve original characters where available. Index policy: preserve original first, regenerate later. These belong in `project.yml`; do not change them ad hoc.

## When in doubt

Stop and surface the question rather than silently choosing. The brief explicitly designs human review gates between phases; respect them.
