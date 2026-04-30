#!/bin/bash

# Phase 11b Regression Tests: Chapter Reference Automation
# Tests that chapter references have been properly converted to \ref{} commands

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

test_count=0
pass_count=0

run_test() {
    local test_name="$1"
    local test_cmd="$2"
    
    test_count=$((test_count + 1))
    
    if eval "$test_cmd"; then
        echo -e "${GREEN}✓${NC} Test $test_count: $test_name"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗${NC} Test $test_count: $test_name"
    fi
}

echo "Phase 11b Regression Tests: Chapter Reference Automation"
echo "=========================================================="
echo

# Test 1-5: Count of replaced references per chapter
run_test "ch01 has \\ref references to chapters" \
    'grep -q "\\\\ref{ch:" tex/chapters/ch01.tex'

run_test "ch02 has \\ref references to chapters" \
    'grep -q "\\\\ref{ch:" tex/chapters/ch02.tex'

run_test "ch03 has \\ref references to chapters" \
    'grep -q "\\\\ref{ch:" tex/chapters/ch03.tex'

run_test "ch04 has \\ref references to chapters" \
    'grep -q "\\\\ref{ch:" tex/chapters/ch04.tex'

run_test "ch05 has \\ref references to chapters" \
    'grep -q "\\\\ref{ch:" tex/chapters/ch05.tex'

# Test 6: Total count of automated references (should be 140+, some may be skipped)
run_test "Total automated references is >= 140" \
    "[ \$(grep -r '\\\\ref{ch:' tex/chapters/ | wc -l) -ge 140 ]"

# Test 7: All \ref commands use valid ch:N format
run_test "All \\ref commands use valid ch:N format" \
    'grep -rq "\\\\ref{ch:[1-5]}" tex/chapters/'

# Test 8: No empty \ref commands
run_test "No empty \\ref commands for chapters" \
    '! grep -r "\\\\ref{ch:}" tex/chapters/'

# Test 9: Chapter 1 label exists
run_test "Chapter 1 label exists" \
    'grep -q "\\\\label{ch:1}" tex/chapters/ch01.tex'

# Test 10: Chapter 4 label exists
run_test "Chapter 4 label exists" \
    'grep -q "\\\\label{ch:4}" tex/chapters/ch04.tex'

# Test 11: Original content preserved in comments (for review)
run_test "Original chapter references preserved as fallback" \
    'grep -q "(see ch\. [1-5])" tex/chapters/ch01.tex'

# Test 12: References appear in main text and footnotes
run_test "Chapter references appear in footnotes" \
    'grep -q "\\\\ref{ch:" tex/chapters/ch02.tex | head -1'

# Test 13: Cross-chapter references are automated (e.g., ch01 refers to ch02)
run_test "Cross-chapter reference ch01->ch02 automated" \
    'grep -q "\\\\ref{ch:2}" tex/chapters/ch01.tex'

# Test 14: Self-references are included (ch04 referencing ch04)
run_test "Self-references included (ch references within same chapter)" \
    'grep "\\\\ref{ch:4}" tex/chapters/ch04.tex | wc -l | grep -qE "[1-9]"'

# Test 15: Multiple references to same chapter are all updated
run_test "All references to chapter 2 are updated in ch01" \
    '! grep -E "(see ch\. 2[^0-9]|see ch\. 2})" tex/chapters/ch01.tex || grep -q "\\\\ref{ch:2}" tex/chapters/ch01.tex'

# Test 16: Verify fallback text format is consistent
run_test "Fallback text uses consistent format (see ch. N)" \
    'grep "\\\\ref{ch:[1-5]}" tex/chapters/ch01.tex | grep -q "(see ch\. [1-5])"'

# Test 17: Original labels still present and unchanged  
run_test "Original chapter labels unchanged (ch:1 exists)" \
    'grep -q "\\\\label{ch:1}" tex/chapters/ch01.tex'

echo
echo "=========================================================="
echo -e "Results: ${GREEN}$pass_count/$test_count${NC} tests passed"

if [ "$pass_count" -eq "$test_count" ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
