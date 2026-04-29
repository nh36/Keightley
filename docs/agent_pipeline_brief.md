# AI Agent Brief: Rebuild *Sources of Shang History* as a Clean LaTeX Edition

## 0. Purpose

Produce a new scholarly LaTeX edition of David N. Keightley, *Sources of Shang History: The Oracle-Bone Inscriptions of Bronze Age China* from the supplied OCR text and page images. The edition must be cleanly typeset, internally cross-referenced, equipped with a proper `.bib` bibliography, and modernised from Wade-Giles romanisation to Hanyu Pinyin where appropriate.

This is not a simple OCR-cleaning job. Treat it as a controlled digital edition project with version control, source-image anchoring, audit trails, and human review gates.

## 1. Non-negotiable principles

1. Preserve the author's argument, wording, structure, notes, numbering, and scholarly apparatus unless an explicit editorial decision says otherwise.
2. Do not make silent global changes. Every systematic change, especially Wade-Giles to Pinyin conversion, must be logged.
3. Keep a path back to the source page for every section, footnote, table, figure, bibliography item, and index/finding-list entry.
4. Separate automation from judgement. The agent may propose and implement changes, but uncertain cases must be marked for review rather than guessed.
5. Use Git from the beginning. Each stage should be committed separately: ingest, OCR cleanup, structure, bibliography, romanisation, figures, tables, cross-references, proofing.
6. Do not overwrite source files. All scripts must be reproducible and idempotent.
7. Build often. The LaTeX project should compile cleanly chapter by chapter before it is assembled as a whole book.

## 2. Required inputs

Minimum inputs:

- `source/Keightley_1978.txt` — OCR text.
- `source/Keightley_1978.pdf` — page-image PDF.
- A full page-image scan of the whole book, not only preliminaries, if figures and tables after p. 182 are to be recovered accurately.

Preferred additional inputs:

- Higher-resolution scan, ideally 400–600 dpi, grayscale or bitonal TIFF/PDF.
- Any existing published PDF from a reliable source.
- Any hand-corrected OCR, if available.
- Any existing bibliography export from WorldCat, Crossref, Zotero, library catalogues, or Google Books.

## 3. Repository layout

Use the following structure.

```text
keightley-sources-latex/
  README.md
  Makefile
  latexmkrc
  project.yml
  source/
    Keightley_1978.txt
    Keightley_1978.pdf
    pages/                    # rendered page images
  build/
    ocr/
    logs/
    qa/
  data/
    pages.csv                 # physical page, printed page, logical page, source image
    toc.yml                   # canonical table of contents
    figures.yml               # figure inventory and source crop data
    tables.yml                # table inventory and source page/crop data
    bibliography_raw.tsv      # raw bibliography extraction
    bibliography_review.tsv   # checked bibliography entries
    citations.tsv             # in-text citation inventory
    romanisation_map.tsv      # Wade-Giles -> Pinyin map
    romanisation_decisions.tsv
    abbreviations.yml
    oracle_bone_refs.tsv
    index_raw.tsv
    finding_list_raw.tsv
  scripts/
    00_render_pages.py
    01_align_ocr_to_pages.py
    02_segment_book.py
    03_clean_ocr.py
    04_extract_notes.py
    05_extract_bibliography.py
    06_match_citations.py
    07_detect_wadegiles.py
    08_apply_romanisation.py
    09_extract_figures.py
    10_extract_tables.py
    11_make_crossrefs.py
    12_qa.py
  tex/
    main.tex
    preamble.tex
    macros.tex
    frontmatter/
    chapters/
    appendices/
    backmatter/
    figures/
    tables/
    bibliography/
      keightley.bib
      oracle-collections.bib
  proofs/
    page_proofs/
    chapter_proofs/
    romanisation_reports/
    bibliography_reports/
```

## 4. Recommended toolchain

### Core text and build tools

