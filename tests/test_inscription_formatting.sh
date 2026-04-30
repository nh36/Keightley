#!/bin/bash

# Regression tests for oracle inscription formatting (Phase 9)

echo "=== Phase 9: Oracle Inscription Formatting Tests ==="

# Test 1: Verify inscriptionblock macro is used in ch02
test_inscriptionblock_in_ch02() {
  grep -q "\\\\begin{inscriptionblock}" tex/chapters/ch02.tex
  echo $?
}

# Test 2: Verify inscriptionsection macro is used
test_inscriptionsection_in_ch02() {
  grep -q "\\\\inscriptionsection{PAIR OF COMPLEMENTARY CHARGES}" tex/chapters/ch02.tex
  echo $?
}

# Test 3: Verify inscriptionside macros are used
test_inscriptionside_in_ch02() {
  grep -q "\\\\inscriptionside{" tex/chapters/ch02.tex
  echo $?
}

# Test 4: Verify inscriptionref macros are used
test_inscriptionref_in_ch02() {
  grep -q "\\\\inscriptionref{" tex/chapters/ch02.tex
  echo $?
}

# Test 5: Verify macros are still defined in preamble
test_macros_still_defined() {
  grep -q "\\\\newcommand{\\\\inscriptionblock}" tex/preamble.tex 2>/dev/null || \
  grep -q "\\\\newenvironment{inscriptionblock}" tex/preamble.tex
  echo $?
}

# Run tests
result=$(test_inscriptionblock_in_ch02)
[ "$result" -eq 0 ] && echo "✓ Test 1: inscriptionblock found in ch02.tex" || echo "✗ Test 1: inscriptionblock not found"

result=$(test_inscriptionsection_in_ch02)
[ "$result" -eq 0 ] && echo "✓ Test 2: inscriptionsection macro used" || echo "✗ Test 2: inscriptionsection not used"

result=$(test_inscriptionside_in_ch02)
[ "$result" -eq 0 ] && echo "✓ Test 3: inscriptionside macros used" || echo "✗ Test 3: inscriptionside not used"

result=$(test_inscriptionref_in_ch02)
[ "$result" -eq 0 ] && echo "✓ Test 4: inscriptionref macros used" || echo "✗ Test 4: inscriptionref not used"

result=$(test_macros_still_defined)
[ "$result" -eq 0 ] && echo "✓ Test 5: All macros defined in preamble" || echo "✗ Test 5: Missing macro definitions"

# Test 6: LaTeX compilation succeeds
echo -n "Test 6: LaTeX compilation... "
cd tex && /usr/local/texlive/2025/bin/universal-darwin/xelatex -interaction=nonstopmode main.tex > /tmp/xelatex_test.log 2>&1
if grep -q "Output written on main.pdf" /tmp/xelatex_test.log; then
  echo "✓ LaTeX compilation successful"
  test_result=0
else
  echo "✗ LaTeX compilation failed"
  test_result=1
fi
cd ..

# Test 7: PDF generated and valid
echo -n "Test 7: PDF validation... "
if file tex/main.pdf | grep -q "PDF document"; then
  echo "✓ Valid PDF generated"
else
  echo "✗ PDF invalid or missing"
fi

echo "=== Tests Complete ==="
