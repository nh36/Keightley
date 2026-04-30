#!/usr/bin/env python3
"""
Fix footnote ordering by performing swaps and re-checking after each one.
"""

import re
import sys
from pathlib import Path

def get_footnote_order(content: str) -> list:
    """Get the order of footnotes as they appear in content."""
    return [m for m in re.findall(r'<!-- FOOTNOTE:(\d+) -->', content)]

def swap_adjacent_footnotes(content: str, fn1: str, fn2: str) -> str:
    """Swap two adjacent footnote blocks."""
    pattern1 = r'(<!-- FOOTNOTE:' + re.escape(fn1) + r' -->.*?<!-- /FOOTNOTE -->)'
    pattern2 = r'(<!-- FOOTNOTE:' + re.escape(fn2) + r' -->.*?<!-- /FOOTNOTE -->)'
    
    # Find the exact pattern of fn1 followed by fn2
    combined_pattern = pattern1 + r'(\s*)' + pattern2
    match = re.search(combined_pattern, content, re.DOTALL)
    
    if match:
        # Extract the blocks and whitespace
        block1 = match.group(1)
        whitespace = match.group(3)
        block2 = match.group(2)
        
        # Replace with swapped order
        replacement = block2 + whitespace + block1
        result = content[:match.start()] + replacement + content[match.end():]
        return result
    
    return content

def fix_page(page_num: int) -> bool:
    """Fix footnote ordering on a single page."""
    page_file = Path(f'build/ocr/cleaned_with_notes/p_{page_num:04d}.md')
    
    if not page_file.exists():
        print(f"✗ Page {page_num}: File not found")
        return False
    
    content = page_file.read_text()
    current_order = get_footnote_order(content)
    expected_order = sorted(set(int(fn) for fn in current_order))
    expected_order_str = [str(fn) for fn in expected_order]
    
    if current_order == expected_order_str:
        print(f"✓ Page {page_num}: Already in order {current_order}")
        return True
    
    print(f"\nPage {page_num}:")
    print(f"  Current:  {current_order}")
    print(f"  Expected: {expected_order_str}")
    
    # Keep swapping until order is correct
    max_iterations = 100
    iteration = 0
    while current_order != expected_order_str and iteration < max_iterations:
        iteration += 1
        
        # Find first pair that's out of order
        for i in range(len(current_order) - 1):
            if int(current_order[i]) > int(current_order[i+1]):
                # Swap them
                fn1 = current_order[i]
                fn2 = current_order[i+1]
                print(f"  Iteration {iteration}: Swap FN {fn1} ↔ FN {fn2}")
                
                content = swap_adjacent_footnotes(content, fn1, fn2)
                current_order = get_footnote_order(content)
                break
    
    success = current_order == expected_order_str
    if success:
        print(f"  ✓ Fixed in {iteration} iterations! New order: {current_order}")
        page_file.write_text(content)
    else:
        print(f"  ✗ Failed after {iteration} iterations. Final order: {current_order}")
    
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