- Python 3.11+ for scripting.
- `regex`, `pandas`, `lxml`, `beautifulsoup4`, `rapidfuzz`, `unidecode`, `pyyaml`.
- XeLaTeX.
- `biblatex` + `biber` rather than old BibTeX, because the book contains Chinese, Japanese, accented European names, and complex multilingual bibliography. Still store the data in `.bib` files.
- `booktabs`, `longtable`, `tabularx`, `threeparttable`, `graphicx`, `hyperref`, `cleveref`, `imakeidx` or `xindy`.


### Bibliography tools

- Zotero or Better BibTeX where human checking is convenient.
- Crossref only for modern article DOIs; do not expect complete DOI coverage for older sinological items.
- WorldCat, Library of Congress, HathiTrust, university catalogues, and publisher catalogues for monographs and older East Asian works.
- A local CSL/BibLaTeX style file if needed, but do not solve style questions too early. First make the data correct.

## 5. Build philosophy

Use a semantic intermediate layer. Do not go straight from OCR text to final LaTeX.

Recommended intermediate representation:

- Markdown or TEI-lite for chapter text.
- YAML/TSV for structured inventories: pages, notes, figures, tables, bibliography, citations, romanisation changes.
- LaTeX generated from structured sources where possible, but hand-edit LaTeX where scholarly formatting requires it.

Every generated `.tex` file should include source comments such as:

```tex
% source: printed p. 57, scan page 76, OCR lines approx. 11240-11320
```

These comments are for proofing and should remain in the working source, even if stripped for final release.

## 6. Project phases

### Phase 1: Source audit and page inventory

Goal: establish what the source actually contains.

Tasks:

1. Render the PDF into page images.
2. Create `data/pages.csv` with columns:
   - `scan_page`
   - `printed_page`
   - `logical_page`
   - `section`
   - `image_path`
   - `ocr_start_offset`
   - `ocr_end_offset`
   - `notes`
3. Check whether the supplied PDF is complete. If it is only a sample or only preliminaries, mark all missing pages and request/locate a complete scan before figure/table recovery.
4. Identify page-numbering zones: front matter roman numerals, main text Arabic numerals, figure/table plates, bibliographies, finding list, index.
5. Create a canonical table of contents in `data/toc.yml` from the book's own contents page.

Deliverable:

- `data/pages.csv`
- `data/toc.yml`
- `build/logs/source_audit.md`

Human review gate:

- Confirm page count, page-numbering scheme, and whether all image-bearing pages are available.

### Phase 2: OCR alignment and cleanup

Goal: produce clean text while preserving page anchors.

Tasks:

1. Align OCR text to page images. If the OCR text has page breaks, preserve them as markers.
2. Remove scan artefacts: stray boxes, repeated gutter marks, OCR garbage from page edges, orphaned running heads.
3. Fix systematic OCR errors only after documenting them. Common expected problems:
   - `I`, `l`, `1`, and roman numeral confusion.
   - Wade-Giles apostrophes misread as curly quotes or lost entirely.
   - Diacritics in names and Japanese romanisation.
   - Chinese characters replaced by symbols.
   - Footnote numbers joined to body text.
   - Hyphenated line breaks wrongly retained.
4. Preserve authorial punctuation unless it is clearly OCR damage.
5. Put uncertain readings in a review marker:

```tex
\ednote{CHECK OCR: source p. 148, unclear graph/title}
```

or, in the intermediate source:

```markdown
<!-- CHECK OCR: source p. 148, unclear graph/title -->
```

Deliverable:

- `build/ocr/cleaned_page_aligned.md`
- `build/logs/ocr_cleanup_rules.md`

Human review gate:

- Proof a sample of at least one front-matter page, one ordinary prose page, one note-heavy page, one bibliography page, one table page, and one index page.

### Phase 3: Structural segmentation

Goal: transform the OCR stream into a book structure.

Tasks:

1. Split into:
   - title pages
   - dedication
   - epigraph
   - contents
   - list of figures and tables
   - abbreviations
   - preface and postscript
   - preamble
   - chapters 1–5
   - appendices 1–5
   - figures
   - tables
   - Bibliography A
   - Bibliography B
   - finding list
   - index
