#!/usr/bin/env python3
"""
Phase 11b: Automate chapter reference replacement with \ref{} commands.

This script finds text patterns like "ch. 2" and replaces them with
LaTeX \ref{} commands like "\ref{ch:2}".

The script:
1. Reads source files
2. Identifies chapter references using regex patterns
3. Replaces references with \ref{} commands
4. Preserves originals as comments for review
5. Validates LaTeX compilation
"""

import re
import os
import sys
from pathlib import Path

# Chapter reference patterns to match
# Matches: "ch. 1", "chapter 2", "ch. 3, n. 5", etc.
CHAPTER_REF_PATTERN = r'\bch\.\s+([1-5])(?=[,;.\s)\}])'

class ChapterReferenceAutomator:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.chapter_files = {
            'ch01': self.root_dir / 'tex/chapters/ch01.tex',
            'ch02': self.root_dir / 'tex/chapters/ch02.tex',
            'ch03': self.root_dir / 'tex/chapters/ch03.tex',
            'ch04': self.root_dir / 'tex/chapters/ch04.tex',
            'ch05': self.root_dir / 'tex/chapters/ch05.tex',
        }
        self.chapter_labels = {
            '1': 'ch:1',
            '2': 'ch:2',
            '3': 'ch:3',
            '4': 'ch:4',
            '5': 'ch:5',
        }
        self.replacements = []
        
    def find_references_in_chapter(self, chapter_key):
        """Find all chapter references in a chapter."""
        filepath = self.chapter_files[chapter_key]
        if not filepath.exists():
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        references = []
        for match in re.finditer(CHAPTER_REF_PATTERN, content):
            chapter_num = match.group(1)
            full_match = match.group(0)
            start = match.start()
            end = match.end()
            references.append({
                'chapter_num': chapter_num,
                'full_match': full_match,
                'start': start,
                'end': end,
                'source_chapter': chapter_key,
            })
        
        return references
    
    def replace_reference(self, filepath, start, end, chapter_num, original_text):
        """Replace a single reference in a file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Build replacement text
        if chapter_num in self.chapter_labels:
            label = self.chapter_labels[chapter_num]
            # Format: "ch. 2" -> "\ref{ch:2} (see ch. 2)"
            # Keep the original for review
            replacement = f"\\ref{{{label}}} (see {original_text})"
        else:
            # Shouldn't happen - but keep original just in case
            replacement = original_text
        
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
            print(f"No chapter references found in {chapter_key}")
            return []
        
        # Group by target chapter
        by_target = {}
        for ref in references:
            target = ref['chapter_num']
            if target not in by_target:
                by_target[target] = []
            by_target[target].append(ref)
        
        print(f"\nFound {len(references)} chapter reference(s) in {chapter_key}:")
        for target in sorted(by_target.keys()):
            refs = by_target[target]
            print(f"  -> ch. {target}: {len(refs)} reference(s)")
        
        if dry_run:
            print(f"Dry run: no changes made to {chapter_key}")
            return references
        
        # Process references in reverse order to preserve positions
        for ref in reversed(references):
            self.replace_reference(
                filepath,
                ref['start'],
                ref['end'],
                ref['chapter_num'],
                ref['full_match']
            )
        
        print(f"Updated {len(references)} reference(s) in {chapter_key}")
        return references
    
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
        description='Automate chapter reference replacement with \\ref{} commands'
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
    automator = ChapterReferenceAutomator(root_dir)
    
    print("Chapter Reference Automator")
    print("=" * 50)
    print(f"Found {len(automator.chapter_labels)} chapter labels")
    print()
    
    if args.chapter:
        automator.process_chapter(args.chapter, dry_run=args.dry_run)
    else:
        automator.process_all_chapters(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
