#!/usr/bin/env python3
"""
Wade-Giles Audit Script

Systematically finds and catalogs Wade-Giles romanizations in the document.
Generates a TSV file for tracking conversions to pinyin.

The script identifies patterns like:
- Ch'en, Ch'ien, Tung, Hsü (names with apostrophes or aspirated initials)
- T'ang, T'ai (words with aspirated initials)
- Chou, Chu, Kung (dynasty/place names)
- Lung-shan, Shih-chi (hyphenated terms)

TSV columns:
- wade_giles: The original Wade-Giles term
- frequency: How many times it appears
- type: Inferred type (name, place, dynasty, term, etc.)
- first_context: Where it first appears (chapter, line excerpt)
- all_contexts: Sample of different contexts where it appears
- pinyin: (blank for now, filled in later)
- notes: Any special considerations
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

class WadeGilesAuditor:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.chapter_files = {
            'ch01': self.root_dir / 'tex/chapters/ch01.tex',
            'ch02': self.root_dir / 'tex/chapters/ch02.tex',
            'ch03': self.root_dir / 'tex/chapters/ch03.tex',
            'ch04': self.root_dir / 'tex/chapters/ch04.tex',
            'ch05': self.root_dir / 'tex/chapters/ch05.tex',
        }
        
        # Wade-Giles patterns to match
        # These patterns capture common Wade-Giles romanization characteristics
        self.patterns = [
            # Names/words with apostrophe (aspiration marker): Ch'en, T'ang, etc.
            r"\b([A-Z]h?'[a-z]+(?:-[a-z]+)?)\b",
            
            # Common initial consonant clusters: Tung, Hsü, Tao, etc.
            r"\b((?:Ch|Hs|Ch'|Sh|Chueh|Cheng|Chih|Chia|Chi|Chiu|Chou|Chu|Kung|Kuo)(?:[a-z]+-?[a-z]*)?)\b",
            
            # Words starting with aspirated T: Tang, Tao, etc.
            r"\b(T[a-z]+(?:-[a-z]+)?)\b",
            
            # Common place/dynasty names: Lung-shan, Shih-chi, etc.
            r"\b([A-Z][a-z]*(?:-[a-z]+)+)\b",
            
            # Two-character names common in Chinese: names like Chang, Liu, Li, Hu, etc.
            r"\b((?:Chang|Liu|Li|Hu|Tso|Ting|Chuang|Hsiung|Chi|Han|Yen|Ho|Pai|Chao|Cheng|Chou)(?:\s+[A-Z][a-z]+)?)\b",
        ]
        
        self.findings = defaultdict(lambda: {
            'frequency': 0,
            'contexts': [],
            'chapters': set(),
        })
    
    def infer_type(self, term):
        """Guess the type of Wade-Giles term."""
        # Check against known patterns
        if term in ['Shang', 'Chou', 'Han', 'Tang', "T'ang"]:
            return 'dynasty'
        elif term in ['Shih-chi', 'Lung-shan', "Ch'eng-tzu-yai", 'Fu-ho-kou-men']:
            return 'place/site'
        elif term[0].isupper() and len(term.split()) <= 2:
            return 'name'
        elif '-' in term:
            return 'hyphenated_term'
        else:
            return 'term'
    
    def extract_context(self, text, match_start, match_end, context_length=80):
        """Extract surrounding context around a match."""
        start = max(0, match_start - context_length)
        end = min(len(text), match_end + context_length)
        context = text[start:end].strip()
        # Remove newlines and excessive whitespace
        context = ' '.join(context.split())
        return context
    
    def audit_chapter(self, chapter_key):
        """Audit a single chapter for Wade-Giles terms."""
        filepath = self.chapter_files[chapter_key]
        if not filepath.exists():
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # More precise combined pattern
        # Apostrophe patterns: Ch'en, T'ang, etc.
        # Hyphenated patterns: Ping-pien, Lung-shan
        # Specific known names: Tung, Hsü, Chang, etc.
        combined_pattern = r"\b([A-Z][a-z]*'[a-z]+|[A-Z][a-z]+-[a-z]+(?:-[a-z]+)*|Tung|Hsü|Hu(?:\s+[A-Z][a-z]+)?|Hsin|Ting|Chia(?:ng)?|Ch'en|Ch'ien|Chou|Shang|Shih|Shima|Chin|Han|Li(?!\s+Chi)|Liu|Yen|Hsiung|Chih|Chu|Kung|Kuo|Chueh|Cheng|Fu-ho|Erh-li|Lung-shan|Shih-chi|Chang|Ping|Yi|Ch(?=i|u|o|a|e|')|Chuang|Tsao|Hsiang|Ming)\b"
        
        # Exclude common English words
        english_words = {'The', 'This', 'These', 'There', 'That', 'Their', 'They', 'Then', 'Than', 'Them', 'What', 'When', 'Where', 'Why', 'How', 'Who', 'Which', 'Were', 'Ting', 'He', 'She', 'His', 'Her', 'Him', 'Or', 'And', 'For', 'From', 'Has', 'Have', 'Had', 'Can', 'Did', 'Do', 'Does', 'Ch', 'A', 'An', 'Is', 'Are', 'Be', 'Was', 'By'}
        
        for match in re.finditer(combined_pattern, content):
            term = match.group(1).strip()
            
            # Skip English words
            if term in english_words:
                continue
            
            # Record this finding
            self.findings[term]['frequency'] += 1
            self.findings[term]['chapters'].add(chapter_key)
            
            # Store context (limit to first 5 unique contexts per term)
            if len(self.findings[term]['contexts']) < 5:
                context = self.extract_context(content, match.start(), match.end())
                self.findings[term]['contexts'].append({
                    'chapter': chapter_key,
                    'text': context
                })
    
    def audit_all_chapters(self):
        """Audit all chapters."""
        for chapter_key in sorted(self.chapter_files.keys()):
            print(f"Auditing {chapter_key}...", file=sys.stderr)
            self.audit_chapter(chapter_key)
    
    def write_tsv(self, output_path):
        """Write findings to TSV file."""
        output_path = Path(output_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write('\t'.join([
                'wade_giles',
                'frequency',
                'type',
                'chapters',
                'first_context',
                'pinyin',
                'notes'
            ]))
            f.write('\n')
            
            # Sort by frequency (descending)
            sorted_terms = sorted(
                self.findings.items(),
                key=lambda x: x[1]['frequency'],
                reverse=True
            )
            
            for term, data in sorted_terms:
                chapters = ', '.join(sorted(data['chapters']))
                
                # Get first context
                first_context = ''
                if data['contexts']:
                    first_context = data['contexts'][0]['text']
                    # Clean up for TSV
                    first_context = first_context.replace('\t', ' ').replace('\n', ' ')[:100]
                
                term_type = self.infer_type(term)
                
                # Write row
                f.write('\t'.join([
                    term,
                    str(data['frequency']),
                    term_type,
                    chapters,
                    first_context,
                    '',  # pinyin (empty for now)
                    ''   # notes (empty for now)
                ]))
                f.write('\n')
        
        print(f"✓ Wrote {len(sorted_terms)} unique Wade-Giles terms to {output_path}")
    
    def print_summary(self):
        """Print summary statistics."""
        total_unique = len(self.findings)
        total_occurrences = sum(d['frequency'] for d in self.findings.values())
        
        print("\n" + "="*60)
        print("Wade-Giles Audit Summary")
        print("="*60)
        print(f"Unique Wade-Giles terms found: {total_unique}")
        print(f"Total occurrences: {total_occurrences}")
        print(f"Average frequency per term: {total_occurrences / total_unique:.1f}")
        
        # Top 20 terms
        print("\nTop 20 Most Frequent Wade-Giles Terms:")
        print("-" * 60)
        sorted_terms = sorted(
            self.findings.items(),
            key=lambda x: x[1]['frequency'],
            reverse=True
        )[:20]
        
        for i, (term, data) in enumerate(sorted_terms, 1):
            term_type = self.infer_type(term)
            print(f"{i:2d}. {term:20s} ({data['frequency']:3d}x) - {term_type}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit Wade-Giles romanizations in document')
    parser.add_argument(
        '--output',
        default='data/wade_giles_audit.tsv',
        help='Output TSV file (default: data/wade_giles_audit.tsv)'
    )
    
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent
    auditor = WadeGilesAuditor(root_dir)
    
    print("Starting Wade-Giles Audit", file=sys.stderr)
    print("="*60, file=sys.stderr)
    
    auditor.audit_all_chapters()
    
    auditor.print_summary()
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    auditor.write_tsv(output_path)


if __name__ == '__main__':
    main()