2. Convert headings into semantic LaTeX:
   - `\chapter{}`
   - `\section{}`
   - `\subsection{}`
   - `\subsubsection{}` where necessary.
3. Preserve original section numbers where they are meaningful. For example:

```tex
\section{Pyro-Scapulimancy as a Culture Trait}\label{sec:pyro-scapulimancy}
```

If the original printed number must be visible, define a macro:

```tex
\newcommand{\origsecnum}[1]{\textup{#1}\quad}
```

4. Convert internal references such as `sec. 3.7`, `ch. 4`, `appendix 4`, `table 38`, and `fig. 21` to LaTeX cross-references only after labels are created.

Deliverable:

- `tex/frontmatter/*.tex`
- `tex/chapters/ch01.tex` etc.
- `tex/appendices/app01.tex` etc.
- `tex/backmatter/*.tex`

Human review gate:

- Confirm that the generated table of contents matches the printed table of contents before typography is refined.

### Phase 4: Footnotes and end-of-page notes

Goal: reconstruct all notes accurately.

Tasks:

1. Detect note references in the body and note text at page bottoms.
2. Convert them into inline `\footnote{...}` calls.
3. Preserve note numbering by chapter/frontmatter unit unless the original uses continuous numbering in a section.
4. Check every note reference has exactly one note body.
5. Check every note body has exactly one anchor.
6. Do not merge note paragraphs unless the source image confirms they belong together.
7. For notes containing bibliography citations, leave citation conversion to Phase 5.

Deliverable:

- Chapter `.tex` files with integrated footnotes.
- `build/qa/footnote_inventory.tsv` with columns `unit`, `note_no`, `source_page`, `anchor_context`, `status`.

Human review gate:

- Manually proof all notes in the Preface, Preamble, and one full chapter before scaling up.

### Phase 5: Bibliography and citation reconstruction

Goal: replace informal author-year text references with a correct `.bib` database and reliable LaTeX citation commands.

The book has at least two distinct bibliographic zones:

1. Bibliography A: oracle-bone collections cited and their abbreviations.
2. Bibliography B: other works cited.

Treat these differently.

#### 5.1 Bibliography B

Tasks:

1. Extract each entry into `data/bibliography_raw.tsv`.
2. Parse fields:
   - author/editor
   - year
   - title
   - container title
   - volume/issue
   - pages
   - publisher
   - place
   - language/script fields
   - notes
   - DOI/URL/identifier, if verified
3. Create stable BibLaTeX keys. Suggested pattern:

```text
SurnameYYYYShortTitle
Chang1968Archaeology
Keightley1978Sources
Takashima1977Survival
```

4. Do not invent missing data. Use `note = {CHECK: ...}` for unresolved cases.
5. Verify entries against authoritative sources where possible.
6. Preserve Chinese and Japanese titles in Unicode. Add Pinyin romanisation in a controlled field if needed:

```bibtex
@book{Chen1956YinxuBuci,
  author       = {Chen, Mengjia},
  title        = {Yinxu buci zongshu},
  titleaddon   = {殷墟卜辭綜述},
  location     = {Beijing},
  publisher    = {Kexue chubanshe},
  date         = {1956},
  langid       = {chinese},
  keywords     = {converted-from-wadegiles, checked}
}
```

7. Add DOIs only when verified from a reliable source. Many older sinological works will not have DOIs.

#### 5.2 Bibliography A and abbreviations

Tasks:

1. Extract abbreviations into `data/abbreviations.yml` and `tex/backmatter/abbreviations.tex`.
2. Treat oracle-bone collection abbreviations as a controlled list, not merely ordinary bibliography.
3. Where abbreviations are cited in the text, use a macro rather than ordinary citation if the reference is to an inscription number, rubbing number, drawing number, or plate.

Possible macros:

```tex
\newcommand{\obcol}[1]{\textit{#1}}
\newcommand{\obref}[2]{\textit{#1}~#2}
\newcommand{\shimaref}[1]{S#1}
```

