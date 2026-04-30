#!/usr/bin/env python3
"""
Fix footnote ordering by extracting, sorting, and replacing footnote blocks.
"""

import re
import sys
from pathlib import Path

def fix_page(page_num: int) -> bool:
    """Fix footnote ordering on a single page."""
    page_file = Path(f'build/ocr/cleaned_with_notes/p_{page_num:04d}.md')
    
    if not page_file.exists():
        print(f"✗ Page {page_num}: File not found")
        return False
    
    content = page_file.read_text()
    
    # Extract all footnotes
    footnotes = {}
    for match in re.finditer(r'<!-- FOOTNOTE:(\d+) -->(.*?)<!-- /FOOTNOTE -->', content, re.DOTALL):
        fn_no = int(match.group(1))
        fn_body = match.group(2)
        footnotes[fn_no] = fn_body
    
    if not footnotes:
        print(f"✓ Page {page_num}: No footnotes found")
        return True
    
    # Get current order
    current_order = [int(m) for m in re.findall(r'<!-- FOOTNOTE:(\d+) -->', content)]
    expected_order = sorted(set(current_order))
    
    if current_order == expected_order:
        print(f"✓ Page {page_num}: Already in order")
        return True
    
    print(f"\nPage {page_num}:")
    print(f"  Current:  {current_order}")
    print(f"  Expected: {expected_order}")
    
    # Remove all footnote blocks from content
    result = re.sub(r'<!-- FOOTNOTE:\d+ -->.*?<!-- /FOOTNOTE -->', '', content, flags=re.DOTALL)
    
    # Find where the first footnote was (for insertion point)
    first_fn_match = re.search(r'<!-- FOOTNOTE:\d+ -->', content)
    if not first_fn_match:
        return False
    
    insertion_point = first_fn_match.start()
    
    # Build sorted footnote string
    sorted_footnotes_str = ''
    for fn_no in expected_order:
        if fn_no in footnotes:
            sorted_footnotes_str += f'<!-- FOOTNOTE:{fn_no} -->{footnotes[fn_no]}<!-- /FOOTNOTE -->'
    
    # Insert sorted footnotes at original position
    result = result[:insertion_point] + sorted_footnotes_str + result[insertion_point:]
    
    # Verify
    final_order = [int(m) for m in re.findall(r'<!-- FOOTNOTE:(\d+) -->', result)]
    success = final_order == expected_order
    
    if success:
        print(f"  ✓ Fixed! New order: {final_order}")
        page_file.write_text(result)
    else:
        print(f"  ✗ Failed. Final order: {final_order}")
    
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
