#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Target sections to find
sections_to_find = [
    "4.1.1",     # Five Periods Introduction
    "4.3",       # Physical Criteria Overview (just the intro)
    "4.3.1",     # Bone vs Shell (intro section)
    "4.3.1.1",   # Introduction/Physical Criteria
    "4.3.1.9",   # Prognostications by Period
    "4.3.2",     # Initial Preparation Changes
    "4.3.2.1",   # Bone Structure  
    "4.3.2.3",   # Hollow Shapes
    "4.3.2.4",   # Hollow Placement
    "4.3.3",     # Archaeological Criteria
    "4.3.3.1",   # Pit Provenance
]

ocr_dir = Path("/Users/nathanhill/Code/Keightley/build/ocr/cleaned_with_notes")

# Search for each section
results = {}

for section in sections_to_find:
    print(f"\n{'='*60}")
    print(f"Searching for section: {section}")
    print(f"{'='*60}")
    
    # Try different patterns
    patterns = [
        f"^{re.escape(section)}$",
        f"^## {re.escape(section)}",
        f"^### {re.escape(section)}",
        f"^{re.escape(section)}\\s",
    ]
    
    for md_file in sorted(ocr_dir.glob("p_*.md")):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                for pattern in patterns:
                    if re.search(pattern, line):
                        print(f"✓ Found in {md_file.name} at line {i+1}: {line[:80]}")
                        
                        # Extract surrounding context
                        start = max(0, i - 2)
                        end = min(len(lines), i + 30)
                        context = '\n'.join(lines[start:end])
                        results[section] = {
                            'file': md_file.name,
                            'line': i + 1,
                            'context': context
                        }
                        break

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
for section in sections_to_find:
    if section in results:
        print(f"✓ {section}: {results[section]['file']}")
    else:
        print(f"✗ {section}: NOT FOUND")

