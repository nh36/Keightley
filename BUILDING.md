# Building the Keightley Document

This document explains how to build the LaTeX document from source and understand the repository structure.

## Prerequisites

You need a complete TeX Live or MacTeX installation with:
- `xelatex` - XeTeX LaTeX engine (for Unicode and Chinese character support)
- `biber` - Bibliography processor
- XeTeX packages (typically included with full TeX installations)

### Installation

**macOS (with Homebrew):**
```bash
brew install --cask mactex
```

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra
```

**Or download:**
- [TeX Live](https://tug.org/texlive/)
- [MacTeX](https://tug.org/mactex/)

## Building the PDF

### Using the build script (Recommended)

```bash
./scripts/build.sh
```

This will:
1. Validate that `xelatex` is available
2. Run xelatex twice (to resolve cross-references)
3. Generate output at `build/output/main.pdf`

### Manual build

```bash
cd tex
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex  # Second pass for references
```

The output PDF will be in the `tex/` directory; copy it to `build/output/main.pdf` for consistency.

## Repository Structure

```
Keightley/
├── tex/
│   ├── main.tex              # Main document root
│   ├── chapters/
│   │   ├── ch01.tex          # Chapter 1: Introduction
│   │   ├── ch02.tex          # Chapter 2-5: Main text
│   │   ├── ch03.tex
│   │   ├── ch04.tex
│   │   └── ch05.tex
│   ├── macros.tex            # Custom LaTeX macros (inscriptions, lists, etc)
│   ├── preamble.tex          # Document setup and packages
│   └── appendices/           # Appendix files (referenced from main.tex)
│
├── build/
│   ├── output/
│   │   └── main.pdf          # 📍 CANONICAL OUTPUT LOCATION
│   ├── logs/                 # Build logs (gitignored)
│   ├── ocr/                  # OCR data from Phase 1-2 (gitignored)
│   ├── data/                 # Intermediate data files (gitignored)
│   └── tex/                  # XeTeX intermediate files (gitignored)
│
├── scripts/
│   ├── build.sh              # Build script - use this to generate PDF
│   ├── apply_wade_giles_conversions.py  # Phase 12: Wade-Giles → Pinyin
│   └── (other utility scripts)
│
├── tests/
│   ├── regression_repo_structure.py    # Repository tidiness tests
│   └── (other regression test suites)
│
├── data/
│   └── wade_giles_audit.tsv            # Phase 12: Romanization mappings
│
├── source/
│   └── Keightley_1978_original.pdf     # Reference: original 1978 edition
│
├── docs/                               # Documentation files
├── reference/                          # Reference materials
├── proofs/                             # Proof pages and notes
│
├── .gitignore                          # Ignore build artifacts
├── .github/workflows/repo-tidiness.yml # Automated tidiness checks
├── BUILDING.md                         # This file
├── README.md                           # Project overview
└── project.yml                         # Project configuration
```

## Output Locations

- **Canonical PDF:** `build/output/main.pdf`
- **Do NOT use:** `tex/main.pdf` (intermediate), `main.pdf` (root - removed)

The build process ensures:
- PDF is generated in a clean `build/output/` directory
- Only the canonical location is tracked
- Temporary XeTeX files are in `build/tex/` (gitignored)

## Repository Tidiness

The repository has automated checks to prevent clutter:

### Run tidiness tests locally
```bash
python3 tests/regression_repo_structure.py
```

### What's checked:
- ✓ No PDFs outside `build/output/` (except reference)
- ✓ No LaTeX temp files in root (`*.aux`, `*.log`, etc)
- ✓ No test artifacts in root
- ✓ Required directories exist
- ✓ Build script is present and executable
- ✓ `.gitignore` covers artifact types

### GitHub Actions
The `.github/workflows/repo-tidiness.yml` workflow runs these tests on every push and pull request.

## Project Phases

The document has been built incrementally through phases:

| Phase | Topic | Status | Output Location |
|-------|-------|--------|-----------------|
| 1-8 | Foundation & structure | ✓ Done | Integrated in LaTeX |
| 9 | Oracle inscription formatting | ✓ Done | `tex/macros.tex` (inscriptions) |
| 10 | Numbered list formatting | ✓ Done | `tex/macros.tex` (\listitem) |
| 11a-b | Internal cross-references | ✓ Done | `tex/chapters/` (section labels) |
| 12 | Wade-Giles → Pinyin conversion | ✓ Done | `tex/chapters/` + `data/wade_giles_audit.tsv` |
| 13+ | Bibliography & final polish | ⏳ Planned | TBD |

## Troubleshooting

### xelatex not found
```
Error: xelatex not found
Solution: Install TeX Live or MacTeX (see Prerequisites above)
```

### PDF won't compile
Check for errors:
1. Run `scripts/build.sh` and look for error messages
2. Check `build/logs/` for detailed logs
3. Verify all chapter files exist in `tex/chapters/`
4. Ensure no special characters in commit messages in `.tex` files

### PDF generated but cross-references show "??"
This is normal after first build. The build script runs xelatex twice to resolve all references.

## Development Workflow

1. **Edit source files** in `tex/chapters/` or `tex/main.tex`
2. **Build locally:** `./scripts/build.sh`
3. **Review** `build/output/main.pdf`
4. **Commit** only source files (not PDFs - they're gitignored)
5. **Push** - CI will verify tidiness and ensure structure is maintained

## Related Documentation

- [README.md](README.md) - Project overview
- [Keightley 1978 Original](source/Keightley_1978_original.pdf) - Reference edition
- Phase documentation in `/docs/` (for each major phase)
