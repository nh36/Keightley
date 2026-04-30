#!/usr/bin/env python3
"""
Fix footnote ordering by handling inline footnotes embedded in prose.
Footnotes can appear:
1. Inline in prose: <!-- FOOTNOTE:N -->...<!-- /FOOTNOTE -->
2. Separately after prose: <!-- FOOTNOTE-UNANCHORED:N -->...<!-- /FOOTNOTE -->
"""

import re
import sys
from pathlib import Path
from collections import OrderedDict

def extract_all_footnotes(content: str):
    """Extract all footnotes (inline and separate) and their positions."""
    footnotes = {}
    positions = []
    
    for match in re.finditer(r'<!-- (?:FOOTNOTE|FOOTNOTE-UNANCHORED):(\d+) -->(.*?)<!-- /FOOTNOTE -->', content, re.DOTALL):
        fn_no = int(match.group(1))
        fn_body = match.group(2)
        footnotes[fn_no] = fn_body
        positions.append((match.start(), match.end(), fn_no))
    
    return footnotes, sorted(positions)

def rebuild_page_with_sorted_footnotes(content: str):
    """Rebuild page with all footnotes in sorted order."""
    # Split content into parts (before any footnote, and after all footnotes)
    first_match = re.search(r'<!-- (?:FOOTNOTE|FOOTNOTE-UNANCHORED):\d+ -->', content)
    if not first_match:
        return content
    
    # Find the last footnote end
    matches = list(re.finditer(r'<!-- /FOOTNOTE -->', content))
    if not matches:
        return content
    
    last_fn_end = matches[-1].end()
    prose_part = content[:first_match.start()]
    final_part = content[last_fn_end:]
    
    # Extract all footnotes
    footnotes = {}
    for match in re.finditer(r'<!-- (?:FOOTNOTE|FOOTNOTE-UNANCHORED):(\d+) -->(.*?)<!-- /FOOTNOTE -->', content, re.DOTALL):
        fn_no = int(match.group(1))
        fn_body = match.group(2)
        footnotes[fn_no] = fn_body
    
    # Sort footnotes by number
    sorted_fn_numbers = sorted(footnotes.keys())
    
    # Rebuild footnotes section in correct order
    footnotes_section = ''
    for fn_no in sorted_fn_numbers:
        footnotes_section += f'<!-- FOOTNOTE:{fn_no} -->{footnotes[fn_no]}<!-- /FOOTNOTE -->'
    
    # Return reconstructed content
    result = prose_part + footnotes_section + final_part
    return result

def get_footnote_order(content: str):
    """Get the order of footnotes as they appear."""
    return sorted([int(m) for m in re.findall(r'<!-- (?:FOOTNOTE|FOOTNOTE-UNANCHORED):(\d+) -->', content)])

def fix_page(page_num: int) -> bool:
    """Fix footnote ordering on a single page."""
    page_file = Path(f'build/ocr/cleaned_with_notes/p_{page_num:04d}.md')
    
    if not page_file.exists():
        print(f"✗ Page {page_num}: File not found")
        return False
    
    content = page_file.read_text()
    current_order = get_footnote_order(content)
    
    # Check if there are any unanchored footnotes (which would be out of order)
    unanchored = re.findall(r'<!-- FOOTNOTE-UNANCHORED:(\d+) -->', content)
    has_inline_footnotes = bool(re.search(r'<!-- FOOTNOTE:\d+ -->', content))
    
    if not (unanchored or has_inline_footnotes):
        print(f"✓ Page {page_num}: No footnotes")
        return True
    
    if not unanchored and not has_inline_footnotes:
        print(f"✓ Page {page_num}: Already clean")
        return True
    
    # Check if unanchored footnotes exist and are out of order
    if unanchored:
        unanchored_nums = [int(fn) for fn in unanchored]
        expected = sorted(set(current_order))
        unanchored_in_order = sorted(set(unanchored_nums))
        
        if unanchored_in_order != expected or len(current_order) != len(expected):
            print(f"\nPage {page_num}:")
            print(f"  Current order: {current_order}")
            print(f"  Expected order: {expected}")
            
            # Rebuild
            fixed_content = rebuild_page_with_sorted_footnotes(content)
            final_order = get_footnote_order(fixed_content)
            
            success = final_order == expected
            if success:
                print(f"  ✓ Fixed! New order: {final_order}")
                page_file.write_text(fixed_content)
            else:
                print(f"  ✗ Failed. Final order: {final_order}")
            
            return success
    
    print(f"✓ Page {page_num}: Already in order")
    return True

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
