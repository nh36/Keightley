#!/usr/bin/env python3
"""Fix footnote ordering on page 21 - improved version.

Extracts all misplaced footnotes first, removes them, then inserts at correct positions.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CWN_FILE = ROOT / "build" / "ocr" / "cleaned_with_notes" / "p_0021.md"


def extract_all_footnotes(content: str) -> dict[int, str]:
    """Extract all footnote bodies by number."""
    footnotes = {}
    for fn_no in range(1, 200):  # Scan for up to 200 footnotes
        pattern = rf'<!-- FOOTNOTE(?:-UNANCHORED)?:{fn_no} -->(.+?)<!-- /FOOTNOTE -->'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            footnotes[fn_no] = match.group(0)  # Include the full sentinel
    return footnotes


def remove_all_footnotes(content: str) -> str:
    """Remove all footnote sentinels from content."""
    content = re.sub(r'<!-- FOOTNOTE[^>]*\d[^>]*-->', '', content)
    content = re.sub(r'<!-- FOOTNOTE-UNANCHORED[^>]*\d[^>]*-->.*?<!-- /FOOTNOTE -->', '', content, flags=re.DOTALL)
    content = re.sub(r'<!-- FOOTNOTE:\d+ -->.*?<!-- /FOOTNOTE -->', '', content, flags=re.DOTALL)
    return content


def insert_footnote_before(content: str, fn_body: str, before_text: str, is_regex: bool = False) -> tuple[str, bool]:
    """Insert footnote before specified text."""
    if is_regex:
        match = re.search(before_text, content)
        if not match:
            return content, False
        insert_pos = match.start()
    else:
        insert_pos = content.find(before_text)
        if insert_pos < 0:
            return content, False
    
    return content[:insert_pos] + fn_body + content[insert_pos:], True


def fix_page_21():
    """Fix footnote ordering on page 21."""
    print("=" * 70)
    print("FIXING PAGE 21 FOOTNOTE ORDERING - IMPROVED")
    print("=" * 70)
    
    if not CWN_FILE.exists():
        print(f"ERROR: {CWN_FILE} not found")
        return False
    
    content = CWN_FILE.read_text()
    
    # Step 1: Extract all footnotes
    print("\nStep 1: Extracting all footnotes...")
    footnotes = extract_all_footnotes(content)
    print(f"  Found {len(footnotes)} footnotes: {sorted(footnotes.keys())}")
    
    # FN 4 and 9 are misplaced
    if 4 not in footnotes:
        print("  ERROR: FN 4 not found!")
        return False
    if 9 not in footnotes:
        print("  ERROR: FN 9 not found!")
        return False
    
    fn4_body = footnotes[4]
    fn9_body = footnotes[9]
    
    # Step 2: Remove all footnotes from content
    print("\nStep 2: Removing all footnotes from prose...")
    content = remove_all_footnotes(content)
    
    # Step 3: Re-insert footnotes in correct order
    print("\nStep 3: Re-inserting footnotes in correct positions...")
    
    # Order and positions:
    # FN 4 should be before "dendrochronologically" (around position 4231)
    # FN 5 should be after "Yamato Japan in the third century"
    # FN 6 should be after "eighth century"
    # FN 7 should be after "before the battle of Chalons in A.D."
    # FN 8 should be after "nonGreek peoples"
    # FN 9 should be somewhere in the introduction (after Satow citation)
    # FN 10 should be after "grandson, Mangu"
    # FN 11 should be after "porcupines;"
    # FN 12 should be after "Labrador in the east"
    
    insertions = [
        (5, "Japan in the third century", False),  # FN 5
        (6, "eighth century.", False),             # FN 6
        (7, "before the battle of Chalons", False), # FN 7
        (8, "nonGreek) peoples.", False),          # FN 8
        (9, "Satow (1879), pp. 429-433", False),   # FN 9 - right after the citation
        (10, "grandson, Mangu.", False),           # FN 10
        (11, "porcupines;", False),                # FN 11
        (4, "dendrochronologically", False),       # FN 4 - last to avoid shifting positions
        (12, "east.", False),                      # FN 12 - very last
    ]
    
    for fn_no, before_text, is_regex in insertions:
        if fn_no not in footnotes:
            print(f"  ⚠ FN {fn_no} not in extracted footnotes")
            continue
        
        fn_body = footnotes[fn_no]
        content, success = insert_footnote_before(content, fn_body, before_text, is_regex)
        if success:
            print(f"  ✓ FN {fn_no} inserted before: '{before_text[:40]}...'")
        else:
            print(f"  ✗ FN {fn_no} could not find: '{before_text[:40]}...'")
            # Try to find a good fallback position
            # Just append it at end as unanchored
            print(f"      → Appending as UNANCHORED")
            content += f"\n<!-- FOOTNOTE-UNANCHORED:{fn_no} -->{footnotes[fn_no].split('-->')[1]}\n"
    
    # Step 4: Save and verify
    print("\n" + "=" * 70)
    print("Saving corrected page...")
    CWN_FILE.write_text(content)
    
    # Verify
    print("\nVerification:")
    markers = re.findall(r'<!-- FOOTNOTE:(\d+) -->', content)
    print(f"  Footnotes in order: {markers}")
    is_ordered = all(int(markers[i]) <= int(markers[i+1]) for i in range(len(markers)-1))
    print(f"  All ordered: {'✓' if is_ordered else '✗'}")
    
    return is_ordered


if __name__ == '__main__':
    success = fix_page_21()
    exit(0 if success else 1)
