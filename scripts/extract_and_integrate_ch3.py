#!/usr/bin/env python3
"""
Extract all missing sections from Chapter 3 OCR files and integrate into ch03.tex.
Converts Markdown/HTML footnotes to LaTeX format and applies proper section formatting.
"""

import re
import os
from pathlib import Path

def convert_footnotes_to_latex(text):
    """Convert OCR footnote format to LaTeX \footnote{} format."""
    # Pattern: text<!-- FOOTNOTE:N -->content<!-- /FOOTNOTE -->
    pattern = r'<!-- ?FOOTNOTE:(\d+) ?-->(.+?)<!-- ?/FOOTNOTE ?-->'
    
    def replace_footnote(match):
        num = match.group(1)
        content = match.group(2).strip()
        return f'\\footnote{{{content}}}'
    
    result = re.sub(pattern, replace_footnote, text, flags=re.DOTALL)
    return result

def extract_section(filepath, start_marker, end_marker=None):
    """Extract content between start and optional end marker."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove HTML comments and metadata
    content = re.sub(r'<!-- .+? -->', '', content, flags=re.DOTALL)
    
    # Find section start
    start_idx = content.find(start_marker)
    if start_idx == -1:
        return None
    
    start_idx += len(start_marker)
    
    # Find section end
    if end_marker:
        end_idx = content.find(end_marker, start_idx)
        if end_idx == -1:
            end_idx = len(content)
    else:
        end_idx = len(content)
    
    section_content = content[start_idx:end_idx].strip()
    
    # Clean up
    section_content = re.sub(r'\n\s*\n\s*\n', '\n\n', section_content)  # Multiple blank lines
    section_content = section_content.rstrip()
    
    return section_content

def clean_ocr_text(text):
    """Clean OCR artifacts from text."""
    # Remove symbol-only lines
    text = re.sub(r'^\s*[☐□U■\[\]]+\s*$', '', text, flags=re.MULTILINE)
    
    # Fix common OCR joining issues
    text = text.replace('OverKaizuka', 'Over\n\nKaizuka')
    
    # Remove stray characters and incomplete lines at start/end
    text = re.sub(r'^[\d\s\[\]☐□]+', '', text)
    text = re.sub(r'[\d\s\[\]☐□]+$', '', text)
    
    return text.strip()

def build_section_latex(section_num, title, content, level='section'):
    """Build LaTeX section with proper formatting."""
    short_title = title[:30] if len(title) > 30 else title
    short_title = short_title.split('\n')[0]  # Take first line
    
    # Convert footnotes
    content = convert_footnotes_to_latex(content)
    
    # Clean OCR artifacts
    content = clean_ocr_text(content)
    
    if level == 'section':
        cmd = '\\section'
    elif level == 'subsection':
        cmd = '\\subsection'
    else:
        cmd = '\\subsubsection'
    
    label_key = f'sec:chapters-ch03:{section_num}'
    
    latex = f'''{cmd}[{short_title}]{{\\origsecnum{{{section_num}}}{title}}}
\\label{{{label_key}}}

{content}

'''
    return latex

# Main extraction mapping
SECTIONS_TO_EXTRACT = {
    '3.1': {
        'title': 'Introduction to the Scholarship',
        'file': 'p_0074.md',
        'start': '3.1\nIntroduction',
        'end': '3.2\nPublished Sources',
        'level': 'section',
        'note': 'Currently just plain text in ch03.tex'
    },
    '3.3': {
        'title': 'Reference Works',
        'file': 'p_0076.md',
        'start': '3.3\nReference Works',
        'end': '3.3.1\nDictionaries',
        'level': 'section',
    },
    '3.3.1': {
        'title': 'Dictionaries',
        'file': 'p_0076.md',
        'start': '3.3.1\nDictionaries',
        'end': '3.3.2\nConcordances',
        'level': 'subsection',
    },
    '3.3.2': {
        'title': 'Concordances and Compendiums',
        'file': 'p_0078.md',
        'start': '3.3.2',
        'end': None,
        'level': 'subsection',
    },
    '3.4': {
        'title': 'Unknown (Transcription)',
        'file': 'p_0080.md',
        'start': '3.4',
        'end': '3.5',
        'level': 'section',
        'note': 'Section title to be determined'
    },
    '3.6': {
        'title': 'How to Read the Graphs on a Bone or Shell Fragment',
        'file': 'p_0088.md',
        'start': '3.6\nHow to Read',
        'end': '3.6.1',
        'level': 'section',
    },
    '3.6.1': {
        'title': 'How to Identify the Fragment',
        'file': 'p_0088.md',
        'start': '3.6.1\nHow to Identify',
        'end': '3.7',
        'level': 'subsection',
    },
    '3.7.1': {
        'title': 'The Inscriptions',
        'file': 'p_0093.md',
        'start': '3.7.1',
        'end': '3.7.1.1',
        'level': 'subsection',
    },
    '3.7.1.1': {
        'title': 'Duplication and Abbreviation',
        'file': 'p_0093.md',
        'start': '3.7.1.1\nDuplication',
        'end': '3.7.2',
        'level': 'subsubsection',
    },
    '3.7.2': {
        'title': 'The Comparative Method',
        'file': 'p_0095.md',
        'start': '3.7.2',
        'end': '3.7.3',
        'level': 'subsection',
    },
    '3.7.3': {
        'title': 'The Hollows and Cracks',
        'file': 'p_0098.md',
        'start': '3.7.3',
        'end': '3.7.4',
        'level': 'subsection',
    },
    '3.7.4.1': {
        'title': 'The Front of the Plastron',
        'file': 'p_0100.md',
        'start': '3.7.4.1',
        'end': '3.7.4.2',
        'level': 'subsubsection',
    },
    '3.8': {
        'title': 'Conclusion',
        'file': 'p_0107.md',
        'start': '3.8',
        'end': None,
        'level': 'section',
    }
}

def main():
    ocr_dir = Path('/Users/nathanhill/Code/Keightley/build/ocr/cleaned_with_notes')
    output = []
    
    output.append('% Extracted and integrated missing sections from Chapter 3\n')
    output.append('% Auto-generated from OCR cleaned files\n')
    output.append('% Footnotes converted to LaTeX format\n\n')
    
    for section_num in sorted(SECTIONS_TO_EXTRACT.keys(), 
                             key=lambda x: [int(n) for n in x.split('.')]):
        section_info = SECTIONS_TO_EXTRACT[section_num]
        filepath = ocr_dir / section_info['file']
        
        if not filepath.exists():
            output.append(f'% ERROR: File not found: {filepath}\n')
            continue
        
        print(f"Extracting {section_num}: {section_info['title']} from {section_info['file']}")
        
        content = extract_section(filepath, section_info['start'], section_info.get('end'))
        
        if content is None:
            output.append(f'% WARNING: Section {section_num} not found in {section_info["file"]}\n')
            continue
        
        latex = build_section_latex(section_num, section_info['title'], content, 
                                   section_info['level'])
        output.append(latex)
    
    # Write output
    output_file = Path('/Users/nathanhill/Code/Keightley/extracted_ch3_complete.tex')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(output))
    
    print(f"\nExtracted sections written to: {output_file}")
    
    # Also show what needs to be integrated
    print("\n=== Integration Instructions ===")
    print("Add the extracted sections to ch03.tex before the 3.2 section.")
    print(f"Content is ready in: {output_file}")

if __name__ == '__main__':
    main()
