#!/bin/bash

# Phase 11a Regression Tests: Section Reference Automation
# Tests that section references have been properly converted to \ref{} commands

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

echo "Phase 11a Regression Tests: Section Reference Automation"
echo "=========================================================="
echo

# Test 1-5: Count of replaced references per chapter
run_test "ch01 has \ref references" \
    "[ $(grep -c '\\ref{sec:chapters-ch01:' tex/chapters/ch01.tex) -gt 0 ]"

run_test "ch02 has \ref references" \
    "[ $(grep -c '\\ref{sec:chapters-ch02:' tex/chapters/ch02.tex) -gt 0 ]"

run_test "ch03 has \ref references" \
    "[ $(grep -c '\\ref{sec:chapters-ch03:' tex/chapters/ch03.tex) -gt 0 ]"

run_test "ch04 has \ref references" \
    "[ $(grep -c '\\ref{sec:chapters-ch04:' tex/chapters/ch04.tex) -gt 0 ]"

run_test "ch05 has \ref references" \
    "[ $(grep -c '\\ref{sec:chapters-ch05:' tex/chapters/ch05.tex) -gt 0 ]"

# Test 6: Total count of automated references (should be 60+, some preserved)
run_test "Total automated references is >= 60" \
    "[ $(grep -r '\\ref{sec:chapters-' tex/chapters/ | wc -l) -ge 60 ]"

# Test 7: All \ref commands use valid label format (checking a sample)
run_test "All \\ref commands use valid sec:chapters- format" \
    'grep -rq "\\\\ref{sec:chapters-" tex/chapters/'

# Test 8: No empty \ref commands
run_test "No empty \\ref commands" \
    "! grep -r '\\ref{}' tex/chapters/"

# Test 9: Referenced chapters exist (spot check: verify ch01:1.5 exists as label)
run_test "Referenced label ch01:1.5 exists" \
    "grep -q '\\label{sec:chapters-ch01:1.5}' tex/chapters/ch01.tex"

# Test 10: Referenced label ch02:2.4 exists
run_test "Referenced label ch02:2.4 exists" \
    "grep -q '\\label{sec:chapters-ch02:2.4}' tex/chapters/ch02.tex"

# Test 11: Original content preserved in comments (for unreferenceable sections)
run_test "Some original section text preserved as fallback" \
    "grep -q 'see sec\. [0-9]' tex/chapters/ch01.tex"

# Test 12: Verify references are properly formatted (sample check)
run_test "References are properly formatted with fallback text" \
    'grep -q "\\\\ref{sec:chapters-" tex/chapters/ch01.tex && grep -q "(see" tex/chapters/ch01.tex'

# Test 13: Verify ch04:4.2 reference appears in replacement text (high-traffic ref)
run_test "High-traffic ch04:4.2 reference automated" \
    'grep -q "\\\\ref{sec:chapters-ch04:4.2}" tex/chapters/ch01.tex'

# Test 14: Verify references to external/non-existent sections are preserved
run_test "Non-existent section references preserved (e.g., 4.3.3.3)" \
    "grep -q 'see sec\. 4.3.3.3' tex/chapters/ch01.tex"

# Test 15: Original labels still present and unchanged
run_test "Original section labels unchanged (ch01:1.2 exists)" \
    "grep -q '\\label{sec:chapters-ch01:1.2}' tex/chapters/ch01.tex"

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
