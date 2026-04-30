# Phase 5 — Bibliography reconstruction: verification report

## Outputs

| Artefact | Path |
| --- | --- |
| Raw bibliography B sub-entries (TSV) | `data/bibliography_raw.tsv` |
| Bibliography B (biblatex) | `tex/bibliography/keightley.bib` |
| Oracle-bone abbreviations (YAML) | `data/abbreviations.yml` |
| Oracle-bone abbreviations (TeX) | `tex/backmatter/abbreviations.tex` |
| In-text citations (1:1 matched, TSV) | `data/citations.tsv` |
| Unmatched / ambiguous citations | `build/qa/unmatched_citations.tsv` |
| Phase 5 log | `build/logs/phase5_bibliography.md` |
| Re-OCR (psm 6) of biblio pages | `build/ocr/bibliography/p_NNNN.txt` |

## Counts (current run)

- Bibliography B: **223 sub-entries**, **89 distinct authors**.
- Bibliography A: **39 abbreviations** parsed.
- In-text citations: **131 matched 1:1** to a bib key; **577 unmatched / ambiguous**.

## Pipeline

`scripts/08a_recoco_bibliography.py` re-OCRs the bibliography pages (scans
275–302) at `--psm 6` (single uniform block of text), which preserves the
hanging-indent column layout much better than the default page-segmenter.

`scripts/08_extract_bibliography.py` parses these page texts:

- **Year sub-entries** detected by `^(?:18|19|20)\d{2}[a-z]?\b`.
- **Author headers** detected by a heuristic on short, capital-led, name-shaped
  lines at column 0 (with explicit rejects for place names, OCR fragments,
  section headings).
- **Continuations** attach to the current sub-entry.

Each parsed (author, year) sub-entry is then **cross-referenced against Google
Vision** OCR (`source/Keightley_1978.txt`, form-feed split):

- The GV chunk for the same scan page is searched for the year token.
- The longest CJK-rich line near each year hit is captured as `gv_title`.
- All distinct CJK runs near the author surname are captured as `gv_cjk`.

When the GV title is appreciably longer than the Tesseract title and contains
CJK or Romaji-with-macrons (`āēīōūĀĒĪŌŪ`), it **replaces** the Tesseract title
in the emitted .bib entry.  Both OCR streams are preserved in
`note = {RAW: <tesseract> ; GV: <gv>}` for Phase 11 proofing.

`scripts/09_intext_citations.py` scans every chapter/appendix .tex file for
`Surname (YYYY)` patterns and matches them against the bib index.  Only 1:1
matches go to `data/citations.tsv`; ambiguous matches and 0-match cases go to
`build/qa/unmatched_citations.tsv`.

## Known limitations (deferred to Phase 11 proofing)

The OCR of the bibliography pages is the noisiest part of the entire book:
- Two-column layout with narrow year column.
- Heavy CJK / Japanese / Wade-Giles content with high glyph confusion.
- Margin glyphs from the binding gutter polluting many lines.

Specific known false positives in the parser output:
- A handful of "authors" are OCR fragments (`BYE FH SiH`, `LPR be`, etc.) where
  scrambled CJK fragments at the boundary of one entry briefly look like a
  capital-led roman name.  Their sub-entries are wrongly attached and need
  to be reattributed during Phase 11.
- Some bib keys have generic short titles (`Akatsuka1955Kohon`) where the
  first capital-led word in the OCR title was used as the short title; these
  should be hand-curated against the printed page.
- The `note = {RAW:...; GV:...}` field is intentionally large and ugly: it is
  the proofing checklist, not the published output.

## Macros

`tex/preamble.tex` now defines:

- `\obcol{ABBR}` — typeset an oracle-bone collection abbreviation in small caps.
- `\obref{ABBR}{NUM}` — typeset a collection abbreviation + reference number.
- `\shimaref{NUM}` — typeset a Shima Kunio reference index value.

`\addbibresource{bibliography/keightley.bib}` is wired in.

## Phase 5 → Phase 6 / Phase 11 hand-off

- Phase 6 (Wade-Giles → Pinyin) operates on chapter/appendix text *and* on
  bibliography author names; this conversion is best run *after* Phase 11
  proofing has cleaned author surnames.  Until then, conservative pass only.
- Phase 11 proofing should:
  1. Sweep the .bib file using the `note = {RAW: ...; GV: ...}` evidence.
  2. Reattribute orphaned sub-entries from OCR-fragment "authors" to the
     correct preceding author.
  3. Curate `data/abbreviations.yml` against the printed Bibliography A pages
     to remove OCR splits / merges.
  4. Run the unmatched citations TSV by hand to either pick the right
     candidate or add new bib entries.
