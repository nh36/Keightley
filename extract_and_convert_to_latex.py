#!/usr/bin/env python3
import re
from pathlib import Path

ocr_dir = Path("/Users/nathanhill/Code/Keightley/build/ocr/cleaned_with_notes")
output_file = Path("/Users/nathanhill/Code/Keightley/EXTRACTED_LATEX_SECTIONS.md")

def read_page(page_num):
    file_path = ocr_dir / f"p_{page_num:04d}.md"
    if not file_path.exists():
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def get_source_info(lines):
    if not lines:
        return None, None
    match = re.search(r'source: scan p\. (\d+), printed p\. (\d+)', lines[0])
    if match:
        return match.group(1), match.group(2)
    return None, None

def extract_section(page_num, start_line, end_line, skip_header_lines=4):
    """Extract a section from a page"""
    lines = read_page(page_num)
    if not lines:
        return None, None, None
    
    scan_p, printed_p = get_source_info(lines)
    
    # Skip header comment lines
    content_lines = lines[skip_header_lines:]
    
    # Extract section content
    section_content = ''.join(content_lines)
    return section_content, scan_p, printed_p

def md_to_latex_simple(text):
    """Simple conversion of markdown to LaTeX"""
    # Preserve footnotes as-is
    # Convert strong to textbf
    text = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', text)
    return text

# Sections to extract
sections = [
    ("4.1.1", "Five Periods Introduction", 110, None),
    ("4.3", "Physical Criteria Overview", 139, None),
    ("4.3.1", "Bone vs Shell", 140, None),
    ("4.3.1.1", "The Diviners", 117, None),
    ("4.3.1.9", "Topics and Idioms", 139, None),
    ("4.3.2", "Initial Preparation", 140, None),
    ("4.3.3", "Archaeological Criteria", 145, None),
    ("4.3.3.1", "Pit Provenance", 146, None),
]

output = []
output.append("# EXTRACTED CHAPTER 4 SECTIONS\n")
output.append("Converted from OCR markdown files to LaTeX format\n")
output.append("=" * 80 + "\n\n")

for section_id, section_title, page_num, notes in sections:
    lines = read_page(page_num)
    if not lines:
        continue
    
    scan_p, printed_p = get_source_info(lines)
    
    output.append(f"\n{'='*80}\n")
    output.append(f"## Section: {section_id} {section_title}\n")
    output.append(f"Source file: p_{page_num:04d}.md\n")
    output.append(f"Source pages: scan {scan_p}, printed {printed_p}\n")
    output.append(f"{'='*80}\n\n")
    
    # Extract content (skip first 4 header lines)
    content = ''.join(lines[4:])
    output.append("### LaTeX Code:\n\n")
    output.append("```latex\n")
    output.append(f"% source: scan {scan_p}, printed {printed_p}\n")
    output.append(f"% Section {section_id}: {section_title}\n\n")
    output.append(content)
    output.append("```\n")

# Write output
with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(output)

print(f"Extraction complete! Output written to: {output_file}")
print(f"Total file size: {output_file.stat().st_size} bytes")

