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

echo "=== CROSS-REFERENCE INFRASTRUCTURE TESTS ==="
echo ""

# Test 1: Labels exist in chapters
for ch in 1 2 3 4 5; do
    grep -q '\\label{' tex/chapters/ch0${ch}.tex
    test_case "ch0${ch} contains labels" $?
done

# Test 2: Check for duplicated label definitions
labels=$(grep -h '\\label{' tex/chapters/*.tex tex/appendices/*.tex 2>/dev/null | sort | uniq -d)
if [ -z "$labels" ]; then
    echo "✓ Test: No duplicate labels found"
    ((PASSED++))
else
    echo "✗ Test: Duplicate labels detected"
    ((FAILED++))
fi

# Test 3: Sample label format verification
grep -q '\\label{sec:chapters-ch01:' tex/chapters/ch01.tex
test_case "Label format is correct (sec:chapters-chXX:section.num)" $?

# Test 4: Chapter labels exist
grep -q '\\label{ch:1}' tex/chapters/ch01.tex
test_case "Chapter-level labels present (\\label{ch:X})" $?

# Test 5: No orphaned labels
orphaned=$(grep -B 1 '\\label{' tex/chapters/ch01.tex | grep -v '\\label' | grep -v '\\section' | grep -v '\\subsection' | grep -v '^--$' | wc -l)
[ "$orphaned" -lt 5 ]
test_case "Labels properly positioned after headings" $?

# Test 6: Verify section references exist
grep -q 'see sec\.' tex/chapters/ch01.tex
test_case "Section references exist ('see sec. X.Y')" $?

# Test 7: Verify chapter references exist
grep -q 'ch\. [0-9]' tex/chapters/ch01.tex
test_case "Chapter references exist ('ch. N')" $?

# Test 8: Verify page references exist
grep -q 'pp\. ' tex/chapters/ch01.tex
test_case "Page references exist ('pp. NN')" $?

# Test 9: Count total labels across document
total=$(grep -rh '\\label{' tex/ 2>/dev/null | wc -l)
[ "$total" -gt 50 ]
test_case "50+ labels exist across document ($total found)" $?

# Test 10: Cross-references haven't been auto-replaced yet (no early \ref commands)
auto_refs=$(grep -rh '\\ref{' tex/chapters/*.tex 2>/dev/null | wc -l)
[ "$auto_refs" -eq 0 ]
test_case "Section references not yet automated (\\\ref commands not yet applied)" $?

# Summary
echo ""
echo "=============================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "=============================="

if [ $FAILED -eq 0 ]; then
    echo "✓ Cross-reference infrastructure ready for automation!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi

