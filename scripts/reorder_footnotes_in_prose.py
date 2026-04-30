#!/usr/bin/env python3
"""
Reorder footnotes in prose by moving their marker positions to maintain sequential order.
"""

import re
import sys
from pathlib import Path

def extract_footnote_blocks(content):
    """Extract all footnote blocks: (fn_no, start_pos, end_pos, body)"""
    blocks = []
    for match in re.finditer(r'(<!-- FOOTNOTE:(\d+) -->.*?<!-- /FOOTNOTE -->)', content, re.DOTALL):
        fn_no = int(match.group(2))
        blocks.append({
            'fn_no': fn_no,
            'full_marker': match.group(1),
            'start': match.start(),
            'end': match.end(),
        })
    return sorted(blocks, key=lambda b: b['start'])

def find_footnote_order_in_prose(content):
    """Find the order of footnote markers as they appear in prose."""
    return [int(m) for m in re.findall(r'<!-- FOOTNOTE:(\d+) -->', content)]

def reorder_footnotes(content):
    """Reorder footnotes to be sequential."""
    current_order = find_footnote_order_in_prose(content)
    blocks = extract_footnote_blocks(content)
    
    if not blocks:
        return content, current_order, current_order
    
    # Determine correct order (sequential from min to max)
    fn_nums = sorted(set(current_order))
    expected_order = fn_nums
    
    if current_order == expected_order:
        return content, current_order, expected_order
    
    # Extract blocks into a dict for easy access
    block_dict = {b['fn_no']: b for b in blocks}
    
    # Find the text between footnotes (to preserve non-footnote content)
    # Strategy: remove all footnote blocks, then re-insert them in correct order
    
    # Remove all footnote blocks
    result = content
    for block in sorted(blocks, key=lambda b: -b['start']):  # Remove from end to start
        result = result[:block['start']] + result[block['end']:]
    
    # Find positions where each footnote marker was originally
    # We need to find where to re-insert them
    # For now, insert all footnotes at the end of prose (where the last one was)
    
    # Actually, a better approach: keep footnotes where they are, just swap misplaced ones
    # Extract each footnote block's text
    fn_blocks_text = {}
    for block in blocks:
        fn_blocks_text[block['fn_no']] = block['full_marker']
    
    # Now rebuild: keep document structure but reorder footnotes
    # Find all FOOTNOTE markers
    result = content
    
    # Replace markers to enforce order
    for i, fn_no in enumerate(expected_order):
        if i < len(current_order) and current_order[i] != fn_no:
            # Need to swap
            # Find position of expected_order[i] footnote
            for j in range(i+1, len(current_order)):
                if current_order[j] == fn_no:
                    # Swap footnotes at positions i and j
                    current_order[i], current_order[j] = current_order[j], current_order[i]
                    
                    # Find the actual blocks and swap them in the content
                    # This is getting complex; let me use a simpler approach
                    break
    
    return content, current_order, expected_order

def fix_page(page_num):
    """Fix footnote ordering on a single page."""
    page_file = Path(f'build/ocr/cleaned_with_notes/p_{page_num:04d}.md')
    
    if not page_file.exists():
        print(f"✗ Page {page_num}: File not found")
        return False
    
    content = page_file.read_text()
    current_order = find_footnote_order_in_prose(content)
    expected_order = sorted(set(current_order))
    
    if current_order == expected_order:
        print(f"✓ Page {page_num}: Already in order")
        return True
    
    print(f"\nPage {page_num}:")
    print(f"  Current: {current_order}")
    print(f"  Expected: {expected_order}")
    
    # Simple fix for adjacent swaps
    result = content
    for i in range(len(current_order) - 1):
        if current_order[i] > current_order[i+1]:
            print(f"  Swap positions {i} and {i+1}: {current_order[i]} ↔ {current_order[i+1]}")
            # Find these two footnotes in content and swap them
            fn1, fn2 = current_order[i], current_order[i+1]
            
            # Find the FOOTNOTE blocks
            pattern1 = r'(<!-- FOOTNOTE:' + str(fn1) + r' -->.*?<!-- /FOOTNOTE -->)'
            pattern2 = r'(<!-- FOOTNOTE:' + str(fn2) + r' -->.*?<!-- /FOOTNOTE -->)'
            
            match1 = re.search(pattern1, result, re.DOTALL)
            match2 = re.search(pattern2, result, re.DOTALL)
            
            if match1 and match2:
                # Swap the blocks
                text1 = match1.group(1)
                text2 = match2.group(1)
                
                # Replace first match with second, second with first
                result = result[:match1.start()] + text2 + result[match1.end():]
                # Find match2 again in the modified string
                match2_new = re.search(pattern2, result, re.DOTALL)
                if match2_new:
                    result = result[:match2_new.start()] + text1 + result[match2_new.end():]
                
                current_order[i], current_order[i+1] = current_order[i+1], current_order[i]
    
    # Check final order
    final_order = find_footnote_order_in_prose(result)
    success = final_order == expected_order
    
    if success:
        print(f"  ✓ Fixed! New order: {final_order}")
        page_file.write_text(result)
    else:
        print(f"  ✗ Fix incomplete. Order is now: {final_order}")
    
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
