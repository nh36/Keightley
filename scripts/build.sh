#!/bin/bash
# Build script for Keightley LaTeX document
# Generates PDF from tex/main.tex and outputs to build/output/main.pdf

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_OUTPUT="$REPO_ROOT/build/output"
TEX_SOURCE="$REPO_ROOT/tex/main.tex"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Building Keightley LaTeX document..."
echo "  Source: $TEX_SOURCE"
echo "  Output: $BUILD_OUTPUT/main.pdf"

# Ensure output directory exists
mkdir -p "$BUILD_OUTPUT"

# Check if xelatex is available
if ! command -v xelatex &> /dev/null; then
    echo -e "${RED}✗ xelatex not found${NC}"
    echo "  Please install TeX Live or MacTeX"
    exit 1
fi

# Build with xelatex (run twice to resolve references)
cd "$REPO_ROOT/tex"
echo "Running xelatex (pass 1)..."
xelatex -interaction=nonstopmode -output-directory="$BUILD_OUTPUT" main.tex > /dev/null 2>&1 || {
    echo -e "${RED}✗ First xelatex pass failed${NC}"
    exit 1
}

echo "Running xelatex (pass 2)..."
xelatex -interaction=nonstopmode -output-directory="$BUILD_OUTPUT" main.tex > /dev/null 2>&1 || {
    echo -e "${RED}✗ Second xelatex pass failed${NC}"
    exit 1
}

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
