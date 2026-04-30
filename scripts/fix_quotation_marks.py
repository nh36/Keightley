#!/usr/bin/env python3
"""
Convert straight double quotes to LaTeX-style quotes (`` for opening, '' for closing).

This script uses a simple heuristic:
- Quote after whitespace or at start of line -> opening quote (``)
- Quote before whitespace, punctuation, or end of line -> closing quote ('')
- Quote in the middle of a word -> leave as is (likely part of OCR artifact)
"""

import re
from pathlib import Path
from typing import Tuple

def convert_quotes_in_text(text: str) -> Tuple[str, int]:
    """Convert straight quotes to LaTeX-style quotes."""
    
    # Pattern: capture context around straight quotes
    # This matches a quote with characters before/after to determine if opening or closing
    
    modified = text
    count = 0
    
    # Process line by line to better understand context
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        # Skip lines that are markdown metadata or LaTeX commands
        if line.startswith('<!--') or line.startswith('\\'):
            result_lines.append(line)
            continue
        
        # Process quotes in this line
        new_line = line
        pos = 0
        
        while True:
            idx = new_line.find('"', pos)
            if idx == -1:
                break
            
            # Get context
            before = new_line[idx - 1] if idx > 0 else ' '
            after = new_line[idx + 1] if idx < len(new_line) - 1 else ' '
            
            # Determine if opening or closing quote
            # Opening: after whitespace, punctuation, or start of line
            # Closing: before whitespace, punctuation, or end of line
            
            is_opening = before in ' \t\n([{-–—' or idx == 0
            is_closing = after in ' \t\n.,;:!?)}\'"' or idx == len(new_line) - 1
            
            if is_opening and not is_closing:
                # Opening quote
                new_line = new_line[:idx] + '``' + new_line[idx+1:]
                pos = idx + 2
                count += 1
            elif is_closing and not is_opening:
                # Closing quote
                new_line = new_line[:idx] + "''" + new_line[idx+1:]
                pos = idx + 2
                count += 1
            elif is_opening and is_closing:
                # Could be either - use heuristic: if short distance to next quote, it's closing
                next_quote = new_line.find('"', idx + 1)
                if next_quote != -1 and next_quote - idx < 100:
                    # Pair of quotes close together - first is opening, will handle second
                    new_line = new_line[:idx] + '``' + new_line[idx+1:]
                    pos = idx + 2
                    count += 1
                else:
                    # Ambiguous - lean towards closing (more common at end of phrase)
                    new_line = new_line[:idx] + "''" + new_line[idx+1:]
                    pos = idx + 2
                    count += 1
            else:
                # Neither - possibly part of a word or OCR artifact
                pos = idx + 1
        
        result_lines.append(new_line)
    
    return '\n'.join(result_lines), count


def main():
    md_dir = Path('build/ocr/cleaned_with_notes')
    markdown_files = sorted(md_dir.glob('p_*.md'))
    
    total_converted = 0
    files_modified = 0
    
    print("Converting straight quotes to LaTeX-style quotes...\n")
    
    for md_file in markdown_files:
        content = md_file.read_text(encoding='utf-8')
        
        if '"' not in content:
            continue
        
        new_content, count = convert_quotes_in_text(content)
        
        if count > 0:
            md_file.write_text(new_content, encoding='utf-8')
            print(f"  {md_file.name}: {count} quotes converted")
            total_converted += count
            files_modified += 1
    
    print(f"\nTotal: {total_converted} quotes converted in {files_modified} files")
    print("\nNext step: Regenerate TeX files")


if __name__ == '__main__':
    main()
