#!/usr/bin/env python3
"""Comprehensive footnote ordering fix that unanchors and re-anchors misplaced notes.

This script:
1. Reads current page data
2. Finds misplaced footnotes (those not in numerical order)
3. Unanchors them
4. Applies manual anchors from manual_footnote_anchors.tsv
5. Verifies ordering is corrected

Usage:
  python3 scripts/fix_all_footnote_ordering.py [page]

If no page specified, fixes all problem pages.
"""

import re
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CWN_DIR = ROOT / "build" / "ocr" / "cleaned_with_notes"
MANUAL_ANCHORS_FILE = ROOT / "data" / "manual_footnote_anchors.tsv"

# Problem pages and their issues
PROBLEM_PAGES = {
    21: [5, 6, 7, 8, 10, 11, 4, 12, 9],
    46: [2, 3, 4, 8, 9, 7, 5, 6],
    78: [15, 16, 17, 18, 14, 19, 20],
    96: [87, 89, 88],
    101: [105, 104, 106, 107, 108, 109],
    132: [100, 99, 101, 102],
    135: [117, 118, 116, 119, 120, 121, 122, 123],
}


def load_manual_anchors():
    """Load manual anchor overrides."""
    anchors = {}
    try:
        with open(MANUAL_ANCHORS_FILE) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if not row or row[0].startswith('#') or len(row) < 3:
                    continue
                scan, fn_no, snippet = row[0], int(row[1]), row[2]
                key = (int(scan), fn_no)
                anchors[key] = snippet
    except Exception as e:
        print(f"Error loading manual anchors: {e}")
    return anchors


def find_misplaced_fns(fns_in_order):
    """Identify which footnotes are not in numerical order."""
    misplaced = []
    for i in range(len(fns_in_order) - 1):
        if fns_in_order[i] > fns_in_order[i+1]:
            # fns_in_order[i] is larger than next, so it's misplaced
            misplaced.append(fns_in_order[i])
    return misplaced


def unanchor_footnote(content, fn_no):
    """Convert anchored footnote to unanchored."""
    pattern = rf'<!-- FOOTNOTE:{fn_no} -->(.+?)<!-- /FOOTNOTE -->'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return content, False
    
    body = match.group(1)
    unanchored = f'<!-- FOOTNOTE-UNANCHORED:{fn_no} -->{body}<!-- /FOOTNOTE -->'
    
    # Remove from current location
    content = content[:match.start()] + content[match.end():]
    
    # Append to end
    content += f"\n{unanchored}\n"
    
    return content, True


def anchor_footnote(content, fn_no, snippet):
    """Find unanchored footnote and anchor it at snippet position."""
    # Find unanchored body
    pattern = rf'<!-- FOOTNOTE-UNANCHORED:{fn_no} -->(.+?)<!-- /FOOTNOTE -->'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return content, False
    
    body = match.group(1)
    
    # Remove from unanchored location
    content = content[:match.start()] + content[match.end():]
    
    # Find insertion point
    insert_pos = content.find(snippet)
    if insert_pos < 0:
        # Try with normalized whitespace
        normalized_snippet = re.sub(r'\s+', ' ', snippet)
        normalized_content = re.sub(r'\s+', ' ', content)
        normalized_pos = normalized_content.find(normalized_snippet)
        if normalized_pos < 0:
            # Can't find snippet, return as still unanchored
            content += f"\n<!-- FOOTNOTE-UNANCHORED:{fn_no} -->{body}<!-- /FOOTNOTE -->\n"
            return content, False
        # Map back to original
        insert_pos = 0
        for c in content:
            if normalized_content[insert_pos] == c or (c.isspace() and normalized_content[insert_pos].isspace()):
                insert_pos += 1
            if insert_pos >= normalized_pos + len(normalized_snippet):
                insert_pos = content.find(snippet[-10:], insert_pos - 10)
                break
    
    # Insert anchored footnote at snippet location
    anchored = f'<!-- FOOTNOTE:{fn_no} -->{body}<!-- /FOOTNOTE -->'
    content = content[:insert_pos] + anchored + content[insert_pos:]
    
    return content, True


def fix_page(page_num):
    """Fix footnote ordering on a specific page."""
    page_file = CWN_DIR / f"p_{page_num:04d}.md"
    if not page_file.exists():
        print(f"Page {page_num}: File not found")
        return False
    
    content = page_file.read_text()
    
    # Get current footnote order
    markers = re.findall(r'<!-- FOOTNOTE:(\d+) -->', content)
    current_order = [int(m) for m in markers]
    
    # Identify misplaced footnotes
    misplaced = find_misplaced_fns(current_order)
    
    if not misplaced:
        print(f"Page {page_num}: ✓ All in order: {current_order}")
        return True
    
    print(f"Page {page_num}: Current order: {current_order}")
    print(f"  Misplaced: {misplaced}")
    
    # Step 1: Unanchor misplaced footnotes
    for fn_no in misplaced:
        content, success = unanchor_footnote(content, fn_no)
        if success:
            print(f"  ✓ Unanchored FN {fn_no}")
        else:
            print(f"  ⚠ Could not unanchor FN {fn_no}")
    
    # Step 2: Apply manual anchors
    manual_anchors = load_manual_anchors()
    for fn_no in misplaced:
        key = (page_num, fn_no)
        if key in manual_anchors:
            snippet = manual_anchors[key]
            content, success = anchor_footnote(content, fn_no, snippet)
            if success:
                print(f"  ✓ Anchored FN {fn_no} at: {snippet[:40]}")
            else:
                print(f"  ✗ Could not anchor FN {fn_no}: snippet not found")
        else:
            print(f"  ⚠ No manual anchor for FN {fn_no}")
    
    # Step 3: Save and verify
    page_file.write_text(content)
    
    # Verify
    new_markers = re.findall(r'<!-- FOOTNOTE:(\d+) -->', content)
    new_order = [int(m) for m in new_markers]
    is_ordered = all(new_order[i] <= new_order[i+1] for i in range(len(new_order)-1))
    
    print(f"  After fix: {new_order} {'✓' if is_ordered else '✗'}")
    return is_ordered


def main():
    import sys
    
    if len(sys.argv) > 1:
        pages = [int(sys.argv[1])]
    else:
        pages = sorted(PROBLEM_PAGES.keys())
    
    print("=" * 70)
    print("FOOTNOTE ORDERING COMPREHENSIVE FIX")
    print("=" * 70)
    
    results = {}
    for page in pages:
        success = fix_page(page)
        results[page] = success
        print()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for page, success in results.items():
        status = "✓ FIXED" if success else "✗ FAILED"
        print(f"  Page {page}: {status}")


if __name__ == '__main__':
    main()