Examples:

```tex
\obref{Ping-pien}{12--21}
\shimaref{279.2--3}
```

#### 5.3 In-text citations

Tasks:

1. Extract all candidate citations into `data/citations.tsv`.
2. Match every citation to a `.bib` key.
3. Convert author-year citations:

```tex
Soper (1966), pp. 356--358
```

into one of:

```tex
\textcite[356--358]{Soper1966Problems}
\parencite[356--358]{Soper1966Problems}
```

4. Preserve original prose where converting to citation macros would damage readability.
5. Check for all unmatched references.
6. Compile with `biber` and fail the build if any citation remains undefined.

Deliverables:

- `tex/bibliography/keightley.bib`
- `tex/bibliography/oracle-collections.bib`, if useful
- `data/citations.tsv`
- `build/qa/unmatched_citations.tsv`
- `build/qa/bibliography_verification.md`

Human review gate:

- Review all bibliography entries with Chinese/Japanese titles and all entries where publication place, journal, volume, issue, or page range is uncertain.

### Phase 6: Wade-Giles to Pinyin conversion

Goal: modernise Chinese romanisation while avoiding false changes.

This phase is high risk. Wade-Giles conversion is not a one-to-one regular-expression problem. It requires a lexicon, context, and review.

#### 6.1 Scope decision

Create an explicit policy in `data/romanisation_policy.md` before replacing anything.

Default policy:

1. Convert Chinese personal names, place names, dynastic terms, book titles, journal titles, and romanised Chinese phrases from Wade-Giles to Hanyu Pinyin.
2. Preserve non-Chinese romanisation systems such as Japanese, Korean, Sanskrit, Tibetan, Mongolian, Vietnamese, and European names.
3. Preserve quoted historical titles if there is a reason to display the older form, but add Pinyin in brackets or in a note if required.
4. In bibliography entries, use Pinyin as the main romanisation, retain original Chinese characters where known, and preserve the old form in a `note` or `origtitle` field if necessary for identification.
5. Do not convert abbreviations or call numbers if they function as established sigla.
6. Do not change oracle-bone collection abbreviations unless the abbreviation list itself is being editorially modernised.

#### 6.2 Candidate detection

Build `data/romanisation_map.tsv` with columns:

```text
source_form    target_pinyin    category    confidence    rule_or_source    first_page    notes
```

Categories:

- `person`
- `place`
- `dynasty_period`
- `book_title`
- `journal_title`
- `technical_term`
- `publisher`
- `ambiguous`
- `do_not_change`

Confidence levels:

- `A`: exact known mapping, safe in context.
- `B`: likely mapping, needs quick human check.
- `C`: ambiguous; do not replace automatically.
- `D`: do not change.

Examples of likely mappings to review:

```text
P'an Keng    Pan Geng      person/king       B
Wu Ting      Wu Ding       person/king       A
Ti Hsin      Di Xin        person/king       A
Hsiao-t'un   Xiaotun       place             A
An-yang      Anyang        place             A
Shih-chi     Shiji         book_title        A
Shang-shu    Shangshu      book_title        A
Chou         Zhou          dynasty/name      B
Ch'en        Chen          surname           B
Tung         Dong          surname           B
Hsü          Xu            surname           B
K'ao-ku      Kaogu         journal_title     A
Wen-wu       Wenwu         journal_title     A
chia-ku-wen  jiaguwen      technical_term    A
Yin-hsü      Yinxu         place/term        A
```

The actual map must be generated from the text, not limited to this sample.

#### 6.3 Replacement method

1. Tokenise the text and identify candidate Wade-Giles strings.
2. Match candidates against `romanisation_map.tsv`.
3. Apply only confidence `A` automatically.
4. Emit a diff for confidence `B`; apply only after review.
5. Never apply confidence `C` automatically.
6. Keep a replacement log in `data/romanisation_decisions.tsv`:

```text
file    line    source_page    original    replacement    category    confidence    reviewer    date    note
```

