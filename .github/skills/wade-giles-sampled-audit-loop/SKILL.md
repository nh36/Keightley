---
name: wade-giles-sampled-audit-loop
description: Repeat the Keightley sampled PDF audit workflow for remaining Wade-Giles and mixed-script cleanup. Use this when asked to do another random page pass, apply only safe fixes, refresh data/wade_giles_audit.tsv, and optionally commit and push.
---

# Wade-Giles sampled audit loop

Use this skill for the recurring cleanup loop in this repository: sample random pages from the built PDF, trace visible leftovers back to source, apply only conservative fixes, refresh the live Wade-Giles audit TSV, and finish with git operations if the user asked for them.

## Repository-specific rules

Follow these editorial constraints throughout:

1. Use **traditional Chinese characters only**.
2. **Do not convert Japanese scholar names** into Chinese characters.
3. Avoid false positives. If a scholar name or title is not firmly established, leave it alone.
4. Prefer fixing:
   - mixed-script artifacts like `成 Te-k'un`
   - exact sampled leftovers visible in the current PDF
   - clearly wrong simplified forms in otherwise established Chinese names or places
5. Keep `data/wade_giles_audit.tsv` aligned with the current chapter text, but preserve curated `pinyin` and `notes` for surviving rows.
6. When a term disappears from the live audit, retire that row into `data/wade_giles_resolved_history.tsv` so the two TSVs stay in sync.

## Standard loop

1. Build the current PDF if needed:

   ```bash
   ./scripts/build.sh
   ```

2. Sample random pages from `build/output/main.pdf` with the helper script in this skill:

   ```bash
   python3 .github/skills/wade-giles-sampled-audit-loop/sample_random_pdf_pages.py
   ```

   By default this samples 6 pages and prints extract text for each page. You can pass `--seed` for reproducibility or `--count` to change the sample size.

3. Inspect the sampled pages and trace any visible Wade-Giles, mixed-script, or simplified/traditional problems back into the relevant `tex/chapters/`, `tex/appendices/`, or `tex/frontmatter/` files.

4. Apply only **safe, exact** fixes. Reuse already-established conversions from this repository when available.

5. Rebuild and rerun the repo tidiness regression:

   ```bash
   ./scripts/build.sh
   python3 -m pytest tests/regression_repo_structure.py -q
   ```

6. Refresh the audit inventory with the helper script in this skill:

   ```bash
   python3 .github/skills/wade-giles-sampled-audit-loop/refresh_wade_giles_audit.py
   ```

    This regenerates the live audit using `scripts/audit_wade_giles.py`, merges it back into `data/wade_giles_audit.tsv` while preserving the existing `pinyin` and `notes` columns, and appends any rows that disappeared from the live audit into `data/wade_giles_resolved_history.tsv`.

7. If the user asked for the full loop, commit and push the resulting changes. Keep the commit focused on that pass. A typical message is:

   ```bash
   git add tex/ data/wade_giles_audit.tsv data/wade_giles_resolved_history.tsv .github/skills/wade-giles-sampled-audit-loop
   git commit -m "Add sampled Wade-Giles audit skill"
   git push
   ```

## What to report back

Summarize:

- which pages were sampled
- what safe fixes were made
- whether the live TSV was refreshed
- whether rows were retired into the cumulative resolved-history TSV
- whether commit/push was completed

If a sample yields only ambiguous cases, say so plainly and do not force conversions.
