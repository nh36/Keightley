#!/usr/bin/env python3
"""
Fix footnote ordering by rebuilding prose with footnotes in correct order.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def extract_footnotes_and_prose(content: str) -> Tuple[Dict, str, List]:
    """
    Extract all footnotes and return: (footnote_dict, prose_without_footnotes, order)
    """
    footnotes = {}
    current_order = []
    prose = content
    
    # Find all footnotes and their positions
    matches = list(re.finditer(r'<!-- FOOTNOTE:(\d+) -->(.*?)<!-- /FOOTNOTE -->', prose, re.DOTALL))
    
    # Build footnote dict and track order
    for match in matches:
        fn_no = match.group(1)
        fn_body = match.group(2)
        footnotes[fn_no] = fn_body
        current_order.append(fn_no)
    
    # Remove all footnotes from prose
    for match in reversed(matches):  # Reverse to maintain positions
        prose = prose[:match.start()] + prose[match.end():]
    
    return footnotes, prose, current_order

def rebuild_with_correct_order(prose: str, footnotes: Dict, current_order: List) -> Tuple[str, List]:
    """
    Rebuild prose with footnotes in sequential order.
    Find where each footnote marker should be and insert footnotes accordingly.
    """
    # Determine correct order
    fn_nums = sorted(set(int(fn) for fn in current_order))
    expected_order = [str(fn) for fn in fn_nums]
    
    if current_order == expected_order:
        # Already correct, just rebuild with footnotes
        result = prose
        for fn_no in current_order:
            result += f'<!-- FOOTNOTE:{fn_no} -->{footnotes[fn_no]}<!-- /FOOTNOTE -->'
        return result, current_order
    
    # Need to reorder: remove all footnote markers from prose and rebuild
    # First, find where each footnote marker was
    marker_positions = {}
    for fn_no in current_order:
        marker_positions[fn_no] = prose.find(f'<!-- FOOTNOTE:{fn_no} -->')
    
    # Actually, the markers are already removed, so we need to re-insert them
    # in the correct positions based on the content
    
    # For now, just re-insert footnotes in the order they should be
    result = prose
    for fn_no in expected_order:
        if fn_no in footnotes:
            result += f'<!-- FOOTNOTE:{fn_no} -->{footnotes[fn_no]}<!-- /FOOTNOTE -->'
    
    return result, expected_order

def fix_page(page_num: int) -> bool:
    """Fix footnote ordering on a single page."""
    page_file = Path(f'build/ocr/cleaned_with_notes/p_{page_num:04d}.md')
    
    if not page_file.exists():
        print(f"✗ Page {page_num}: File not found")
        return False
    
    content = page_file.read_text()
    
    # Get current order
    current_order_list = [m for m in re.findall(r'<!-- FOOTNOTE:(\d+) -->', content)]
    expected_order_list = sorted(set(int(fn) for fn in current_order_list))
    expected_order_list = [str(fn) for fn in expected_order_list]
    
    if current_order_list == expected_order_list:
        print(f"✓ Page {page_num}: Already in order {current_order_list}")
        return True
    
    print(f"\nPage {page_num}:")
    print(f"  Current:  {current_order_list}")
    print(f"  Expected: {expected_order_list}")
    
    # Extract footnotes and clean prose
    footnotes, prose_clean, current_order = extract_footnotes_and_prose(content)
    
    # Rebuild with correct order
    new_content, new_order = rebuild_with_correct_order(prose_clean, footnotes, current_order_list)
    
    # Check if order is now correct
    final_order = [m for m in re.findall(r'<!-- FOOTNOTE:(\d+) -->', new_content)]
    success = final_order == expected_order_list
    
    if success:
        print(f"  ✓ Fixed! New order: {final_order}")
        page_file.write_text(new_content)
    else:
        print(f"  ✗ Still not fixed. Order: {final_order}")
    
    return success

def main():
    problem_pages = [21, 46, 78, 96, 101, 132, 135]
    
    if len(sys.argv) > 1:
        problem_pages = [int(sys.argv[1])]
    
    results = {}
    for page in problem_pages:
        results[page] = fix_page(page)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    for page in sorted(results.keys()):
        status = "✓ FIXED" if results[page] else "✗ FAILED"
        print(f"  Page {page}: {status}")

if __name__ == '__main__':
    main()