7. Pay special attention to apostrophes. Wade-Giles aspiration apostrophes are not the same as Pinyin syllable-boundary apostrophes. Do not globally remove apostrophes.
8. Preserve authorial discussion of romanisation conventions if the text comments on them.

Deliverables:

- `data/romanisation_policy.md`
- `data/romanisation_map.tsv`
- `data/romanisation_decisions.tsv`
- `proofs/romanisation_reports/chapter_*.md`

Human review gate:

- Review all changed proper names in bibliography, notes, captions, index, and finding list.

### Phase 7: Figures and images

Goal: reinsert all figures and image material missing from OCR.

Tasks:

1. Use the printed List of Figures to create `data/figures.yml`.
2. For each figure, record:
   - figure number
   - caption
   - source printed page or plate location
   - scan page
   - crop coordinates
   - image file path
   - rights/permission status
   - whether figure is photographic, drawing, map, chart, or diagram
   - whether it should be reproduced as image or redrawn
3. Extract/crop figures from page images at high resolution.
4. Deskew, clean margins, and normalise contrast conservatively.
5. Save master crops as TIFF or PNG. Use PDF/PNG for LaTeX inclusion.
6. For maps, charts, and line diagrams, consider redrawing as vector graphics only if this improves legibility and does not introduce errors.
7. Insert with stable labels:

```tex
\begin{figure}[p]
  \centering
  \includegraphics[width=.9\textwidth]{figures/fig_021_flow_chart_deciphering.png}
  \caption{A flow chart for deciphering inscriptions}
  \label{fig:flow-chart-deciphering}
\end{figure}
```

8. Convert all references such as `fig. 21` to `\cref{fig:flow-chart-deciphering}` where appropriate.

Deliverables:

- `tex/figures/*.tex`
- `tex/figures/*.png` or `.pdf`
- `data/figures.yml`
- `build/qa/missing_figures.tsv`

Human review gate:

- Check every figure against the original source page for caption, numbering, crop completeness, and legibility.

### Phase 8: Tables

Goal: reconstruct all tables as real LaTeX tables, not screenshots, except where impossible.

Tasks:

1. Use the printed List of Tables to create `data/tables.yml`.
2. Extract tables from OCR and page images.
3. Convert each table to structured CSV/TSV first.
4. Manually verify row and column alignment against the image.
5. Typeset using `booktabs`, `longtable`, or `threeparttable`.
6. Preserve table notes and unusual symbols.
7. Add labels:

```tex
\begin{table}
\caption{The five periods}
\label{tab:five-periods}
...
\end{table}
```

8. Convert references such as `table 38` to `\cref{tab:revised-short-chronology}`.

Deliverables:

- `data/tables/table_*.tsv`
- `tex/tables/table_*.tex`
- `build/qa/table_checklist.tsv`

Human review gate:

- Tables must be visually checked cell by cell. This is a no-shortcut task.

### Phase 9: Index and finding list

Goal: preserve and, if possible, regenerate backmatter accurately.

Tasks:

1. Extract the printed index into `data/index_raw.tsv`.
2. Extract the finding list into `data/finding_list_raw.tsv`.
3. Decide whether the new edition will:
   - preserve the old printed index page numbers, or
   - regenerate a new index based on the new LaTeX pagination.
4. Preferred approach for a new edition:
   - preserve the original index as a historical reference only if necessary;
   - otherwise embed `\index{}` commands and regenerate with `xindy` or `makeindex`.
5. Because automatic index regeneration is error-prone, start by typesetting the original index faithfully; later add semantic index markers as a separate enhancement.
6. The finding list of inscriptions/oracle bones is a scholarly apparatus and should be proofed independently from the ordinary index.

Deliverables:

- `tex/backmatter/finding-list.tex`
- `tex/backmatter/index.tex` or generated index workflow
- `data/index_raw.tsv`
- `data/finding_list_raw.tsv`

Human review gate:

- Check all inscription numbers, collection abbreviations, and page references. OCR will be especially unreliable here.

