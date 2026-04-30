#!/usr/bin/env python3
import os
import re
from pathlib import Path

ocr_dir = Path("/Users/nathanhill/Code/Keightley/build/ocr/cleaned_with_notes")

# Based on content review, here are the sections and their approximate page locations:
sections_info = {
    "4.1.1": {"title": "Five Periods Introduction", "start_page": 110, "approx_lines": "6-50"},
    "4.3": {"title": "Physical Criteria Overview", "start_page": 139, "approx_lines": "26-30"},
    "4.3.1": {"title": "Bone vs Shell (intro)", "start_page": 140, "approx_lines": "6-18"},
    "4.3.1.1": {"title": "Introduction/Physical Criteria", "start_page": 117, "approx_lines": "27-43"},
    "4.3.1.9": {"title": "Prognostications by Period", "start_page": 139, "approx_lines": "7-25"},
    "4.3.2": {"title": "Initial Preparation Changes", "start_page": 140, "approx_lines": "19-32"},
    "4.3.2.1": {"title": "Bone Structure", "start_page": 140, "approx_lines": "6-18"},
    "4.3.2.3": {"title": "Hollow Shapes", "start_page": 140, "approx_lines": "33-44"},
    "4.3.2.4": {"title": "Hollow Placement", "start_page": 144, "approx_lines": "8-14"},
    "4.3.3": {"title": "Archaeological Criteria", "start_page": 145, "approx_lines": "21-25"},
    "4.3.3.1": {"title": "Pit Provenance", "start_page": 146, "approx_lines": "9-26"},
}

print("CHAPTER 4 SECTION LOCATIONS")
print("="*70)
for section, info in sections_info.items():
    print(f"\n{section}: {info['title']}")
    print(f"  Approx location: p_{info['start_page']:04d}.md")
    file_path = ocr_dir / f"p_{info['start_page']:04d}.md"
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"  File exists: YES ({len(lines)} lines)")
            # Show first and source info
            source_line = lines[0].strip() if lines else ""
            print(f"  Source: {source_line[:70]}")
    else:
        print(f"  File exists: NO")

