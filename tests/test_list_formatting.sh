#!/bin/bash
# Regression tests for numbered list formatting (Phase 10)
# Tests the \listitem{N} macro for inline list formatting

echo "=== Phase 10: Numbered List Formatting Tests ==="
echo ""

PASS=0
FAIL=0

test_result() {
    local name=$1
    local result=$2
    
    if [ "$result" -eq 0 ]; then
        echo "✓ $name"
        ((PASS++))
    else
        echo "✗ $name"
        ((FAIL++))
    fi
}

echo "=== Macro Definition Tests ==="

# Test 1: listitem macro is defined
grep -q "\\\\newcommand{\\\\listitem}" tex/preamble.tex
test_result "Test 1: listitem macro defined in preamble" $?

# Test 2: listitem macro used in ch01
grep -q "\\\\listitem{" tex/chapters/ch01.tex
test_result "Test 2: listitem macro used in ch01" $?

echo ""
echo "=== Content Integrity Tests ==="

# Test 3: All 6 list items present in ch01
grep -o "\\\\listitem{" tex/chapters/ch01.tex | wc -l | awk '{if ($1 >= 6) exit 0; else exit 1}'
test_result "Test 3: All 6 list items present" $?

# Test 4: List item 1 content preserved
grep -q "limiting role exercised by hollow, crack, and inscription density" tex/chapters/ch01.tex
test_result "Test 4: Item 1 content preserved" $?

# Test 5: List item 6 content preserved
grep -q "bureaucratic problem of filing" tex/chapters/ch01.tex
test_result "Test 5: Item 6 content preserved" $?

# Test 6: Footnote in item 5 preserved
grep -q "previous divinations;\\\\footnote" tex/chapters/ch01.tex
test_result "Test 6: Footnote in item 5 preserved" $?

echo ""
echo "=== LaTeX Compilation Tests ==="

# Test 7: LaTeX compilation successful
cd tex && /usr/local/texlive/2025/bin/universal-darwin/xelatex -interaction=nonstopmode main.tex > /tmp/test_compile.log 2>&1
grep -q "Output written on main.pdf" /tmp/test_compile.log
test_result "Test 7: LaTeX compilation successful" $?
cd ..

# Test 8: Valid PDF generated
file tex/main.pdf | grep -q "PDF document"
test_result "Test 8: Valid PDF generated" $?

echo ""
echo "=== Format Validation Tests ==="

# Test 9: Old inline format (1) removed
! grep -q "^(1) the limiting role" tex/chapters/ch01.tex
test_result "Test 9: Old format markers (1) removed" $?

# Test 10: Prose flow maintained (no enumerate environment)
! grep -q "\\\\begin{enumerate}" tex/chapters/ch01.tex
test_result "Test 10: Prose flow maintained (no enumerate)" $?

echo ""
echo "=== Test Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ All list formatting tests passed!"
    exit 0
else
    exit 1
fi
