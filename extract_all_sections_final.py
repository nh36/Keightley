#!/usr/bin/env python3
import re
from pathlib import Path

ocr_dir = Path("/Users/nathanhill/Code/Keightley/build/ocr/cleaned_with_notes")

def read_file(page_num):
    file_path = ocr_dir / f"p_{page_num:04d}.md"
    if not file_path.exists():
        return None, None
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines, file_path

def extract_source_info(lines):
    """Extract scan page and printed page from first line"""
    if not lines:
        return None, None
    source_line = lines[0]
    match = re.search(r'source: scan p\. (\d+), printed p\. (\d+)', source_line)
    if match:
        return match.group(1), match.group(2)
    return None, None

def md_to_latex(text):
    """Convert markdown formatting to LaTeX"""
    # Convert ** to \textbf{}
    text = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', text)
    # Convert * (italic) to \emph{}
    text = re.sub(r'\*([^*]+)\*', r'\\emph{\1}', text)
    # Handle bullet lists (lines starting with -)
    text = re.sub(r'^- ', r'\\item ', text, flags=re.MULTILINE)
    return text

# Define sections based on manual review
sections_map = {
    "4.1.1": {
        "title": "Five Periods Introduction",
        "search_text": "Tung Tso-pin's",
        "pages": [109, 110],
        "start_marker": "4.2",
        "end_marker": "FOOTNOTE"
    },
    "4.3": {
        "title": "Physical Criteria Overview",
        "search_text": "Physical Criteria",
        "pages": [139],
    },
    "4.3.1": {
        "title": "Bone vs Shell",
        "search_text": "Bone or Shell",
        "pages": [140],
    },
    "4.3.1.1": {
        "title": "The Diviners",
        "search_text": "4.3.1.2",
        "pages": [117],
    },
    "4.3.1.9": {
        "title": "Topics and Idioms",
        "search_text": "Topics and Idioms",
        "pages": [139],
    },
    "4.3.2": {
        "title": "Initial Preparation",
        "search_text": "4.3.2.2",
        "pages": [140],
    },
    "4.3.2.1": {
        "title": "Bone Structure",
        "search_text": "4.3.2.1",
        "pages": [140],
    },
    "4.3.2.3": {
        "title": "Hollow Shapes",
        "search_text": "Hollow Shapes",
        "pages": [141],
    },
    "4.3.2.4": {
        "title": "Hollow Placement",
        "search_text": "Hollow Placement",
        "pages": [144],
    },
    "4.3.3": {
        "title": "Archaeological Criteria",
        "search_text": "Archaeological Criteria",
        "pages": [145],
    },
    "4.3.3.1": {
        "title": "Pit Provenance",
        "search_text": "Pit Provenance",
        "pages": [146],
    },
}

results = {}

for section_id, section_info in sections_map.items():
    print(f"\n{'='*70}")
    print(f"Extracting {section_id}: {section_info['title']}")
    print(f"{'='*70}")
    
    search_text = section_info['search_text']
    pages = section_info['pages']
    
    for page_num in pages:
        lines, file_path = read_file(page_num)
        if not lines:
            print(f"ERROR: Could not read p_{page_num:04d}.md")
            continue
        
        # Find the section
        for i, line in enumerate(lines):
            if search_text in line:
                print(f"Found in p_{page_num:04d}.md at line {i+1}")
                scan_p, printed_p = extract_source_info(lines)
                print(f"Source: scan p. {scan_p}, printed p. {printed_p}")
                results[section_id] = {
                    'page': page_num,
                    'line': i+1,
                    'scan_p': scan_p,
                    'printed_p': printed_p,
                    'content_start': i
                }
                break

print("\n" + "="*70)
print("EXTRACTION SUMMARY")
print("="*70)
for section_id in sections_map:
    if section_id in results:
        info = results[section_id]
        print(f"✓ {section_id}: p_{info['page']:04d}.md (scan {info['scan_p']}, printed {info['printed_p']})")
    else:
        print(f"✗ {section_id}: NOT FOUND")

