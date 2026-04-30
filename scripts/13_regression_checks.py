#!/usr/bin/env python3
"""
Regression check suite for document quality.
Ensures previous fixes don't regress in future regenerations.
"""

import re
import sys
from pathlib import Path

def check_title_page_formatting():
    """Verify title page has proper LaTeX formatting, not escaped markdown."""
    title_tex = Path('tex/frontmatter/title.tex').read_text()
    
    # Check for escaped markdown headers (regression indicator)
    if r'\#' in title_tex:
        return False, "Title page has escaped markdown headers (\\#)"
    
    # Check for titlepage environment (proper LaTeX formatting)
    if r'\begin{titlepage}' not in title_tex:
        return False, "Title page missing titlepage environment"
    
    if r'\end{titlepage}' not in title_tex:
        return False, "Title page missing closing titlepage environment"
    
    # Check for font sizing commands (should use \fontsize, not \Large, \large, etc.)
    if r'\fontsize{' not in title_tex:
        return False, "Title page missing \\fontsize commands for proper sizing"
    
    # Verify key title elements are present
    if 'Sources of Shang History' not in title_tex:
        return False, "Title page missing main title text"
    
    if 'Oracle-Bone Inscriptions' not in title_tex:
        return False, "Title page missing subtitle"
    
    if 'David N. Keightley' not in title_tex:
        return False, "Title page missing author name"
    
    # Check that it doesn't look like plain text (no leading \# or newlines at start)
    lines = title_tex.strip().split('\n')
    if lines[0].startswith('#'):
        return False, "Title page starts with markdown header"
    
    return True, "Title page formatting OK (titlepage env, fonts, all elements)"

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

def check_markdown_header_preservation():
    """Verify markdown headers are preserved, not escaped."""
    from pathlib import Path
    
    # Check that emit_structure.py actually preserves markdown headers
    # Look at a file that should have markdown headers
    test_files = list(Path('build/ocr/cleaned_with_notes').glob('p_0[0-2]*.md'))
    
    if not test_files:
        return True, "No markdown files to check"
    
    headers_found = 0
    for md_file in test_files[:5]:
        content = md_file.read_text()
        # Count markdown headers (# , ## , ### , etc.)
        header_count = len(re.findall(r'^#+\s+', content, re.MULTILINE))
        headers_found += header_count
    
    if headers_found == 0:
        return False, "No markdown headers found in source files"
    
    # Now check that they DON'T appear as escaped \# in TeX
    ch01_tex = Path('tex/chapters/ch01.tex').read_text()
    escaped_hashes = len(re.findall(r'^\s*\\\#\s+', ch01_tex, re.MULTILINE))
    
    if escaped_hashes > 2:  # Allow 1-2, but not many
        return False, f"Too many escaped markdown headers (\\#) in ch01.tex: {escaped_hashes}"
    
    return True, f"Markdown header preservation OK ({headers_found} headers in source)"

def check_title_page_skip_logic():
    """Verify emit_structure.py skips title page generation."""
    emit_script = Path('scripts/06_emit_structure.py').read_text()
    
    # Check that the skip logic is present
    if 'sec_id == "frontmatter/title"' not in emit_script:
        return False, "Missing title page skip logic in emit_structure.py"
    
    if 'continue' not in emit_script[emit_script.find('sec_id == "frontmatter/title"'):]:
        return False, "Title page skip logic incomplete (no continue statement)"
    
    return True, "Title page skip logic present"

def check_section_headers_not_escaped():
    """Verify section headers in body chapters are rendered, not escaped."""
    ch01_tex = Path('tex/chapters/ch01.tex').read_text()
    
    # Check for \section[ commands (properly rendered)
    section_cmds = len(re.findall(r'\\section\[', ch01_tex))
    
    if section_cmds == 0:
        return False, "No section commands found in ch01.tex"
    
    # Check for excessive escaped hashes that might indicate section number issues
    # A few escaped hashes might be OK (in footnotes, etc), but many would be bad
    escaped_hashes = len(re.findall(r'\\#', ch01_tex))
    
    if escaped_hashes > 10:
        return False, f"Too many escaped hashes in ch01.tex: {escaped_hashes}"
    
    return True, f"Section headers properly rendered ({section_cmds} sections, {escaped_hashes} escaped hashes)"

def main():
    """Run all regression checks."""
    checks = [
        ("Title Page Formatting", check_title_page_formatting),
        ("Title Page Skip Logic", check_title_page_skip_logic),
        ("Markdown Header Preservation", check_markdown_header_preservation),
        ("Section Headers Not Escaped", check_section_headers_not_escaped),
        ("Footnote Order", check_footnote_order),
        ("Section Numbers", check_section_numbers),
        ("Quotation Marks", check_quotation_marks),
        ("Frontmatter Cleanup", check_frontmatter_cleanup),
    ]
    
    print("Running regression checks...")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for name, check_fn in checks:
        try:
            ok, msg = check_fn()
            status = "✅ PASS" if ok else "❌ FAIL"
            print(f"{status} | {name:30} | {msg}")
            if ok:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ ERROR | {name:30} | {e}")
            failed += 1
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
