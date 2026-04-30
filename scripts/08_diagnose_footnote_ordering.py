#!/usr/bin/env python3
"""Comprehensive diagnostic for footnote ordering issues.

Analyzes GV vs Tesseract versions of each problem page to identify:
1. Which footnotes are in wrong positions
2. What their content is about
3. Where they should logically belong based on context
4. What OCR artifacts may be causing the misplacement

Usage:
  python3 scripts/08_diagnose_footnote_ordering.py [page_num]
  
Outputs diagnostic TSV for manual correction.
"""

import csv
import re
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
CLEANED_DIR = ROOT / "build" / "ocr" / "cleaned"
CWN_DIR = ROOT / "build" / "ocr" / "cleaned_with_notes"
GV_SOURCE = ROOT / "source" / "Keightley_1978.txt"
DIAGNOSTIC_OUT = ROOT / "build" / "qa" / "footnote_diagnostics.tsv"

# Problem pages identified
PROBLEM_PAGES = {
    21: [5, 6, 7, 8, 10, 11, 4, 12, 9],  # Out-of-order: 11>4, 12>9
    46: [2, 3, 4, 8, 9, 7, 5, 6],        # Out-of-order: 9>7, 7>5
    78: [15, 16, 17, 18, 14, 19, 20],    # Out-of-order: 18>14
    96: [87, 89, 88],                     # Out-of-order: 89>88
    101: [105, 104, 106, 107, 108, 109], # Out-of-order: 105>104
    132: [100, 99, 101, 102],            # Out-of-order: 100>99
    135: [117, 118, 116, 119, 120, 121, 122, 123],  # Out-of-order: 118>116
}


def load_gv_source() -> dict[int, str]:
    """Load Google Vision chunks indexed by scan page number."""
    gv_text = GV_SOURCE.read_text()
    pages = gv_text.split('\f')
    return {i+1: pages[i] for i in range(len(pages))}


def extract_footnote_content(page_content: str, fn_no: int) -> Optional[str]:
    """Extract footnote body text from page. Handles both FOOTNOTE and FOOTNOTE-UNANCHORED."""
    pattern = rf'<!-- FOOTNOTE(?:-UNANCHORED)?:{fn_no} -->(.+?)<!-- /FOOTNOTE -->'
    match = re.search(pattern, page_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def get_footnote_context(prose: str, marker_pos: int, window: int = 200) -> str:
    """Get prose context around where a footnote marker appears."""
    start = max(0, marker_pos - window)
    end = min(len(prose), marker_pos + window)
    return prose[start:end]


def find_gv_markers(gv_prose: str) -> dict[int, int]:
    """Find Unicode superscript markers in GV prose, return {fn_no: position}."""
    markers = {}
    
    # Look for patterns like "text¹" and extract the number
    for match in re.finditer(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]', gv_prose):
        marker_char = match.group()
        # Convert unicode superscript to digit
        digit_map = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
                     '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'}
        fn_no = int(digit_map[marker_char])
        markers[fn_no] = match.start()
    
    return markers


def diagnose_page(scan_page: int, gv_pages: dict) -> dict:
    """Comprehensive diagnosis of a problem page."""
    cwn_file = CWN_DIR / f"p_{scan_page:04d}.md"
    tess_file = CLEANED_DIR / f"p_{scan_page:04d}.md"
    
    if not cwn_file.exists() or not tess_file.exists():
        return {'error': f'Files not found for page {scan_page}'}
    
    cwn_content = cwn_file.read_text()
    tess_content = tess_file.read_text()
    gv_content = gv_pages.get(scan_page, "")
    
    # Get expected sequence from PROBLEM_PAGES
    expected_seq = PROBLEM_PAGES.get(scan_page, [])
    
    # Actual sequence from current output
    actual_markers = []
    for match in re.finditer(r'<!-- FOOTNOTE:(\d+) -->', cwn_content):
        actual_markers.append(int(match.group(1)))
    
    # Find GV markers
    gv_prose_match = re.search(r'^(.+?)(?=^\d+\.\s+)', gv_content, re.MULTILINE | re.DOTALL)
    gv_prose = gv_prose_match.group(1) if gv_prose_match else gv_content
    gv_markers = find_gv_markers(gv_prose)
    
    # Diagnose each footnote
    diagnostics = []
    for i, fn_no in enumerate(expected_seq):
        status = 'OK'
        if i > 0 and fn_no < expected_seq[i-1]:
            status = f'OUT-OF-ORDER (after {expected_seq[i-1]})'
        
        # Get footnote content
        body = extract_footnote_content(cwn_content, fn_no)
        if not body:
            body = "[NOT FOUND IN OUTPUT]"
        
        # Get GV marker position if available
        gv_marker_pos = gv_markers.get(fn_no, -1)
        gv_context = ""
        if gv_marker_pos >= 0:
            gv_context = get_footnote_context(gv_prose, gv_marker_pos, 100)
        
        diagnostics.append({
            'page': scan_page,
            'fn_no': fn_no,
            'status': status,
            'body_snippet': (body[:60] + '...') if len(body) > 60 else body,
            'gv_marker_pos': gv_marker_pos,
            'gv_context': gv_context[:100],
        })
    
    return {
        'page': scan_page,
        'expected_sequence': expected_seq,
        'actual_sequence': actual_markers,
        'diagnostics': diagnostics,
    }


def main():
    if len(sys.argv) > 1:
        pages = [int(sys.argv[1])]
    else:
        pages = sorted(PROBLEM_PAGES.keys())
    
    gv_pages = load_gv_source()
    
    all_diagnostics = []
    for page in pages:
        print(f"\n{'='*70}")
        print(f"PAGE {page}")
        print('='*70)
        
        result = diagnose_page(page, gv_pages)
        
        if 'error' in result:
            print(f"ERROR: {result['error']}")
            continue
        
        print(f"Expected sequence: {result['expected_sequence']}")
        print(f"Actual sequence:   {result['actual_sequence']}")
        
        print(f"\nFootnote details:")
        for diag in result['diagnostics']:
            marker = "⚠️" if 'OUT-OF-ORDER' in diag['status'] else "✓"
            print(f"  {marker} FN {diag['fn_no']:3d}: {diag['status']}")
            print(f"      Body: {diag['body_snippet']}")
            if diag['gv_context']:
                print(f"      GV context: {diag['gv_context'][:60]}")
        
        all_diagnostics.extend(result['diagnostics'])
    
    # Write diagnostics TSV
    if all_diagnostics:
        with open(DIAGNOSTIC_OUT, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_diagnostics[0].keys(), delimiter='\t')
            writer.writeheader()
            writer.writerows(all_diagnostics)
        print(f"\nDiagnostics written to {DIAGNOSTIC_OUT}")


if __name__ == '__main__':
    main()
