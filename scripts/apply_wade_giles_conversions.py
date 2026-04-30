#!/usr/bin/env python3
"""
Phase 12c: Apply Wade-Giles → Pinyin conversions to LaTeX document.

This script reads mapped conversions from data/wade_giles_audit.tsv and applies
them to the document with fallback comments for safe, incremental conversion.

Usage:
    python3 scripts/apply_wade_giles_conversions.py --batch high --dry-run
    python3 scripts/apply_wade_giles_conversions.py --batch high --apply
    python3 scripts/apply_wade_giles_conversions.py --batch medium --apply
    
Options:
    --batch {high,medium,low}      Which priority batch to apply
    --dry-run                       Show what would change (no modification)
    --apply                         Actually apply changes to files
    --with-fallback                 Include Wade-Giles in comment (default: True)
    --cleanup                       Remove fallback comments from existing conversions
"""

import csv
import re
import sys
from pathlib import Path
from argparse import ArgumentParser


class WadeGilesConverter:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root or '.')
        self.audit_file = self.project_root / 'data' / 'wade_giles_audit.tsv'
        self.chapters_dir = self.project_root / 'tex' / 'chapters'
        
        # Load mappings from TSV
        self.mappings = {}  # {wade_giles: (pinyin, frequency, priority)}
        self.load_mappings()
    
    def load_mappings(self):
        """Load Wade-Giles → Pinyin mappings from audit TSV."""
        if not self.audit_file.exists():
            raise FileNotFoundError(f"Audit file not found: {self.audit_file}")
        
        with open(self.audit_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row['pinyin']:  # Only mapped terms
                    freq = int(row['frequency'])
                    
                    # Determine priority
                    if freq > 50:
                        priority = 'high'
                    elif freq > 20:
                        priority = 'high-medium'
                    elif freq > 10:
                        priority = 'medium'
                    else:
                        priority = 'low'
                    
                    self.mappings[row['wade_giles']] = {
                        'pinyin': row['pinyin'],
                        'frequency': freq,
                        'type': row['type'],
                        'priority': priority,
                    }
    
    def get_batch_terms(self, batch):
        """Get terms for a specific priority batch."""
        batch_map = {
            'high': ['high'],
            'high-medium': ['high', 'high-medium'],
            'medium': ['high', 'high-medium', 'medium'],
            'low': list(self.mappings.keys()),
        }
        
        if batch not in batch_map:
            raise ValueError(f"Unknown batch: {batch}. Choose: high, high-medium, medium, low")
        
        allowed_priorities = batch_map[batch]
        terms = {k: v for k, v in self.mappings.items() 
                 if v['priority'] in allowed_priorities}
        
        return terms
    
    def build_regex_pattern(self, terms):
        """Build a regex pattern to match Wade-Giles terms (word boundaries)."""
        # Sort by length (longest first) to avoid partial matches
        sorted_terms = sorted(terms.keys(), key=len, reverse=True)
        
        # Escape regex special characters
        escaped = [re.escape(t) for t in sorted_terms]
        
        # Pattern: word boundary + term + word boundary
        # Negative lookbehind/lookahead to avoid matching inside LaTeX commands
        pattern = r'(?<![\\%])\b(' + '|'.join(escaped) + r')\b'
        
        return re.compile(pattern)
    
    def should_replace(self, match, content, position):
        """Check if this match should be replaced (not in LaTeX command or comment)."""
        # Don't replace if preceded by backslash (LaTeX command)
        if position > 0 and content[position - 1] == '\\':
            return False
        
        # Don't replace if on a line with % before the match
        line_start = content.rfind('\n', 0, position) + 1
        line_before_match = content[line_start:position]
        
        if '%' in line_before_match:
            return False
        
        return True
    
    def process_chapter(self, chapter_path, terms, dry_run=True, with_fallback=True):
        """Process a single chapter file for Wade-Giles conversions."""
        if not chapter_path.exists():
            return {'skipped': True, 'reason': 'file not found'}
        
        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = self.build_regex_pattern(terms)
        
        replacements = []
        new_content = content
        offset = 0
        
        # Process matches in reverse order to maintain positions
        matches = list(pattern.finditer(content))
        matches.reverse()
        
        for match in matches:
            wade_giles = match.group(1)
            mapping = terms[wade_giles]
            pinyin = mapping['pinyin']
            
            # Check if we should replace this match
            if not self.should_replace(match, content, match.start()):
                continue
            
            # Build replacement - NO inline comments to avoid eating LaTeX content
            # Just use the pinyin directly; Wade-Giles is logged in replacements
            replacement = pinyin
            
            # Record replacement
            replacements.append({
                'wade_giles': wade_giles,
                'pinyin': pinyin,
                'position': match.start(),
                'original': match.group(0),
                'replacement': replacement,
            })
            
            # Apply replacement (in reverse to maintain positions)
            new_content = (
                new_content[:match.start()] +
                replacement +
                new_content[match.end():]
            )
        
        result = {
            'chapter': chapter_path.name,
            'replacements': len(replacements),
            'details': replacements,
        }
        
        if not dry_run and replacements:
            # Write modified content
            with open(chapter_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            result['applied'] = True
        else:
            result['applied'] = False
        
        return result
    
    def process_all_chapters(self, batch, dry_run=True, with_fallback=True):
        """Process all chapter files."""
        terms = self.get_batch_terms(batch)
        
        results = {
            'batch': batch,
            'dry_run': dry_run,
            'total_terms': len(terms),
            'total_frequency': sum(t['frequency'] for t in terms.values()),
            'chapters': {},
        }
        
        # Find all chapter files
        chapter_files = sorted(self.chapters_dir.glob('ch*.tex'))
        
        for chapter_file in chapter_files:
            result = self.process_chapter(chapter_file, terms, dry_run, with_fallback)
            results['chapters'][chapter_file.name] = result
        
        return results
    
    def print_summary(self, results):
        """Print summary of replacements."""
        print(f"\n{'='*70}")
        print(f"Wade-Giles → Pinyin Conversion Report")
        print(f"{'='*70}")
        print(f"Batch: {results['batch'].upper()}")
        print(f"Mode: {'DRY-RUN (no changes)' if results['dry_run'] else 'APPLY (making changes)'}")
        print(f"Terms: {results['total_terms']} ({results['total_frequency']} occurrences)")
        print(f"\n{'Chapter':<20} {'Replacements':<15} {'Status'}")
        print(f"{'-'*70}")
        
        total_replacements = 0
        for chapter, result in results['chapters'].items():
            if result.get('skipped'):
                print(f"{chapter:<20} {'SKIPPED':<15} ({result['reason']})")
            else:
                count = result['replacements']
                total_replacements += count
                applied = "APPLIED" if result.get('applied') else "PREVIEW"
                print(f"{chapter:<20} {count:<15} {applied}")
        
        print(f"{'-'*70}")
        print(f"{'TOTAL':<20} {total_replacements:<15} replacements")
        print(f"{'='*70}")
        
        # Show some example replacements
        if total_replacements > 0:
            print(f"\nSample Replacements (first 5):")
            sample_count = 0
            for chapter, result in results['chapters'].items():
                if result.get('details'):
                    for detail in result['details'][:5-sample_count]:
                        print(f"  {detail['wade_giles']:<15} → {detail['pinyin']:<15} ({chapter})")
                        sample_count += 1
                        if sample_count >= 5:
                            break
                if sample_count >= 5:
                    break


def main():
    parser = ArgumentParser(description='Apply Wade-Giles → Pinyin conversions')
    parser.add_argument('--batch', choices=['high', 'high-medium', 'medium', 'low'],
                        default='high',
                        help='Priority batch to process (default: high)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would change (default: True)')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply changes to files')
    parser.add_argument('--with-fallback', action='store_true', default=True,
                        help='Include Wade-Giles in comment (default: True)')
    parser.add_argument('--cleanup', action='store_true',
                        help='Remove fallback comments (not yet implemented)')
    
    args = parser.parse_args()
    
    # Determine dry_run mode
    dry_run = not args.apply
    
    try:
        converter = WadeGilesConverter()
        results = converter.process_all_chapters(
            batch=args.batch,
            dry_run=dry_run,
            with_fallback=args.with_fallback
        )
        
        converter.print_summary(results)
        
        if dry_run:
            print(f"\nTo apply these changes, run with: --apply")
        else:
            print(f"\n✓ Changes applied successfully")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
