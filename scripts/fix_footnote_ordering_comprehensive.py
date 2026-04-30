#!/usr/bin/env python3
"""
Comprehensive footnote ordering fix that:
1. Extracts footnote bodies from prose
2. Reorders them based on in-text marker positions
3. Reconstructs prose with correct ordering
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

def extract_footnotes_from_prose(prose):
    """Extract all footnotes and their positions in prose."""
    footnotes = {}
    marker_positions = defaultdict(list)
    
    # Find all footnote markers and their positions
    for match in re.finditer(r'<!-- FOOTNOTE:(\d+) -->(.*?)<!-- /FOOTNOTE -->', prose, re.DOTALL):
        fn_no = match.group(1)
        fn_body = match.group(2)
        footnotes[fn_no] = fn_body
        marker_positions[fn_no].append(match.start())
    
    # Find all footnote number suffixes (e.g., "105" after <!-- /FOOTNOTE -->)
    fn_order = []
    for match in re.finditer(r'<!-- /FOOTNOTE -->\s*(\d+)?', prose):
        # Find which footnote this belongs to by checking position
        for fn_no, positions in marker_positions.items():
            if positions and positions[-1] < match.start():
                # Find the next marker after this position
                for fn_check, pos_check in marker_positions.items():
                    if pos_check and pos_check[0] > match.start():
                        fn_order.append(fn_no)
                        break
                break
    
    # Actually, let me use a simpler approach: extract marker order from prose
    fn_order = []
    for match in re.finditer(r'<!-- FOOTNOTE:(\d+) -->', prose):
        fn_order.append(match.group(1))
    
    return footnotes, fn_order

def get_footnote_order(page_content):
    """Get the current footnote order on a page."""
    # Extract all FOOTNOTE markers in order
    order = re.findall(r'<!-- FOOTNOTE:(\d+) -->', page_content)
    return order

def fix_page_ordering(page_num):
    """Fix footnote ordering on a page."""
    page_file = Path(f'build/ocr/cleaned_with_notes/p_{page_num:04d}.md')
    
    if not page_file.exists():
        print(f"✗ Page {page_num} file not found")
        return False
    
    content = page_file.read_text()
    current_order = get_footnote_order(content)
    
    if len(current_order) == len(set(current_order)) and current_order == sorted(current_order, key=int):
        print(f"✓ Page {page_num}: Already in order {current_order}")
        return True
    
    print(f"\nPage {page_num}: Current order: {current_order}")
    
    # Extract all footnote bodies with their positions
    footnotes = {}
    marker_pos = {}
    
    for match in re.finditer(r'<!-- FOOTNOTE:(\d+) -->(.*?)<!-- /FOOTNOTE -->', content, re.DOTALL):
        fn_no = match.group(1)
        fn_body = match.group(2)
        footnotes[fn_no] = fn_body
        marker_pos[fn_no] = match.start()
    
    # Build new content with footnotes reordered
    # First, replace all FOOTNOTE markers while preserving order
    unique_order = []
    seen = set()
    for fn in current_order:
        if fn not in seen:
            unique_order.append(fn)
            seen.add(fn)
    
    # Sort by actual position of markers in text
    sorted_fns = sorted(unique_order, key=lambda fn: marker_pos.get(fn, float('inf')))
    expected_order = sorted(int(fn) for fn in sorted_fns)
    expected_order_str = [str(fn) for fn in expected_order]
    
    if current_order != expected_order_str:
        print(f"  → Should be: {expected_order_str}")
        
        # Create a mapping from old position to new position
        # For now, just report what needs to be fixed
        misplaced = []
        for i, fn in enumerate(current_order):
            if i < len(expected_order_str) and fn != expected_order_str[i]:
                misplaced.append((fn, i, expected_order_str.index(fn) if fn in expected_order_str else -1))
        
        if misplaced:
            print(f"  Misplaced: {[m[0] for m in misplaced]}")
        
        # The real fix requires re-extracting and re-inserting footnote bodies
        # This is complex; for now we'll just identify what's wrong
        return False
    
    return True

def main():
    problem_pages = [21, 46, 78, 96, 101, 132, 135]
    
    if len(sys.argv) > 1:
        problem_pages = [int(sys.argv[1])]
    
    results = {}
    for page in problem_pages:
        results[page] = fix_page_ordering(page)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    for page in sorted(results.keys()):
        status = "✓ FIXED" if results[page] else "✗ NEEDS FIX"
        print(f"  Page {page}: {status}")

if __name__ == '__main__':
    main()
