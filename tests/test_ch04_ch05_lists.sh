#!/bin/bash

# Regression tests for ch04/ch05 numbered list formatting

PASSED=0
FAILED=0

# Test function
test_case() {
    local name="$1"
    local result="$2"
    
    if [ "$result" -eq 0 ]; then
        echo "✓ Test: $name"
        ((PASSED++))
    else
        echo "✗ Test: $name"
        ((FAILED++))
    fi
}

# Test 1: listitem macro defined
grep -q '\\newcommand{\\listitem}' tex/preamble.tex
test_case "listitem macro defined in preamble" $?

# Test 2: ch04 uses listitem macro
grep -q '\\listitem{' tex/chapters/ch04.tex
test_case "ch04 contains listitem macros" $?

# Test 3: ch05 uses listitem macro
grep -q '\\listitem{' tex/chapters/ch05.tex
test_case "ch05 contains listitem macros" $?

# Test 4: ch04 has sufficient listitem usage (40+ items)
count=$(grep -o '\\listitem{' tex/chapters/ch04.tex | wc -l)
[ "$count" -ge 40 ]
test_case "ch04 has 40+ listitem macros (found: $count)" $?

# Test 5: ch05 has sufficient listitem usage (20+ items)
count=$(grep -o '\\listitem{' tex/chapters/ch05.tex | wc -l)
[ "$count" -ge 20 ]
test_case "ch05 has 20+ listitem macros (found: $count)" $?

# Test 6: ch04 line 573 area has listitem items
sed -n '560,600p' tex/chapters/ch04.tex | grep -q '\\listitem{1}.*\\listitem{2}.*\\listitem{3}.*\\listitem{4}'
test_case "ch04 line 573 list has items 1-4" $?

# Test 7: ch05 line 223 area has listitem items
sed -n '215,235p' tex/chapters/ch05.tex | grep -q '\\listitem{1}.*\\listitem{2}.*\\listitem{3}.*\\listitem{4}'
test_case "ch05 line 223 list has items 1-4" $?

# Test 8: Footnotes preserved (ch04)
grep -c '\\footnote\[' tex/chapters/ch04.tex > /dev/null
test_case "ch04 footnotes preserved" $?

# Test 9: Footnotes preserved (ch05)
grep -c '\\footnote\[' tex/chapters/ch05.tex > /dev/null
test_case "ch05 footnotes preserved" $?

# Test 10: No old-style list markers remain (ch04 main list)
# Should not have raw (1) pattern in list context
sed -n '560,600p' tex/chapters/ch04.tex | grep -v '\\listitem' | grep -q '(1).*period.*I.*early.*III'
[ $? -ne 0 ]
test_case "ch04 old-style list markers removed from line 573" $?

# Test 11: No old-style list markers remain (ch05 main list)
sed -n '215,235p' tex/chapters/ch05.tex | grep -v '\\listitem' | grep -q '(1).*early.*collectors'
[ $? -ne 0 ]
test_case "ch05 old-style list markers removed from line 223" $?

# Test 12: Sample content preserved (ch04)
sed -n '560,600p' tex/chapters/ch04.tex | grep -q 'diviner.*Ta.*period.*I'
test_case "ch04 list content preserved (diviner Ta reference)" $?

# Test 13: Sample content preserved (ch05)
sed -n '215,235p' tex/chapters/ch05.tex | grep -q 'early.*collectors.*untrustworthy'
test_case "ch05 list content preserved (collectors reference)" $?

# Summary
echo ""
echo "=============================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "=============================="

if [ $FAILED -eq 0 ]; then
    echo "✓ All ch04/ch05 list formatting tests passed!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi

