# Sources of Shang History — LaTeX edition (working repository)

A scholarly LaTeX edition of David N. Keightley, *Sources of Shang History: The
Oracle-Bone Inscriptions of Bronze Age China* (Berkeley: University of
California Press, 1978), reconstructed from OCR text and page scans.

This is a working repository. It is not a published edition.

## Layout

```
source/      # Read-only inputs: 1978 PDF, OCR text, rendered page images.
reference/   # Secondary materials (e.g. Keightley 2012 Working for His Majesty).
docs/        # Project brief and editorial documentation.
data/        # Structured inventories: pages, TOC, figures, tables, romanisation maps.
scripts/     # Numbered Python pipeline scripts (00_…, 01_…, …).
tex/         # LaTeX source tree (frontmatter, chapters, appendices, backmatter, …).
build/       # Generated artefacts, OCR cleanup output, logs, QA reports. Gitignored.
proofs/      # Per-chapter / per-page proof reports.
```

The authoritative project specification is `docs/agent_pipeline_brief.md`.
Editorial defaults are recorded in `project.yml` (§9 of the brief).

## Building (target state)

```
latexmk -xelatex tex/main.tex
biber main
latexmk -xelatex tex/main.tex
```

The build is not yet wired up. Phase 1 (source audit and page inventory) is in
progress; see `build/logs/source_audit.md` once produced.

## Provenance

The 1978 PDF and OCR text are from the user's personal library and are used
here only as input for a private working edition.
