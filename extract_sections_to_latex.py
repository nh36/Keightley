#!/usr/bin/env python3
import re
from pathlib import Path

ocr_dir = Path("/Users/nathanhill/Code/Keightley/build/ocr/cleaned_with_notes")

# Section details with exact page ranges
sections = {
    "4.1.1": {
        "title": "Five Periods Introduction",
        "pages": [110],
        "start_line": 6,
        "end_line": 50
    },
    "4.3": {
        "title": "Physical Criteria Overview",
        "pages": [139],
        "start_line": 26,
        "end_line": 30
    },
    "4.3.1": {
        "title": "Bone vs Shell (intro section)",
        "pages": [140],
        "start_line": 6,
        "end_line": 18
    },
    "4.3.1.1": {
        "title": "The Diviners",
        "pages": [117],
        "start_line": 27,
        "end_line": 42
    },
    "4.3.1.9": {
        "title": "Topics and Idioms",
        "pages": [139],
        "start_line": 7,
        "end_line": 25
    },
    "4.3.2": {
        "title": "Initial Preparation",
        "pages": [140],
        "start_line": 19,
        "end_line": 35
    },
    "4.3.2.1": {
        "title": "Initial Preparation",
        "pages": [140],
        "start_line": 19,
        "end_line": 27
    },
    "4.3.2.3": {
        "title": "Hollow Shapes",
        "pages": [141],
        "start_line": 7,
        "end_line": 20
    },
    "4.3.2.4": {
        "title": "Hollow Placement",
        "pages": [144],
        "start_line": 8,
        "end_line": 12
    },
    "4.3.3": {
        "title": "Archaeological Criteria",
        "pages": [145],
        "start_line": 21,
        "end_line": 26
    },
    "4.3.3.1": {
        "title": "Pit Provenance",
        "pages": [146],
        "start_line": 9,
        "end_line": 26
    },
}

print("EXTRACTING CHAPTER 4 SECTIONS")
print("="*80)

for section_num, details in sections.items():
    print(f"\n{section_num}: {details['title']}")
    print("-" * 80)
    
    for page_num in details['pages']:
        file_path = ocr_dir / f"p_{page_num:04d}.md"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # Extract source info
                source_line = lines[0] if lines else ""
                source_match = re.search(r'source: scan p\. (\d+), printed p\. (\d+)', source_line)
                if source_match:
                    print(f"Source: scan p. {source_match.group(1)}, printed p. {source_match.group(2)}")
                
                # Extract section content
                start = details['start_line'] - 1  # Convert to 0-indexed
                end = details['end_line']
                
                if start < len(lines) and end <= len(lines):
                    section_content = ''.join(lines[start:end])
                    print("Content preview:")
                    print(section_content[:200])
                else:
                    print(f"ERROR: Invalid line range {start}-{end} for file with {len(lines)} lines")