### Phase 10: LaTeX design and macro layer

Goal: keep the LaTeX source clean and semantic.

Recommended engine:

- LuaLaTeX or XeLaTeX.

Recommended macro areas:

```tex
% macros.tex
\newcommand{\booktitle}[1]{\textit{#1}}
\newcommand{\journal}[1]{\textit{#1}}
\newcommand{\term}[1]{\emph{#1}}
\newcommand{\chinese}[1]{#1}
\newcommand{\japanese}[1]{#1}
\newcommand{\obref}[2]{\textit{#1}~#2}
\newcommand{\shimaref}[1]{S#1}
\newcommand{\missing}[1]{\textsuperscript{[missing: #1]}}
\newcommand{\restored}[1]{[#1]}
\newcommand{\ednote}[1]{\textbf{[ED: #1]}}
```

Typography:

- Use a book class or `memoir`/`scrbook`.
- Use a font with strong Latin, Greek, and IPA support, plus CJK fallback.
- Do not let typography decisions obscure textual cleanup. First get a correct build; refine layout later.

Potential packages:

```tex
\usepackage{fontspec}
\usepackage{xeCJK}        % if XeLaTeX; use luatexja if LuaLaTeX
\usepackage{csquotes}
\usepackage{microtype}
\usepackage{graphicx}
\usepackage{booktabs,longtable,tabularx,threeparttable}
\usepackage[backend=biber,style=authoryear]{biblatex}
\usepackage{hyperref}
\usepackage{cleveref}
\usepackage{imakeidx}
```

Build:

```bash
latexmk -xelatex tex/main.tex
biber main
latexmk -xelatex tex/main.tex
```

or configure `latexmkrc` to handle this automatically.

### Phase 11: Cross-references and numbering

Goal: make the book internally navigable.

Tasks:

1. Label every chapter, section, appendix, table, and figure.
2. Convert internal references carefully.
3. Do not convert page references to `\pageref{}` unless the reference is to the new edition's pagination. If the author refers to the old printed page, make that explicit.
4. Compile and fail on:
   - undefined references
   - duplicate labels
   - missing bibliography entries
   - unresolved `CHECK`, `TODO`, or `ednote` markers unless in a draft build.
5. Produce `build/qa/crossrefs.md` listing:
   - all labels
   - all references
   - unresolved items
   - references deliberately left literal.

Deliverable:

- Clean LaTeX cross-reference build.

Human review gate:

- Review all converted internal references in the Preface, Chapter 3, Chapter 4, appendices, and backmatter. These are likely to contain dense cross-references.

### Phase 12: Quality assurance

Run the following checks before considering any chapter complete.

#### Textual checks

- Compare cleaned text against page images page by page.
- Check proper names, dates, page ranges, titles, and Chinese characters.
- Check all footnotes.
- Search for OCR residue:

```text
☐ ] [ stray box characters
I.2 vs 1.2 errors
p. vs pp. errors
hyphenated line-break leftovers
broken Chinese characters
unmatched parentheses
unmatched quotation marks
```

#### LaTeX checks

- `latexmk` completes with no undefined citations or references.
- No overfull boxes in final proof unless consciously accepted.
- Tables fit and remain legible.
- Figures appear near the intended positions or in a consistent plate section.
- `hyperref` links work.

#### Bibliographic checks

- Every citation has a `.bib` entry.
- Every bibliography entry is cited, unless intentionally retained.
- DOI fields are verified, not guessed.
- Chinese/Japanese titles are checked in original script where possible.
- Pinyin conversion is applied consistently but not blindly.

#### Romanisation checks

- All automatic replacements have a log entry.
- Ambiguous forms remain marked for review.
- Bibliography, notes, captions, index, and finding list have been checked separately.

#### Image/table checks

- Every figure in the List of Figures appears in the new edition.
- Every table in the List of Tables appears in the new edition.
- Crops are complete; captions match; labels and references resolve.

## 7. Suggested agent workflow by chapter

For each chapter or major unit:

