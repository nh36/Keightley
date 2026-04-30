#!/usr/bin/env python3
"""
Extract and convert OCR sections to LaTeX format for Chapter 2.
"""

import re
from pathlib import Path


def clean_text(text):
    """Remove HTML comments and OCR markers."""
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Remove "CHECK OCR:" lines
    text = re.sub(r'CHECK OCR:.*\n', '', text)
    # Remove OCR checkbox markers
    text = re.sub(r'[☐☑]', '', text)
    # Clean up extra whitespace (but preserve newlines)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\n\n+', '\n\n', text)
    return text.strip()


def markdown_to_latex(text):
    """Convert Markdown formatting to LaTeX."""
    # Replace **bold** with \textbf{} (avoid in footnotes)
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    # Replace *italic* with \emph{} but be careful with emphasis
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'\\emph{\1}', text)
    return text


def extract_section_2_1(ocr_dir):
    """Extract Section 2.1 from p_0045.md (lines 8-17)."""
    file_path = Path(ocr_dir) / 'p_0045.md'
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Lines 8-17 (0-indexed: 7-16)
    content = ''.join(lines[7:17])
    content = clean_text(content)
    content = markdown_to_latex(content)
    
    latex = r"""\section{\origsecnum{2.1}Introduction to the Divination Record}
\label{sec:chapters-ch02:2.1}

"""
    latex += content + '\n\n'
    return latex


def extract_section_2_2_1(ocr_dir):
    """Extract Section 2.2.1 from p_0048.md (from line 7 until '2.2.1.1')."""
    file_path = Path(ocr_dir) / 'p_0048.md'
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the start (line 7, 0-indexed: 6) and end (before '2.2.1.1')
    content_lines = []
    for i in range(6, len(lines)):
        if re.match(r'^\s*2\.2\.1\.1\s*', lines[i]):
            break
        content_lines.append(lines[i])
    
    content = ''.join(content_lines)
    content = clean_text(content)
    content = markdown_to_latex(content)
    
    latex = r"""\subsection{\origsecnum{2.2.1}The Diviners}
\label{sec:chapters-ch02:2.2.1}

"""
    latex += content + '\n\n'
    return latex


def extract_section_2_3(ocr_dir):
    """Extract Section 2.3 from p_0050.md (lines 6-15, before 2.3.1)."""
    file_path = Path(ocr_dir) / 'p_0050.md'
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Lines 6-15 (0-indexed: 5-14) but stop at 2.3.1
    content_lines = []
    for i in range(5, min(16, len(lines))):
        if re.match(r'^\s*2\.3\.1\s*', lines[i]):
            break
        content_lines.append(lines[i])
    
    content = ''.join(content_lines)
    content = clean_text(content)
    content = markdown_to_latex(content)
    
    latex = r"""\section{\origsecnum{2.3}The Charge}
\label{sec:chapters-ch02:2.3}

"""
    latex += content + '\n\n'
    return latex


def extract_sections_2_6_to_2_9(ocr_dir):
    """Extract sections 2.6-2.9 from pages p_0057.md through p_0066.md."""
    ocr_dir = Path(ocr_dir)
    sections = {}
    
    # Map of section numbers to page ranges and titles
    # Based on the running-head comments in each page
    section_pages = {
        '2.6': (['p_0057.md'], 'Crack Notations'),
        '2.7': (['p_0058.md'], 'The Prognostication'),
        '2.8': (['p_0059.md', 'p_0060.md', 'p_0061.md'], 'The Verification'),
        '2.9': (['p_0062.md', 'p_0063.md', 'p_0064.md', 'p_0065.md', 'p_0066.md'], 'Recording the Inscriptions'),
    }
    
    for sec_num, (filenames, title) in section_pages.items():
        content_lines = []
        
        for filename in filenames:
            file_path = ocr_dir / filename
            if not file_path.exists():
                print(f"Warning: {filename} not found for section {sec_num}")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Skip the header/metadata lines (first 6 lines typically contain comments and blank lines)
            start_idx = 0
            for i, line in enumerate(lines):
                if not line.strip().startswith('<!--') and line.strip() and not line.strip().startswith('<!-- '):
                    start_idx = i
                    break
            
            # Collect all content lines from this file
            for i in range(start_idx, len(lines)):
                line = lines[i]
                
                # Stop if we hit subsection like 2.6.1, 2.7.1, etc. (but allow within 2.9.x)
                if sec_num != '2.9' and re.match(rf'^\s*{re.escape(sec_num)}\.\d+\s*', line):
                    # For non-2.9 sections, stop before subsections
                    break
                # For section 2.9, stop before subsections other than the current section
                elif sec_num == '2.9' and re.match(r'^\s*3\.\d+', line):
                    # Stop if we hit section 3.x
                    break
                
                content_lines.append(line)
        
        if not content_lines:
            print(f"Warning: No content found for section {sec_num}")
            continue
        
        content = ''.join(content_lines)
        content = clean_text(content)
        content = markdown_to_latex(content)
        
        latex = rf"""\section{{\origsecnum{{{sec_num}}}{{{title}}}}}
\label{{sec:chapters-ch02:{sec_num}}}

"""
        latex += content + '\n\n'
        sections[sec_num] = latex
    
    return sections


def main():
    ocr_dir = '/Users/nathanhill/Code/Keightley/build/ocr/cleaned_with_notes'
    output_file = '/Users/nathanhill/Code/Keightley/extracted_sections.tex'
    
    # Extract all sections
    all_latex = []
    
    print("Extracting Section 2.1...")
    all_latex.append(extract_section_2_1(ocr_dir))
    
    print("Extracting Section 2.2.1...")
    all_latex.append(extract_section_2_2_1(ocr_dir))
    
    print("Extracting Section 2.3...")
    all_latex.append(extract_section_2_3(ocr_dir))
    
    print("Extracting Sections 2.6-2.9...")
    sections_2_6_9 = extract_sections_2_6_to_2_9(ocr_dir)
    for sec_num in sorted(sections_2_6_9.keys(), key=lambda x: float(x)):
        all_latex.append(sections_2_6_9[sec_num])
    
    # Write output
    output_content = ''.join(all_latex)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"\nExtracted sections written to: {output_file}")
    print(f"Total sections extracted: {len(all_latex)}")


if __name__ == '__main__':
    main()
