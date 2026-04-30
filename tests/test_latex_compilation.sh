#!/bin/bash
#
# Regression test suite for LaTeX compilation and OCR artifact cleanup
# Tests fixes from sessions including:
# - LaTeX compilation errors (# artifacts, markdown markers)
# - Paragraph structure fixes (inline section headers)
# - OCR artifact removal (running headers, garbage text)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEX_DIR="$PROJECT_ROOT/tex"
CHAPTERS_DIR="$TEX_DIR/chapters"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to print test results
test_result() {
    local test_name="$1"
    local exit_code="$2"
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $test_name"
        ((TESTS_FAILED++))
    fi
}

echo "========================================="
echo "LaTeX Regression Test Suite"
echo "========================================="
echo

# TEST 1: LaTeX compilation succeeds
echo "TEST 1: LaTeX compilation"
cd "$TEX_DIR"
COMPILE_OUTPUT=$(/usr/local/texlive/2025/bin/universal-darwin/xelatex -interaction=nonstopmode main.tex 2>&1)
if echo "$COMPILE_OUTPUT" | grep -q "Output written on main.pdf"; then
    test_result "LaTeX compiles without errors" 0
else
    test_result "LaTeX compiles without errors" 1
    echo "  Error output: $(echo "$COMPILE_OUTPUT" | grep -i "error" | head -1)"
fi

# TEST 2: PDF output exists and has expected page count
echo
echo "TEST 2: PDF page count"
if [ -f "$TEX_DIR/main.pdf" ]; then
    PAGE_COUNT=$(pdfinfo "$TEX_DIR/main.pdf" 2>/dev/null | grep "^Pages:" | awk '{print $2}')
    if [ "$PAGE_COUNT" = "191" ]; then
        test_result "PDF has exactly 191 pages (current: $PAGE_COUNT)" 0
    else
        test_result "PDF has exactly 191 pages (current: $PAGE_COUNT)" 1
    fi
else
    test_result "PDF file exists" 1
fi

# TEST 3: No OCR artifact "# List of Abbreviations" markdown headers remain
echo
echo "TEST 3: OCR artifact cleanup - markdown headers"
MARKDOWN_HEADERS=$(grep -r "^#.*List of Abbreviations" "$CHAPTERS_DIR" 2>/dev/null || true)
if [ -z "$MARKDOWN_HEADERS" ]; then
    test_result "No markdown '# List of Abbreviations' headers in chapters" 0
else
    test_result "No markdown '# List of Abbreviations' headers in chapters" 1
    echo "  Found: $MARKDOWN_HEADERS"
fi