1. Extract the unit from page-aligned OCR.
2. Create an intermediate Markdown/TEI file with source-page markers.
3. Clean OCR mechanically.
4. Convert headings and paragraphs to LaTeX.
5. Reconstruct footnotes.
6. Extract citation candidates and match them to `.bib` keys.
7. Detect Wade-Giles candidates.
8. Apply approved romanisation replacements.
9. Insert figure/table placeholders.
10. Compile the chapter in isolation.
11. Produce a proof report:

```markdown
# Proof report: Chapter 3

## Pages covered
printed pp. 57–90; scan pp. __–__

## OCR issues resolved
...

## Open checks
...

## Romanisation changes
...

## Bibliography/citation issues
...

## Figures/tables
...
```

12. Commit the chapter.

Suggested commit messages:

```text
ingest source files
render and inventory source pages
segment chapter 1
reconstruct chapter 1 footnotes
convert chapter 1 citations
apply reviewed pinyin conversions chapter 1
insert chapter 1 figures and tables
proof chapter 1 against scan
```

## 8. Risk register

High-risk areas:

1. The supplied PDF may not include all pages, figures, and tables. Do not attempt final image recovery without a complete scan.
2. Chinese and Japanese bibliography entries will be corrupted by OCR and must be checked from images and external catalogues.
3. Wade-Giles to Pinyin conversion can damage non-Chinese names, Japanese titles, established abbreviations, and quotation contexts.
4. Footnote reconstruction is likely to fail on pages where notes run across page breaks.
5. Tables after p. 182 are likely to require manual cell-by-cell reconstruction.
6. The index and finding list are numerically dense and especially vulnerable to OCR errors.
7. Oracle-bone collection references are not ordinary bibliographic citations. Do not feed them blindly into author-year citation conversion.
8. Page references in the original text may refer to original pagination, not the new edition's pagination. Decide policy before converting them.

## 9. Editorial decisions to make early

The agent should create `project.yml` and record these decisions:

```yaml
edition:
  purpose: private scholarly working edition
  distribution: unknown
  romanisation: pinyin
  preserve_wadegiles_in_notes: false
  bibliography_system: biblatex-biber
  citation_style: authoryear
  cjk_script: preserve_original_characters_where_available
  index_policy: preserve_original_first_then_regenerate_later
  page_reference_policy: preserve_original_literal_references_unless_crossref_is_safe
  figures_policy: crop_from_scan_unless_redrawing_is_approved
  table_policy: reconstruct_as_latex_not_images
  proofing_standard: page_by_page_against_scan
```

## 10. Definition of done

The project is complete when:

1. The full book compiles from `tex/main.tex` with no undefined citations, undefined references, duplicate labels, or unresolved editorial notes.
2. All chapters, appendices, bibliographies, figures, tables, finding list, and index are present.
3. The table of contents, list of figures, and list of tables are generated by LaTeX or match the original by deliberate policy.
4. All bibliography entries have been parsed, checked, and placed in `.bib` form.
5. All in-text citations are either converted to citation commands or deliberately left literal and logged.
6. Wade-Giles to Pinyin conversion has been applied consistently according to a reviewed mapping table.
7. All automatic romanisation changes are logged.
8. All figures are inserted, labelled, captioned, and cross-referenced.
9. All tables are reconstructed, labelled, captioned, and cross-referenced.
10. A proof report exists for every chapter and backmatter unit.
11. A final QA report lists remaining editorial uncertainties, if any.

## 11. First actions for the agent

Run these steps first:

1. Create the repository structure.
2. Copy source files into `source/`.
3. Render PDF pages to `source/pages/`.
4. Create `data/pages.csv`.
5. Produce `build/logs/source_audit.md` stating whether the scan is complete.
6. Extract the table of contents, List of Figures, List of Tables, and List of Abbreviations into structured YAML/TSV.
7. Stop for review if the scan is incomplete.

Do not begin full romanisation conversion or bibliography rewriting until the page inventory and segmentation are stable.
