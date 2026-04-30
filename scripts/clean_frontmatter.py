#!/usr/bin/env python3
"""
Clean up front matter pages (pages with Roman numerals).

Issues to fix:
1. Remove page numbers (i, ii, iii, iv, v, vi, vii, viii, ix, x, xi, xii, xiii, xiv, xv, xvi, etc.)
2. Remove section headers appearing mid-page (PREFACE, INTRODUCTION, etc.)
3. Clean up extra whitespace
"""

import re
from pathlib import Path
from typing import Tuple

def clean_frontmatter_page(text: str) -> Tuple[str, dict]:
    """Clean front matter pages by removing page numbers and headers."""
    
    issues_fixed = {
        'page_numbers_removed': 0,
        'section_headers_cleaned': 0,
    }
    
    lines = text.split('\n')
    result_lines = []
    
    # Split into header and body
    header_lines = []
    body_start = 0
    
    # Keep metadata lines (<!-- ... -->)
    for i, line in enumerate(lines):
        if line.startswith('<!--'):
            header_lines.append(line)
        elif line.strip() == '':
            header_lines.append(line)
        else:
            body_start = i
            break
    
    # Process body lines
    for i in range(body_start, len(lines)):
        line = lines[i]
        
        # Skip pure page number lines (just Roman numerals, Arabic numbers, or symbols)
        if re.match(r'^[\s·•]*([ivx]+|[0-9]+)[\s·•]*$', line, re.IGNORECASE):
            issues_fixed['page_numbers_removed'] += 1
            continue
        
        # Remove page numbers at start of line (e.g., "· xiv" or "xv")
        # But be careful not to remove content that happens to start with those letters
        if re.match(r'^[\s·•]+(i{1,3}v|i{1,3}|v|x{1,3}|xv{0,1}|xiv|xii{0,1})[\s·•]*$', line, re.IGNORECASE):
            issues_fixed['page_numbers_removed'] += 1
            continue
        
        # Remove page numbers embedded at very start with content after
        # e.g., "xiv\na place..." becomes just "a place..."
        line_cleaned = re.sub(r'^[\s·•]+(i{1,3}v|i{1,3}|v|x{1,3}|xv{0,1}|xiv|xii{0,1})[\s]+', '', line, flags=re.IGNORECASE)
        if line_cleaned != line:
            issues_fixed['page_numbers_removed'] += 1
            line = line_cleaned
        
        # Remove all-caps section headers that appear mid-page (if they're short)
        # But not if they're part of normal text (very heuristic)
        if line.isupper() and 3 < len(line.strip()) < 50 and not any(char in line for char in '()[]0-9'):
            # Could be a header like "PREFACE", "INTRODUCTION", "ACKNOWLEDGMENTS"
            # Check if it's likely a section header (common ones)
            upper_line = line.strip()
            if upper_line in ['PREFACE', 'INTRODUCTION', 'ACKNOWLEDGMENTS', 'CONTENTS', 
                              'LIST OF FIGURES', 'LIST OF TABLES', 'ABBREVIATIONS', 
                              'POSTSCRIPT', 'APPENDIX']:
                issues_fixed['section_headers_cleaned'] += 1
                continue
        
        result_lines.append(line)
    
    # Reconstruct with header
    result_lines = header_lines + result_lines
    
    # Remove excessive blank lines (more than 2 in a row)
    cleaned = []
    blank_count = 0
    for line in result_lines:
        if line.strip() == '':
            blank_count += 1
            if blank_count <= 2:
                cleaned.append(line)
        else:
            blank_count = 0
            cleaned.append(line)
    
    return '\n'.join(cleaned), issues_fixed


def main():
    cleaned_dir = Path('build/ocr/cleaned_with_notes')
    
    # These are the front matter pages (Roman numerals)
    frontmatter_pages = [
        'p_0001.md', 'p_0002.md', 'p_0003.md', 'p_0004.md', 'p_0005.md',
        'p_0006.md', 'p_0007.md', 'p_0008.md', 'p_0009.md', 'p_0010.md',
        'p_0011.md', 'p_0012.md', 'p_0013.md', 'p_0014.md', 'p_0015.md',
        'p_0016.md', 'p_0017.md', 'p_0018.md', 'p_0019.md', 'p_0020.md',
    ]
    
    total_issues = {
        'page_numbers_removed': 0,
        'section_headers_cleaned': 0,
        'files_modified': 0,
    }
    
    print("Cleaning front matter pages...\n")
    
    for page_name in frontmatter_pages:
        md_file = cleaned_dir / page_name
        if not md_file.exists():
            continue
        
        content = md_file.read_text(encoding='utf-8')
        new_content, issues = clean_frontmatter_page(content)
        
        if new_content != content:
            md_file.write_text(new_content, encoding='utf-8')
            print(f"  {page_name}:")
            if issues['page_numbers_removed'] > 0:
                print(f"    - Removed {issues['page_numbers_removed']} page numbers")
            if issues['section_headers_cleaned'] > 0:
                print(f"    - Cleaned {issues['section_headers_cleaned']} section headers")
            
            total_issues['files_modified'] += 1
            for key, val in issues.items():
                total_issues[key] += val
    
    print(f"\nTotal changes:")
    print(f"  Page numbers removed: {total_issues['page_numbers_removed']}")
    print(f"  Section headers cleaned: {total_issues['section_headers_cleaned']}")
    print(f"  Files modified: {total_issues['files_modified']}")


if __name__ == '__main__':
    main()
