#!/bin/bash

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

echo "=== COMPREHENSIVE LIST FORMATTING AUDIT ==="
echo ""

# Core tests
grep -q '\\newcommand{\\listitem}' tex/preamble.tex
test_case "listitem macro defined in preamble" $?

count=$(grep -o '\\listitem{' tex/chapters/ch01.tex | wc -l)
[ "$count" -ge 17 ]
test_case "ch01 has 17+ listitem macros ($count found)" $?

count=$(grep -o '\\listitem{' tex/chapters/ch02.tex | wc -l)
[ "$count" -ge 60 ]
test_case "ch02 has 60+ listitem macros ($count found)" $?

count=$(grep -o '\\listitem{' tex/chapters/ch03.tex | wc -l)
[ "$count" -ge 25 ]
test_case "ch03 has 25+ listitem macros ($count found)" $?

count=$(grep -o '\\listitem{' tex/chapters/ch04.tex | wc -l)
[ "$count" -ge 25 ]
test_case "ch04 has 25+ listitem macros ($count found)" $?

count=$(grep -o '\\listitem{' tex/chapters/ch05.tex | wc -l)
[ "$count" -ge 12 ]
test_case "ch05 has 12+ listitem macros ($count found)" $?

count=$(grep -o '\\listitem{' tex/appendices/app01.tex | wc -l)
[ "$count" -ge 4 ]
test_case "app01 has 4+ listitem macros ($count found)" $?

count=$(grep -o '\\listitem{' tex/appendices/app04.tex | wc -l)
[ "$count" -ge 8 ]
test_case "app04 has 8+ listitem macros ($count found)" $?

total=$(grep -r '\\listitem{' tex/chapters/ tex/appendices/ 2>/dev/null | wc -l)
[ "$total" -ge 85 ]
test_case "Total 85+ listitem macros in document ($total found)" $?

# Old-style marker removal tests
sed -n '600,625p' tex/chapters/ch01.tex | grep -v '\\listitem' | grep -q '(1).*density'
[ $? -ne 0 ]
test_case "ch01 old-style list markers removed (line 602)" $?

sed -n '110,130p' tex/chapters/ch02.tex | grep -v '\\listitem' | grep -q '(1).*sacrifices'
[ $? -ne 0 ]
test_case "ch02 old-style list markers removed (line 115)" $?

# Footnote preservation tests
for ch in ch01 ch02 ch03 ch04 ch05; do
    grep -q '\\footnote\[' tex/chapters/$ch.tex || return 1
done
test_case "Footnote structures preserved in all chapters" $?

# Content spot-checks (check individual components)
grep -A 15 'Among the factors' tex/chapters/ch01.tex | grep -q 'listitem{1}'
test_case "ch01 line 602: item 1 (hollow factors) present" $?

grep -A 15 'Among the factors' tex/chapters/ch01.tex | grep -q 'listitem{2}' && \
grep -A 15 'Among the factors' tex/chapters/ch01.tex | grep -q 'topic'
test_case "ch01 line 602: item 2 (topics) present" $?

sed -n '470,470p' tex/chapters/ch02.tex | grep -q 'listitem{1}' && \
sed -n '470,470p' tex/chapters/ch02.tex | grep -q 'one day after harm had been forecast'
test_case "ch02 line 470: item 1 (verification interval) present" $?

sed -n '470,470p' tex/chapters/ch02.tex | grep -q 'listitem{9}' && \
sed -n '470,470p' tex/chapters/ch02.tex | grep -q '175 (?) days after the divination'
test_case "ch02 line 470: item 9 (long verification interval) present" $?

sed -n '751,756p' tex/chapters/ch03.tex | grep -q 'listitem{1} front-inscription cracks' && \
sed -n '751,756p' tex/chapters/ch03.tex | grep -q 'listitem{2} back-inscription cracks' && \
sed -n '751,756p' tex/chapters/ch03.tex | grep -q 'listitem{3} inscriptionless cracks'
test_case "ch03 line 751: three crack categories use listitem markers" $?

sed -n '751,756p' tex/chapters/ch03.tex | grep -v '\\listitem' | grep -q '(3 inscriptionless cracks'
[ $? -ne 0 ]
test_case "ch03 line 751: malformed raw third marker removed" $?

# Summary stats
echo ""
echo "=== COVERAGE SUMMARY ==="
total=$(grep -r '\\listitem{' tex/ 2>/dev/null | wc -l)
ch01=$(grep -o '\\listitem{' tex/chapters/ch01.tex | wc -l)
ch02=$(grep -o '\\listitem{' tex/chapters/ch02.tex | wc -l)
ch03=$(grep -o '\\listitem{' tex/chapters/ch03.tex | wc -l)
ch04=$(grep -o '\\listitem{' tex/chapters/ch04.tex | wc -l)
ch05=$(grep -o '\\listitem{' tex/chapters/ch05.tex | wc -l)
app01=$(grep -o '\\listitem{' tex/appendices/app01.tex | wc -l)
app04=$(grep -o '\\listitem{' tex/appendices/app04.tex | wc -l)

echo "Total listitem macros: $total"
echo "  ch01: $ch01  |  ch02: $ch02  |  ch03: $ch03"
echo "  ch04: $ch04  |  ch05: $ch05  |  app01: $app01  |  app04: $app04"

echo ""
echo "=============================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "=============================="

if [ $FAILED -eq 0 ]; then
    echo "✓ All list formatting tests PASSED!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
