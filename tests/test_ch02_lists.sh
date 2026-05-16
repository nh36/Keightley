#!/bin/bash

# Regression tests for ch02 numbered list formatting

PASSED=0
FAILED=0

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

# Test 2: ch02 uses listitem macro
grep -q '\\listitem{' tex/chapters/ch02.tex
test_case "ch02 contains listitem macros" $?

# Test 3: ch02 has sufficient listitem usage (60+ items)
count=$(grep -o '\\listitem{' tex/chapters/ch02.tex | wc -l)
[ "$count" -ge 60 ]
test_case "ch02 has 60+ listitem macros (found: $count)" $?

# Test 4: ch02 verification-range band has the expected inline list cluster
sed -n '470,470p' tex/chapters/ch02.tex | grep -o '\\listitem{' | wc -l > /tmp/count.txt
count=$(cat /tmp/count.txt)
[ "$count" -ge 9 ]
test_case "ch02 line 470 has 9+ listitem items (found: $count)" $?

# Test 5: ch02 line 470 verification-range list preserves representative intervals
sed -n '470,470p' tex/chapters/ch02.tex | grep -q 'one day after harm had been forecast.*two days after a divination about hunting by fire.*three days after its prognostication'
test_case "ch02 line 470 list includes expected verification intervals" $?

# Test 6: Footnotes preserved
grep -c '\\footnote\[' tex/chapters/ch02.tex > /dev/null
test_case "ch02 footnotes preserved" $?

# Test 7: No old-style markers in ch02 line 470 area
sed -n '470,470p' tex/chapters/ch02.tex | grep -v '\\listitem' | grep -q '(1).*one day after harm had been forecast'
[ $? -ne 0 ]
test_case "ch02 old-style list markers removed from line 470" $?

# Test 8: Sample items spot-check
sed -n '470,470p' tex/chapters/ch02.tex | grep -Fq '\listitem{9} the onset of sickness appears to have taken place 175 (?) days after the divination'
test_case "ch02 line 470 list includes item 9 (long verification interval)" $?

# Test 9: Verify specific line 40 area if present
sed -n '35,45p' tex/chapters/ch02.tex | grep -q '\\listitem'
result=$?
# This may not be present, so just report
[ $result -eq 0 ] && echo "  (line 40 area has listitem items)" || echo "  (line 40 area not examined)"

# Test 10: Verify specific line 345 area if present
sed -n '340,350p' tex/chapters/ch02.tex | grep -q '\\listitem'
result=$?
[ $result -eq 0 ] && echo "  (line 345 area has listitem items)" || echo "  (line 345 area not examined)"

# Summary
echo ""
echo "=============================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "=============================="

if [ $FAILED -eq 0 ]; then
    echo "✓ All ch02 list formatting tests passed!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
