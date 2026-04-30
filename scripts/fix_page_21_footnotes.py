#!/usr/bin/env python3
"""Fix footnote ordering on page 21.

Problem: Footnotes 4 and 9 appear out of order.
- Expected: 4, 5, 6, 7, 8, 9, 10, 11, 12
- Actual:   5, 6, 7, 8, 10, 11, 4, 12, 9

Analysis: Both GV and Tesseract are missing the superscript markers for 4 and 9.
Looking at footnote content:
- FN 4: about carbon-14 dating and dendrochronology
- FN 9: about Satow (1879) on scapulimancy

From the actual prose text, I can find:
- "dendrochronologically adjusted carbon-14 date" - this is clearly near FN 4
- "Satow (1879), p. 431" citation in text that matches FN 6 body

Strategy: Use keyword matching to find the correct positions in the prose.
"""

import re
from pathlib import Path
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parent.parent
CWN_DIR = ROOT / "build" / "ocr" / "cleaned_with_notes"
GV_SOURCE = ROOT / "source" / "Keightley_1978.txt"


def extract_fn_body(content: str, fn_no: int) -> str:
    """Extract footnote body."""
    pattern = rf'<!-- FOOTNOTE(?:-UNANCHORED)?:{fn_no} -->(.+?)<!-- /FOOTNOTE -->'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
    return ""


def find_keyword_position(prose: str, keywords: list[str]) -> int:
    """Find position in prose where any of the keywords appear."""
    for kw in keywords:
        pos = prose.find(kw)
        if pos >= 0:
            return pos
    return -1


def analyze_page_21():
    """Analyze and report on page 21 footnote placement."""
    cwn_file = CWN_DIR / "p_0021.md"
    content = cwn_file.read_text()
    
    # Get GV source
    gv_text = GV_SOURCE.read_text()
    gv_pages = gv_text.split('\f')
    gv_page_21 = gv_pages[20]
    
    # Extract footnote 4 body
    fn4_body = extract_fn_body(content, 4)
    fn9_body = extract_fn_body(content, 9)
    
    print("=" * 70)
    print("PAGE 21 FOOTNOTE ANALYSIS")
    print("=" * 70)
    
    print("\nFN 4 body:")
    print(f"  {fn4_body[:100]}...")
    print("\nKeywords to search: carbon-14, dendrochrono, carbon dating")
    
    # Find in prose
    stripped = re.sub(r'<!-- /?FOOTNOTE[^>]*-->', '', content)
    
    pos_carbon = stripped.find('carbon-14')
    pos_dendro = stripped.find('dendrochrono')
    
    print(f"\nFound 'carbon-14' at position {pos_carbon}")
    print(f"Found 'dendrochrono' at position {pos_dendro}")
    
    if pos_dendro >= 0:
        start = max(0, pos_dendro - 100)
        end = min(len(stripped), pos_dendro + 200)
        context = stripped[start:end]
        print(f"\nContext around dendrochrono:")
        print(context)
        print("\n^^ FN 4 should go HERE (before 'dendrochronologically')")
    
    print("\n" + "=" * 70)
    print("\nFN 9 body:")
    print(f"  {fn9_body[:100]}...")
    print("\nKeywords: Satow, 1879, p. 431")
    
    pos_satow = stripped.find('Satow (1879)')
    print(f"\nFound 'Satow (1879)' at position {pos_satow}")
    
    if pos_satow >= 0:
        start = max(0, pos_satow - 100)
        end = min(len(stripped), pos_satow + 200)
        context = stripped[start:end]
        print(f"\nContext around Satow:")
        print(context)
        print("\n^^ FN 9 should go HERE (near 'Satow (1879)')")
    
    # Now find where FN 5-8 are currently anchored
    print("\n" + "=" * 70)
    print("\nCURRENT FOOTNOTE POSITIONS:")
    print("=" * 70)
    
    for fn_no in [4, 5, 6, 7, 8, 9, 10, 11, 12]:
        pattern = rf'(.{{100}})<!-- FOOTNOTE:?{fn_no}'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            context = match.group(1)[-100:]
            print(f"\nFN {fn_no} currently at: ...{context}...")


if __name__ == '__main__':
    analyze_page_21()
