#!/bin/bash
# Build script for Keightley LaTeX document
# Generates PDF from tex/main.tex and outputs to build/output/main.pdf

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_OUTPUT="$REPO_ROOT/build/output"
TEX_DIR="$REPO_ROOT/tex"
TEX_SOURCE="$TEX_DIR/main.tex"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Building Keightley LaTeX document..."
echo "  Source: $TEX_SOURCE"
echo "  Output: $BUILD_OUTPUT/main.pdf"

# Ensure output directory exists
mkdir -p "$BUILD_OUTPUT"

# Resolve xelatex from PATH or known MacTeX install location
XELATEX_BIN="${XELATEX_BIN:-}"
if [ -z "$XELATEX_BIN" ]; then
    if command -v xelatex &> /dev/null; then
        XELATEX_BIN="$(command -v xelatex)"
    elif [ -x "/usr/local/texlive/2025/bin/universal-darwin/xelatex" ]; then
        XELATEX_BIN="/usr/local/texlive/2025/bin/universal-darwin/xelatex"
    fi
fi

if [ -z "$XELATEX_BIN" ]; then
    echo -e "${RED}✗ xelatex not found${NC}"
    echo "  Checked PATH and /usr/local/texlive/2025/bin/universal-darwin/xelatex"
    exit 1
fi

# Remove any stale PDF left in tex/ from older manual builds so repo-structure tests pass.
rm -f "$TEX_DIR/main.pdf"

# Build with xelatex (run twice to resolve references)
cd "$TEX_DIR"

run_xelatex_pass() {
    local pass="$1"
    local status=0

    echo "Running xelatex (pass $pass)..."
    set +e
    "$XELATEX_BIN" -interaction=nonstopmode -output-directory="$BUILD_OUTPUT" main.tex > /dev/null 2>&1
    status=$?
    set -e

    if [ "$status" -ne 0 ]; then
        echo "  Warning: xelatex exited with status $status on pass $pass"
    fi
}

run_xelatex_pass 1
run_xelatex_pass 2

# Verify output
if [ -f "$BUILD_OUTPUT/main.pdf" ]; then
    size=$(du -h "$BUILD_OUTPUT/main.pdf" | cut -f1)
    echo -e "${GREEN}✓ Build successful${NC}"
    echo "  Output: $BUILD_OUTPUT/main.pdf ($size)"
    exit 0
else
    echo -e "${RED}✗ PDF generation failed - no output file${NC}"
    exit 1
fi
