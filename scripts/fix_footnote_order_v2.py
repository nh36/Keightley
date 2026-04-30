#!/usr/bin/env python3
"""
Fix footnote ordering by swapping inline footnote positions while preserving structure.
"""

import re
import sys
from pathlib import Path
from collections import OrderedDict

def get_footnote_order(content: str) -> list:
    """Get the order of footnotes as they appear in content."""
    return [m for m in re.findall(r'<!-- FOOTNOTE:(\d+) -->', content)]

def get_expected_order(content: str) -> list:
    """Get the expected sequential order for footnotes."""
    current = get_footnote_order(content)
    unique_fns = sorted(set(int(fn) for fn in current))
    return [str(fn) for fn in unique_fns]

def find_footnote_positions(content: str):
    """Find start/end positions of each footnote block."""
    positions = {}
    for match in re.finditer(r'<!-- FOOTNOTE:(\d+) -->(.*?)<!-- /FOOTNOTE -->', content, re.DOTALL):
        fn_no = match.group(1)
        positions[fn_no] = (match.start(), match.end(), match.group(0))
    return positions

def swap_footnotes_in_place(content: str, fn1: str, fn2: str) -> str:
    """Swap two footnote blocks in content while preserving structure."""
    # Find both footnotes
    pattern1 = r'<!-- FOOTNOTE:' + fn1 + r' -->(.*?)<!-- /FOOTNOTE -->'
    pattern2 = r'<!-- FOOTNOTE:' + fn2 + r' -->(.*?)<!-- /FOOTNOTE -->'
    
    match1 = re.search(pattern1, content, re.DOTALL)
    match2 = re.search(pattern2, content, re.DOTALL)
    
    if not match1 or not match2:
        return content
    
    # Extract the blocks
    block1_full = match1.group(0)
    block2_full = match2.group(0)
    
    # Find which comes first
    if match1.start() < match2.start():
        # Swap: replace first with second, then second with first
        content_after_first = content[:match1.start()] + block2_full + content[match1.end():]
        match2_new = re.search(pattern2, content_after_first, re.DOTALL)
        if match2_new:
            result = content_after_first[:match2_new.start()] + block1_full + content_after_first[match2_new.end():]
            return result
    else:
        # Swap: replace second with first, then first with second
        content_after_second = content[:match2.start()] + block1_full + content[match2.end():]
        match1_new = re.search(pattern1, content_after_second, re.DOTALL)
        if match1_new:
            result = content_after_second[:match1_new.start()] + block2_full + content_after_second[match1_new.end():]
            return result
    
    return content

def fix_ordering_bubble_sort(content: str) -> str:
    """Fix footnote ordering using bubble sort of footnote blocks."""
    current_order = get_footnote_order(content)
    expected_order = get_expected_order(content)
    
    if current_order == expected_order:
        return content
    
    # Use bubble sort to swap misplaced footnotes
    for i in range(len(current_order)):
        for j in range(len(current_order) - 1 - i):
            fn1 = current_order[j]
            fn2 = current_order[j+1]
            
            if int(fn1) > int(fn2):
                # Swap them
                content = swap_footnotes_in_place(content, fn1, fn2)
                current_order[j], current_order[j+1] = current_order[j+1], current_order[j]
    
    return content

def fix_page(page_num: int) -> bool:
    """Fix footnote ordering on a single page."""
    page_file = Path(f'build/ocr/cleaned_with_notes/p_{page_num:04d}.md')
    
    if not page_file.exists():
        print(f"✗ Page {page_num}: File not found")
        return False
    
    content = page_file.read_text()
    current_order = get_footnote_order(content)
    expected_order = get_expected_order(content)
    
    if current_order == expected_order:
        print(f"✓ Page {page_num}: Already in order {current_order}")
        return True
    
    print(f"\nPage {page_num}:")
    print(f"  Current:  {current_order}")
    print(f"  Expected: {expected_order}")
    
    # Fix the ordering
    fixed_content = fix_ordering_bubble_sort(content)
    final_order = get_footnote_order(fixed_content)
    
    success = final_order == expected_order
    if success:
        print(f"  ✓ Fixed! New order: {final_order}")
        page_file.write_text(fixed_content)
    else:
        print(f"  ✗ Failed. Order: {final_order}")
        print(f"  Debug: Current lengths: content={len(content)}, fixed={len(fixed_content)}")
    
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
