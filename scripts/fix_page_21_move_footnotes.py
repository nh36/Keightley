#!/usr/bin/env python3
"""Systematically fix footnote ordering issues on page 21.

Based on semantic analysis of footnote content and prose context:
- FN 4: belongs before "dendrochronologically adjusted carbon-14"
- FN 9: belongs after "Satow (1879), pp. 429-433" citation in FN 6 body

The problem is that both FN 4 and 9 lack superscript markers in both
GV and Tesseract, so auto-matching placed them in wrong locations.

Solution: Manually move these footnotes to semantically correct positions.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CWN_FILE = ROOT / "build" / "ocr" / "cleaned_with_notes" / "p_0021.md"


def move_footnote(content: str, fn_no: int, before_text: str, before_regex: bool = False) -> tuple[str, bool]:
    """Move footnote to a new position.
    
    Args:
        content: Page markdown content
        fn_no: Footnote number to move
        before_text: Text to insert footnote before (literal string or regex)
        before_regex: If True, treat before_text as regex pattern
    
    Returns:
        (modified_content, success)
    """
    # Extract footnote (anchored or unanchored)
    pattern = rf'<!-- FOOTNOTE(?:-UNANCHORED)?:{fn_no} -->(.+?)<!-- /FOOTNOTE -->'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"  ✗ Could not find FN {fn_no}")
        return content, False
    
    fn_body = match.group(0)  # Full sentinel
    
    # Remove from current location
    content = content[:match.start()] + content[match.end():]
    
    # Find insertion point
    if before_regex:
        insert_match = re.search(before_text, content)
        if insert_match:
            insert_pos = insert_match.start()
        else:
            print(f"  ✗ Could not find regex pattern: {before_text}")
            return content, False
    else:
        insert_pos = content.find(before_text)
        if insert_pos < 0:
            print(f"  ✗ Could not find text: {before_text[:50]}")
            return content, False
    
    # Insert footnote before the text
    content = content[:insert_pos] + fn_body + content[insert_pos:]
    
    print(f"  ✓ FN {fn_no} moved before: {before_text[:40]}...")
    return content, True


def fix_page_21():
    """Fix footnote ordering on page 21."""
    print("=" * 70)
    print("FIXING PAGE 21 FOOTNOTE ORDERING")
    print("=" * 70)
    
    if not CWN_FILE.exists():
        print(f"ERROR: {CWN_FILE} not found")
        return False
    
    content = CWN_FILE.read_text()
    
    print("\nStep 1: Move FN 4 to before 'dendrochronologically'")
    # FN 4 should be just before "dendrochronologically adjusted"
    content, success_4 = move_footnote(content, 4, "dendrochronologically")
    
    print("\nStep 2: Move FN 9 to after 'Satow (1879)' citation")
    # FN 9 should be right after the FN 6 sentinel (which contains Satow citation)
    # Actually, FN 9 is the footnote for the Satow reference itself
    content, success_9 = move_footnote(content, 9, r'<!-- /FOOTNOTE -->\n\nFar to the west', before_regex=True)
    
    if not success_9:
        print("\n  Retry: Move FN 9 after FN 6 closing tag")
        content, success_9 = move_footnote(content, 9, r'Satow \(1879\)', before_regex=True)
    
    if success_4 or success_9:
        print("\n" + "=" * 70)
        print("Saving corrected page...")
        CWN_FILE.write_text(content)
        print(f"✓ Page 21 corrected and saved to {CWN_FILE}")
        
        # Verify
        print("\nVerification:")
        markers = re.findall(r'<!-- FOOTNOTE:(\d+) -->', content)
        print(f"  Footnotes in order: {markers}")
        is_ordered = all(int(markers[i]) <= int(markers[i+1]) for i in range(len(markers)-1))
        print(f"  Ordered: {'✓' if is_ordered else '✗'}")
        
        return is_ordered
    else:
        print("\n✗ No changes made")
        return False


if __name__ == '__main__':
    success = fix_page_21()
    exit(0 if success else 1)
