#!/usr/bin/env python3
"""
Audit section numbers in the book to find duplicates or malformed patterns.

Issue: Original section numbers from source text (like "3.2 3.3 Reference Works")
are appearing in markdown as literal text, and when converted to LaTeX, they show
up alongside auto-generated section numbers, creating duplicates.

Solution: Remove these original embedded numbers from the text.
"""

import re
from pathlib import Path
from collections import defaultdict

def audit_section_numbers():
    """Find all embedded section numbers."""
    cleaned_dir = Path('build/ocr/cleaned_with_notes')
    
    # Pattern: a line starting with a section number
    # These are the problematic embedded numbers
    section_pattern = re.compile(r'^(\d+(?:\.\d+)*)\s+(.+)$', re.MULTILINE)
    
    issues_by_file = defaultdict(list)
    
    for md_file in sorted(cleaned_dir.glob('*.md')):
        content = md_file.read_text()
        
        # Skip header metadata (first 5 lines)
        body = '\n'.join(content.split('\n')[4:])
        
        # Find lines that start with section numbers
        for match in section_pattern.finditer(body):
            num, title = match.groups()
            
            # Filter: only flag if it looks like a section number (not just any number)
            # Section numbers: 1, 1.1, 1.1.1, etc. with reasonable structure
            parts = num.split('.')
            if len(parts) <= 4 and all(p.isdigit() for p in parts):
                # Check if this line is followed by heading or normal text
                # If it's followed directly by another similar number, it's likely embedded
                
                # Look ahead to see what comes after
                match_end = match.end()
                next_text = body[match_end:match_end+100]
                
                # Check if title starts uppercase (section headers do)
                if title and title[0].isupper():
                    issues_by_file[md_file.name].append({
                        'number': num,
                        'title': title[:60],
                        'line': f"{num} {title[:40]}"
                    })
    
    return issues_by_file

def main():
    issues = audit_section_numbers()
    
    print("SECTION NUMBER AUDIT")
    print("=" * 80)
    print(f"Found embedded section numbers in {len(issues)} files\n")
    
    # Group by severity
    single_level = []  # 1, 2, 3...
    double_level = []  # 1.1, 2.3, 3.4...
    triple_level = []  # 1.1.1, 2.3.4...
    
    for filename in sorted(issues.keys()):
        items = issues[filename]
        print(f"\n{filename}:")
        
        for item in items[:10]:  # Show first 10
            num_parts = len(item['number'].split('.'))
            print(f"  {item['line']}")
            
            if num_parts == 1:
                single_level.append(filename)
            elif num_parts == 2:
                double_level.append(filename)
            else:
                triple_level.append(filename)
        
        if len(items) > 10:
            print(f"  ... and {len(items) - 10} more")
    
    print("\n" + "=" * 80)
    print(f"\nSUMMARY:")
    print(f"  Files with level 1 numbers (1, 2, 3...): {len(set(single_level))}")
    print(f"  Files with level 2 numbers (1.1, 2.3...): {len(set(double_level))}")
    print(f"  Files with level 3 numbers (1.1.1...): {len(set(triple_level))}")
    print(f"\nThese embedded numbers should be removed to avoid duplicate numbering.")

if __name__ == '__main__':
    main()
