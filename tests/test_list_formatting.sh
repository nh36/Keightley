#!/bin/bash
# Regression tests for numbered list formatting (Phase 10)

echo "=== Phase 10: Numbered List Formatting Tests ==="
echo ""

PASS=0
FAIL=0

test_count() {
    local name=$1
    local pattern=$2
    local expected=$3
    local file=$4
    
    local count=$(grep -c "$pattern" "$file")
    if [ "$count" -ge "$expected" ]; then
        echo "✓ $name"
        ((PASS++))
    else
        echo "✗ $name (found $count, expected $expected)"
        ((FAIL++))
    fi
}

test_no_pattern() {
    local name=$1
    local pattern=$2
    local file=$3
    
    if ! grep -q "$pattern" "$file"; then
        echo "✓ $name"
        ((PASS++))
    else
        echo "✗ $name (pattern still found)"
        ((FAIL++))
    fi
}

echo "=== List Format Tests ==="
test_count "enumerate environment in ch01" "\\\\begin{enumerate}" 1 "tex/chapters/ch01.tex"
test_count "enumerate items in ch01" "\\\\item the" 3 "tex/chapters/ch01.tex"
test_no_pattern "Old (1)...(2)...(3) format removed from ch01 list" "(1) the limiting role" "tex/chapters/ch01.tex"

echo ""
echo "=== List Content Tests ==="
grep -q "the limiting role exercised by hollow, crack, and inscription density" tex/chapters/ch01.tex && \
    echo "✓ List item 1 content preserved" && ((PASS++)) || \
    { echo "✗ List item 1 missing"; ((FAIL++)); }

grep -q "the nature of the divination topic" tex/chapters/ch01.tex && \
    echo "✓ List item 2 content preserved" && ((PASS++)) || \
    { echo "✗ List item 2 missing"; ((FAIL++)); }

grep -q "the bureaucratic problem of filing" tex/chapters/ch01.tex && \
    echo "✓ List item 6 content preserved" && ((PASS++)) || \
    { echo "✗ List item 6 missing"; ((FAIL++)); }

echo ""
echo "=== LaTeX Compilation Test ==="
cd tex && xelatex -interaction=nonstopmode main.tex > /tmp/test_compile.log 2>&1
if grep -q "Output written on main.pdf" /tmp/test_compile.log; then
    echo "✓ LaTeX compilation successful"
    ((PASS++))
else
    echo "✗ LaTeX compilation failed"
    ((FAIL++))
fi

cd ..

echo ""
echo "=== PDF Validation Test ==="
if pdfinfo tex/main.pdf > /dev/null 2>&1; then
    echo "✓ Valid PDF generated"
    ((PASS++))
else
    echo "✗ PDF validation failed"
    ((FAIL++))
fi

echo ""
echo "=== Test Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"

if [ $FAIL -eq 0 ]; then
    echo "All tests passed!"
    exit 0
else
    exit 1
fi
