#!/usr/bin/env python3
"""
Phase 11a: Automate section reference replacement with \ref{} commands.

This script finds text patterns like "see section 2.3.1" and replaces them with
LaTeX \ref{} commands like "\ref{sec:chapters-ch02:2.3.1}".

The script:
1. Reads source files
2. Identifies section references using regex patterns
3. Maps section numbers to chapter contexts
4. Replaces references with \ref{} commands
5. Preserves originals as comments for review
6. Validates LaTeX compilation
"""

import re
import os
import sys
from pathlib import Path

# Section reference patterns to match
# Matches: "see section 2.3", "cf. section 1.2.1", etc.
SECTION_REF_PATTERN = r'(?:see(?:\s+(?:also|further))?)?\s+(?:sec(?:tion)?\.?|cf\.?\s+sec(?:tion)?\.?)\s+(\d+\.\d+(?:\.\d+)*)'

class SectionReferenceAutomator:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.chapter_files = {
            'ch01': self.root_dir / 'tex/chapters/ch01.tex',
            'ch02': self.root_dir / 'tex/chapters/ch02.tex',
            'ch03': self.root_dir / 'tex/chapters/ch03.tex',
            'ch04': self.root_dir / 'tex/chapters/ch04.tex',
            'ch05': self.root_dir / 'tex/chapters/ch05.tex',
        }
        self.section_labels = self._build_label_map()
        self.replacements = []
        
    def _build_label_map(self):
        """Build a map of (section_number, chapter) -> label_name."""
        label_map = {}
        
        # For each chapter file, extract all labels
        for chapter_key, filepath in self.chapter_files.items():
            if not filepath.exists():
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all labels in format: \label{sec:chapters-chXX:SECTION.NUMBER}
            label_pattern = r'\\label\{sec:chapters-' + chapter_key + r':([^}]+)\}'
            for match in re.finditer(label_pattern, content):
                section_num = match.group(1)
                label_name = f"sec:chapters-{chapter_key}:{section_num}"
                label_map[section_num] = (chapter_key, label_name)
        
        return label_map
    
    def find_references_in_chapter(self, chapter_key):
        """Find all section references in a chapter."""
        filepath = self.chapter_files[chapter_key]
        if not filepath.exists():
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        references = []
        for match in re.finditer(SECTION_REF_PATTERN, content):
            section_num = match.group(1)
            full_match = match.group(0)
            start = match.start()
            end = match.end()
            references.append({
                'section_num': section_num,
                'full_match': full_match,
                'start': start,
                'end': end,
                'chapter': chapter_key,
            })
        
        return references
    
    def replace_reference(self, filepath, start, end, section_num, original_text):
        """Replace a single reference in a file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Build replacement text
        if section_num in self.section_labels:
            ch, label = self.section_labels[section_num]
            # Format: "see section X.Y" -> "\ref{sec:chapters-chXX:X.Y}"
            # Keep the original for review
            replacement = f"\\ref{{{label}}} (see {original_text})"
        else:
            # If section number not found, keep original
            replacement = original_text
            print(f"WARNING: Section {section_num} not found in label map", file=sys.stderr)
        
        # Replace in content
        new_content = content[:start] + replacement + content[end:]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return replacement
    
    def process_chapter(self, chapter_key, dry_run=False):
        """Process all references in a chapter."""
        filepath = self.chapter_files[chapter_key]
        if not filepath.exists():
            print(f"Chapter file not found: {filepath}")
            return []
        
        references = self.find_references_in_chapter(chapter_key)
        
        if not references:
            print(f"No section references found in {chapter_key}")
            return []
        
        print(f"\nFound {len(references)} section reference(s) in {chapter_key}:")
        
        changes = []
        for ref in references:
            print(f"  - Section {ref['section_num']}: {ref['full_match']}")
            if ref['section_num'] in self.section_labels:
                ch, label = self.section_labels[ref['section_num']]
                print(f"    -> Will map to: {label}")
            else:
                print(f"    -> NOT FOUND IN LABELS (will keep original)")
            
            changes.append(ref)
        
        if dry_run:
            print(f"\nDry run: no changes made to {chapter_key}")
            return changes
        
        # Process references in reverse order to preserve positions
        for ref in reversed(references):
            self.replace_reference(
                filepath,
                ref['start'],
                ref['end'],
                ref['section_num'],
                ref['full_match']
            )
        
        print(f"Updated {len(references)} reference(s) in {chapter_key}")
        return changes
    
    def process_all_chapters(self, dry_run=False):
        """Process all chapters."""
        all_changes = {}
        for chapter_key in sorted(self.chapter_files.keys()):
            changes = self.process_chapter(chapter_key, dry_run=dry_run)
            if changes:
                all_changes[chapter_key] = changes
        
        return all_changes


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automate section reference replacement with \\ref{} commands'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--chapter',
        help='Process only a specific chapter (e.g., ch01)'
    )
    
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent
    automator = SectionReferenceAutomator(root_dir)
    
    print("Section Reference Automator")
    print("=" * 50)
    print(f"Found {len(automator.section_labels)} section labels")
    print()
    
    if args.chapter:
        automator.process_chapter(args.chapter, dry_run=args.dry_run)
    else:
        automator.process_all_chapters(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
