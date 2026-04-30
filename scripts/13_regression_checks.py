#!/usr/bin/env python3
"""
Regression check suite for document quality.
Ensures previous fixes don't regress in future regenerations.
"""

import re
import sys
from pathlib import Path

def check_title_page_formatting():
    """Verify title page doesn't have escaped markdown headers."""
    title_tex = Path('tex/frontmatter/title.tex').read_text()
    
    # Check for escaped markdown headers (regression indicator)
    if r'\#' in title_tex:
        return False, "Title page has escaped markdown headers (\\#)"
    
    # Check that actual markdown headers are present
    if '# Sources of Shang History' not in title_tex:
        return False, "Title page missing markdown header"
    
    return True, "Title page formatting OK"

def check_footnote_order():
    """Verify footnotes are in sequence on first page with notes."""
    from pathlib import Path
    import re
    
    ch01 = Path('tex/chapters/ch01.tex').read_text()
    
    # Extract footnote numbers from first 50 footnotes
    footnote_nums = re.findall(r'\\footnote\[(\d+)\]', ch01)[:20]
    
    if not footnote_nums:
        return True, "No footnotes found (OK)"
    
    # Check if they're in ascending order
    footnote_nums = [int(n) for n in footnote_nums]
    if footnote_nums != sorted(footnote_nums):
        return False, f"Footnotes out of order: {footnote_nums[:5]}"
    
    return True, "Footnote ordering OK"

def check_section_numbers():
    """Verify section markers are present and valid."""
    ch01 = Path('tex/chapters/ch01.tex').read_text()
    
    # Count section commands
    sections = len(re.findall(r'\\section\[', ch01))
    subsections = len(re.findall(r'\\subsection\[', ch01))
    
    if sections + subsections < 1:
        return False, "No section commands found in ch01"
    
    # Check for \origsecnum markers
    if r'\origsecnum' not in ch01:
        return False, "Missing \\origsecnum macro in section titles"
    
    return True, f"Section structure OK ({sections} sections, {subsections} subsections)"

def check_quotation_marks():
    """Verify LaTeX-style quotation marks are used."""
    ch01 = Path('tex/chapters/ch01.tex').read_text()
    
    # Check for straight quotes in chapter content (excluding comments)
    # Remove comments first
    without_comments = re.sub(r'%.*', '', ch01)
    
    # Count straight double quotes (should be minimal)
    straight_quotes = len(re.findall(r'(?<![`\'])"(?!["`\'])', without_comments))
    
    if straight_quotes > 5:  # Allow a few edge cases
        return False, f"Too many straight quotes found: {straight_quotes}"
    
    # Check for LaTeX-style quotes
    backtick_quotes = len(re.findall(r'``|\'\'', without_comments))
    if backtick_quotes < 10:
        return False, "Few LaTeX-style quotes found"
    
    return True, "Quotation marks OK"

def check_frontmatter_cleanup():
    """Verify frontmatter pages don't have embedded page numbers."""
    frontmatter_files = list(Path('build/ocr/cleaned_with_notes').glob('p_000[0-9].md'))
    
    for md_file in frontmatter_files:
        content = md_file.read_text()
        
        # Check for stray page number patterns in frontmatter
        page_numbers = re.findall(r'^(?:xv|xvi|xi|xii|xiii|xiv|i|ii|iii|iv|v|vi|vii|viii|ix|x|·)$', content, re.MULTILINE)
        
        if len(page_numbers) > 3:  # Allow a few, but not many
            return False, f"Frontmatter page {md_file.name} has {len(page_numbers)} stray page markers"
    
    return True, "Frontmatter cleanup OK"

def main():
    """Run all regression checks."""
    checks = [
        ("Title Page Formatting", check_title_page_formatting),
        ("Footnote Order", check_footnote_order),
        ("Section Numbers", check_section_numbers),
        ("Quotation Marks", check_quotation_marks),
        ("Frontmatter Cleanup", check_frontmatter_cleanup),
    ]
    
    print("Running regression checks...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, check_fn in checks:
        try:
            ok, msg = check_fn()
            status = "✅ PASS" if ok else "❌ FAIL"
            print(f"{status} | {name:25} | {msg}")
            if ok:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ ERROR | {name:25} | {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