# TEST 4: No stray "# " or "## " or "### " markdown markers
echo
echo "TEST 4: OCR artifact cleanup - markdown markers"
MARKDOWN_MARKERS=$(grep -E "^#+\s" "$CHAPTERS_DIR"/*.tex 2>/dev/null || true)
if [ -z "$MARKDOWN_MARKERS" ]; then
    test_result "No orphaned markdown markers (##, ###) in chapters" 0
else
    test_result "No orphaned markdown markers (##, ###) in chapters" 1
    echo "  Found: $(echo "$MARKDOWN_MARKERS" | head -3)"
fi

# TEST 5: No OCR artifact running headers "TRANSLATION: GENERAL CONSIDERATIONS"
echo
echo "TEST 5: OCR artifact cleanup - TRANSLATION headers"
TRANSLATION_HEADERS=$(grep -n "^TRANSLATION: GENERAL CONSIDERATIONS$" "$CHAPTERS_DIR"/*.tex 2>/dev/null || true)
if [ -z "$TRANSLATION_HEADERS" ]; then
    test_result "No 'TRANSLATION: GENERAL CONSIDERATIONS' artifacts in chapters" 0
else
    test_result "No 'TRANSLATION: GENERAL CONSIDERATIONS' artifacts in chapters" 1
    echo "  Found in: $(echo "$TRANSLATION_HEADERS" | cut -d: -f1 | sort -u)"
fi

# TEST 6: No OCR artifact "THE DATING CRITERIA" running headers
echo
echo "TEST 6: OCR artifact cleanup - DATING CRITERIA headers"
DATING_HEADERS=$(grep -n "^THE DATING CRITERIA$" "$CHAPTERS_DIR"/*.tex 2>/dev/null || true)
if [ -z "$DATING_HEADERS" ]; then
    test_result "No 'THE DATING CRITERIA' artifacts in chapters" 0
else
    test_result "No 'THE DATING CRITERIA' artifacts in chapters" 1
    echo "  Found in: $(echo "$DATING_HEADERS" | cut -d: -f1 | sort -u)"
fi

# TEST 7: Section headers in ch04 are properly formatted as LaTeX
echo
echo "TEST 7: Section header formatting in ch04"
REQUIRED_SECTIONS=(
    "Calligraphy"
    "Epigraphy"
    "Inscription Placement"
    "Ancestral Titles"
    "Marginal Notations"
    "Preface and Postface"
    "Prognostications"
    "Physical Criteria"
    "Burn Marks"
    "Archaeological Criteria"
)
MISSING_SECTIONS=()
for section in "${REQUIRED_SECTIONS[@]}"; do
    if ! grep -q "\\\\subsection\*{$section}" "$CHAPTERS_DIR/ch04.tex"; then
        MISSING_SECTIONS+=("$section")
    fi
done

if [ ${#MISSING_SECTIONS[@]} -eq 0 ]; then
    test_result "All 10 required subsection headers present in ch04" 0
else
    test_result "All 10 required subsection headers present in ch04" 1
    echo "  Missing: $(IFS=, ; echo "${MISSING_SECTIONS[*]}")"
fi

# TEST 8: Chronological Distribution header in ch05
echo
echo "TEST 8: Section header formatting in ch05"
if grep -q "\\\\subsection\*{Chronological Distribution}" "$CHAPTERS_DIR/ch05.tex"; then
    test_result "Chronological Distribution subsection header present in ch05" 0
else
    test_result "Chronological Distribution subsection header present in ch05" 1
fi

# TEST 9: Inscription Placement header in ch02
echo
echo "TEST 9: Section header formatting in ch02"
if grep -q "\\\\subsection\*{Inscription Placement}" "$CHAPTERS_DIR/ch02.tex"; then
    test_result "Inscription Placement subsection header present in ch02" 0
else
    test_result "Inscription Placement subsection header present in ch02" 1
fi

# TEST 10: Initial Preparation, Marginal Notations, The Hollows in ch01
echo
echo "TEST 10: Section header formatting in ch01"
REQUIRED_CH01_SECTIONS=(
    "Initial Preparation"
    "Marginal Notations"
    "The Hollows"
)
MISSING_CH01=()
for section in "${REQUIRED_CH01_SECTIONS[@]}"; do
    if ! grep -q "\\\\subsection\*{$section}" "$CHAPTERS_DIR/ch01.tex"; then
        MISSING_CH01+=("$section")
    fi
done

if [ ${#MISSING_CH01[@]} -eq 0 ]; then
    test_result "All 3 required subsection headers present in ch01" 0
else
    test_result "All 3 required subsection headers present in ch01" 1
    echo "  Missing: $(IFS=, ; echo "${MISSING_CH01[*]}")"
fi

# TEST 11: General Studies header in ch03
echo
echo "TEST 11: Section header formatting in ch03"
if grep -q "\\\\subsection\*{General Studies}" "$CHAPTERS_DIR/ch03.tex"; then
    test_result "General Studies subsection header present in ch03" 0
else
    test_result "General Studies subsection header present in ch03" 1
fi

# TEST 12: No orphaned text lines that are all uppercase section headers
echo
echo "TEST 12: No orphaned uppercase headers (potential OCR artifacts)"
# Look for lines that are ONLY uppercase letters and spaces/hyphens (not in LaTeX commands)
ORPHANED_HEADERS=$(grep -n "^[A-Z][A-Z ]*[A-Z]$" "$CHAPTERS_DIR"/*.tex 2>/dev/null | grep -v "\\\\section\|\\\\subsection\|footnote\|\\[" | grep -v "^.*KKKK\|^.*CCCC\|^.*XXXX" | wc -l)
if [ "$ORPHANED_HEADERS" -eq 0 ]; then
    test_result "No suspicious orphaned uppercase headers found" 0
else
    test_result "No suspicious orphaned uppercase headers found" 1
    echo "  Found $ORPHANED_HEADERS potential artifacts"
fi

# TEST 13: No @@ HEADING @@ OCR artifacts remain
echo
echo "TEST 13: OCR artifact cleanup - @@ HEADING @@ markers"
HEADING_ARTIFACTS=$(grep -r "@@.*HEADING.*@@" "$CHAPTERS_DIR" 2>/dev/null || true)
if [ -z "$HEADING_ARTIFACTS" ]; then
    test_result "No '@@HEADING@@' OCR artifacts in chapters" 0
else
    test_result "No '@@HEADING@@' OCR artifacts in chapters" 1
    echo "  Found in: $(echo "$HEADING_ARTIFACTS" | cut -d: -f1 | sort -u)"
fi

# TEST 14: All chapter files exist
echo
echo "TEST 14: Chapter file integrity"
REQUIRED_CHAPTERS=("ch01.tex" "ch02.tex" "ch03.tex" "ch04.tex" "ch05.tex")
MISSING_CHAPTERS=()
for chapter in "${REQUIRED_CHAPTERS[@]}"; do
    if [ ! -f "$CHAPTERS_DIR/$chapter" ]; then
        MISSING_CHAPTERS+=("$chapter")
    fi
done

if [ ${#MISSING_CHAPTERS[@]} -eq 0 ]; then
    test_result "All 5 required chapter files present" 0
else
    test_result "All 5 required chapter files present" 1
    echo "  Missing: $(IFS=, ; echo "${MISSING_CHAPTERS[*]}")"
fi

# TEST 15: preamble.tex exists and contains \origsecnum macro
echo
echo "TEST 15: LaTeX preamble integrity"
if [ -f "$TEX_DIR/preamble.tex" ] && grep -q "\\\\newcommand.*\\\\origsecnum" "$TEX_DIR/preamble.tex"; then
    test_result "preamble.tex exists with \\origsecnum macro definition" 0
else
    test_result "preamble.tex exists with \\origsecnum macro definition" 1
fi

# Summary
echo
echo "========================================="
echo "Test Summary"
echo "========================================="
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo "Total:  $((TESTS_PASSED + TESTS_FAILED))"
echo

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please review the errors above.${NC}"
    exit 1
fi
