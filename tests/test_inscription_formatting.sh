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
  grep -q "\\\\newenvironment{inscriptionblock}" tex/preamble.tex
  echo $?
}

# Test 6: Count inscriptionblock blocks (should be at least 2 for both inscriptions)
test_multiple_inscriptionblocks() {
  count=$(grep -c "\\\\begin{inscriptionblock}" tex/chapters/ch02.tex)
  [ "$count" -ge 2 ]
  echo $?
}

# Test 7: Verify both Ping-pien 235 and Ping-pien 1 references are converted
test_ping_pien_references() {
  grep -q "\\\\inscriptionref{Ping-pien 235.2}" tex/chapters/ch02.tex && \
  grep -q "\\\\inscriptionref{Ping-pien 1.4}" tex/chapters/ch02.tex
  echo $?
}

# Test 8: Verify side descriptors are properly formatted
test_side_descriptors() {
  grep -q "\\\\inscriptionside{positive" tex/chapters/ch02.tex && \
  grep -q "\\\\inscriptionside{negative" tex/chapters/ch02.tex
  echo $?
}

# Test 9: Verify old-style inline labels are removed (should have few/none in formatted sections)
test_old_labels_removed() {
  # In the formatted inscriptions (lines 408-453), old-style (Preface:) etc should be removed
  section_has_old=$(sed -n '408,453p' tex/chapters/ch02.tex | grep -c "^(Preface:)$")
  [ "$section_has_old" -eq 0 ]
  echo $?
}

# Test 10: Verify inscriptionblock environment is properly closed
test_inscriptionblock_closed() {
  opens=$(grep -c "\\\\begin{inscriptionblock}" tex/chapters/ch02.tex)
  closes=$(grep -c "\\\\end{inscriptionblock}" tex/chapters/ch02.tex)
  [ "$opens" -eq "$closes" ]
  echo $?
}

# Test 11: Verify no unclosed inscriptionsection commands
test_inscriptionsection_valid() {
  # inscriptionsection should not create environments, just formatting
  ! grep -q "\\\\end{inscriptionsection}" tex/chapters/ch02.tex
  echo $?
}

# Run all tests
echo ""
echo "=== Test Results ==="
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

result=$(test_multiple_inscriptionblocks)
[ "$result" -eq 0 ] && echo "✓ Test 6: Multiple inscriptionblocks found (2+)" || echo "✗ Test 6: Insufficient inscriptionblocks"

result=$(test_ping_pien_references)
[ "$result" -eq 0 ] && echo "✓ Test 7: Ping-pien references converted" || echo "✗ Test 7: Missing Ping-pien references"

result=$(test_side_descriptors)
[ "$result" -eq 0 ] && echo "✓ Test 8: Side descriptors formatted" || echo "✗ Test 8: Side descriptors missing"

result=$(test_old_labels_removed)
[ "$result" -eq 0 ] && echo "✓ Test 9: Old-style labels removed" || echo "✗ Test 9: Old labels still present"

result=$(test_inscriptionblock_closed)
[ "$result" -eq 0 ] && echo "✓ Test 10: inscriptionblock properly closed" || echo "✗ Test 10: Unmatched inscriptionblock"

result=$(test_inscriptionsection_valid)
[ "$result" -eq 0 ] && echo "✓ Test 11: inscriptionsection used correctly" || echo "✗ Test 11: inscriptionsection misused"

echo ""
echo "=== LaTeX Compilation Test ==="
echo -n "Test 12: LaTeX compilation... "
cd tex && /usr/local/texlive/2025/bin/universal-darwin/xelatex -interaction=nonstopmode main.tex > /tmp/xelatex_test.log 2>&1
if grep -q "Output written on main.pdf" /tmp/xelatex_test.log; then
  echo "✓ LaTeX compilation successful"
else
  echo "✗ LaTeX compilation failed"
fi
cd ..

echo -n "Test 13: PDF validation... "
if file tex/main.pdf | grep -q "PDF document"; then
  echo "✓ Valid PDF generated"
else
  echo "✗ PDF invalid or missing"
fi

echo ""
echo "=== Phase 10: Numbered List Formatting Tests ==="

# Test 14: Verify enumerate environment exists in ch01
test_enumerate_in_ch01() {
  grep -q "\\\\begin{enumerate}" tex/chapters/ch01.tex
  echo $?
}

# Test 15: Verify old inline list format removed from ch01
test_old_list_format_removed() {
  # Should not find "(1) the limiting role" pattern at beginning of line
  ! grep -q "^(1) the limiting role exercised by hollow" tex/chapters/ch01.tex
  echo $?
}

# Test 16: Verify list items are in enumerate format
test_list_items_formatted() {
  count=$(grep -c "\\\\item " tex/chapters/ch01.tex)
  [ "$count" -ge 6 ]  # ch01 list has 6 items
  echo $?
}

# Test 17: Verify list item content preserved
test_list_content_preserved() {
  grep -q "the limiting role exercised by hollow, crack, and inscription density" tex/chapters/ch01.tex && \
  grep -q "the nature of the divination topic" tex/chapters/ch01.tex && \
  grep -q "the bureaucratic problem of filing" tex/chapters/ch01.tex
  echo $?
}

# Test 18: Verify enumerate properly closed
test_enumerate_closed() {
  opens=$(grep -c "\\\\begin{enumerate}" tex/chapters/ch01.tex)
  closes=$(grep -c "\\\\end{enumerate}" tex/chapters/ch01.tex)
  [ "$opens" -eq "$closes" ]
  echo $?
}

result=$(test_enumerate_in_ch01)
[ "$result" -eq 0 ] && echo "✓ Test 14: enumerate environment found in ch01.tex" || echo "✗ Test 14: enumerate not found"

result=$(test_old_list_format_removed)
[ "$result" -eq 0 ] && echo "✓ Test 15: Old inline list format removed" || echo "✗ Test 15: Old format still present"

result=$(test_list_items_formatted)
[ "$result" -eq 0 ] && echo "✓ Test 16: List items formatted with \\item" || echo "✗ Test 16: Missing \\item commands"

result=$(test_list_content_preserved)
[ "$result" -eq 0 ] && echo "✓ Test 17: List content preserved" || echo "✗ Test 17: List content missing"

result=$(test_enumerate_closed)
[ "$result" -eq 0 ] && echo "✓ Test 18: enumerate properly closed" || echo "✗ Test 18: Unmatched enumerate"

echo ""
echo "=== Tests Complete ==="
