#!/usr/bin/env python3
"""
Comprehensive check of footnote ordering across entire book.
Identifies pages with out-of-order or problematic footnotes.
"""

import re
from pathlib import Path
from collections import defaultdict

def check_markdown_pages():
    """Check all markdown pages for footnote ordering issues."""
    issues = []
    pages_dir = Path('build/ocr/cleaned_with_notes')
    
    for page_file in sorted(pages_dir.glob('p_*.md')):
        content = page_file.read_text()
        page_num = page_file.stem.replace('p_', '')
        
        # Get the current order of footnotes
        fn_order = [int(m) for m in re.findall(r'<!-- (?:FOOTNOTE|FOOTNOTE-UNANCHORED):(\d+) -->', content)]
        
        if not fn_order:
            continue
        
        expected_order = sorted(set(fn_order))
        
        # Check for issues
        if fn_order != expected_order:
            issues.append({
                'page': page_num,
                'type': 'markdown_out_of_order',
                'current': fn_order,
                'expected': expected_order,
            })
        
        # Check for unanchored footnotes (indicates unanchored markers)
        unanchored = re.findall(r'<!-- FOOTNOTE-UNANCHORED:(\d+) -->', content)
        if unanchored:
            issues.append({
                'page': page_num,
                'type': 'unanchored_found',
                'unanchored': [int(u) for u in unanchored],
            })
    
    return issues

def check_tex_chapters():
    """Check all TeX chapters for footnote ordering issues."""
    issues = []
    tex_dir = Path('tex/chapters')
    
    for tex_file in sorted(tex_dir.glob('ch*.tex')):
        content = tex_file.read_text()
        chapter = tex_file.stem
        
        # Extract footnote numbers in order of appearance
        fn_numbers = []
        for match in re.finditer(r'\\footnote\[(\d+)\]', content):
            fn_no = int(match.group(1))
            if fn_no not in fn_numbers:
                fn_numbers.append(fn_no)
        
        if not fn_numbers:
            continue
        
        # Check if sequential
        expected = sorted(fn_numbers)
        
        # Find out-of-order footnotes
        out_of_order = []
        for i in range(len(fn_numbers) - 1):
            if fn_numbers[i] > fn_numbers[i+1]:
                out_of_order.append((fn_numbers[i], fn_numbers[i+1]))
        
        if out_of_order:
            issues.append({
                'file': chapter,
                'type': 'tex_out_of_order',
                'current': fn_numbers,
                'expected': expected,
                'pairs': out_of_order,
            })
    
    return issues

def main():
    print("="*70)
    print("COMPREHENSIVE FOOTNOTE ORDERING CHECK")
    print("="*70)
    
    # Check markdown pages
    print("\n### MARKDOWN PAGES ###\n")
    md_issues = check_markdown_pages()
    
    out_of_order_pages = [i for i in md_issues if i['type'] == 'markdown_out_of_order']
    unanchored_pages = [i for i in md_issues if i['type'] == 'unanchored_found']
    
    if out_of_order_pages:
        print(f"⚠ {len(out_of_order_pages)} pages with out-of-order footnotes:\n")
        for issue in out_of_order_pages[:10]:  # Show first 10
            print(f"  Page {issue['page']}:")
            print(f"    Current:  {issue['current']}")
            print(f"    Expected: {issue['expected']}")
    else:
        print("✓ All markdown pages have footnotes in correct order")
    
    if unanchored_pages:
        print(f"\n⚠ {len(unanchored_pages)} pages with unanchored footnotes:")
        for issue in unanchored_pages[:5]:
            print(f"  Page {issue['page']}: {issue['unanchored']}")
    
    # Check TeX chapters
    print("\n### TEX CHAPTERS ###\n")
    tex_issues = check_tex_chapters()
    
    if tex_issues:
        print(f"⚠ {len(tex_issues)} chapters with out-of-order footnotes:\n")
        for issue in tex_issues:
            print(f"  {issue['file'].upper()}:")
            print(f"    Out-of-order pairs: {issue['pairs']}")
            print(f"    Full sequence: {issue['current']}")
    else:
        print("✓ All TeX chapters have footnotes in correct order")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Markdown pages with issues: {len(out_of_order_pages)}")
    print(f"Markdown pages with unanchored: {len(unanchored_pages)}")
    print(f"TeX chapters with issues: {len(tex_issues)}")
    print(f"Total issues: {len(md_issues) + len(tex_issues)}")
    
    if not (out_of_order_pages or tex_issues):
        print("\n✓ ✓ ✓ NO ORDERING ISSUES FOUND ✓ ✓ ✓")
    
    return len(out_of_order_pages) + len(tex_issues)

if __name__ == '__main__':
    exit(main())
