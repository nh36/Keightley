#!/usr/bin/env python3
"""
Phase 1: Improve CRITICAL pages (242, 224, 228)

Based on OCR analysis:
- Page 242 (TABLE): Use Google Vision, clean up CJK overlay comments
- Page 224 (FIGURES+CJK): Manual review needed, heavy OCR issues
- Page 228 (FIGURES): Use Google Vision, remove garbled decorative elements

This script:
1. Compares current cleaned markdown with Google Vision source
2. Identifies which version is better
3. Suggests/applies corrections
"""

import re
from pathlib import Path

def extract_google_vision_page(page_num):
    """Extract specific page from Google Vision source using form-feed."""
    source_txt = Path('source/Keightley_1978.txt')
    text = source_txt.read_text(errors='replace')
    pages = text.split('\f')
    return pages[page_num - 1] if page_num <= len(pages) else ""

def clean_cjk_overlay_comments(text):
    """Remove redundant CJK overlay comments that are just markers."""
    # Remove CJK markers that don't add information
    text = re.sub(r'\s*<!-- CJK -->', '', text)
    # But keep CHECK comments as they indicate actual issues
    return text

def improve_page_242():
    """TABLE page: Clean up CJK comments, verify structure."""
    md_file = Path('build/ocr/cleaned_with_notes/p_0242.md')
    content = md_file.read_text()
    
    # Count issues
    cjk_count = len(re.findall(r'<!-- CJK -->', content))
    check_count = len(re.findall(r'<!-- CHECK', content))
    
    print(f"Page 242 (TABLE)")
    print(f"  Current state: {cjk_count} CJK markers, {check_count} CHECK comments")
    print(f"  Action: Clean up redundant CJK markers")
    print(f"  → Keep structure as-is, remove purely decorative comments")
    
    # Apply cleanup
    cleaned = clean_cjk_overlay_comments(content)
    
    # Don't write yet - just show what would change
    saved_count = len(re.findall(r'<!-- CJK -->', content)) - len(re.findall(r'<!-- CJK -->', cleaned))
    print(f"  Would remove: {saved_count} CJK markers")
    
    return cleaned

def improve_page_224():
    """FIGURES+CJK: Heavy OCR issues, needs review."""
    md_file = Path('build/ocr/cleaned_with_notes/p_0224.md')
    content = md_file.read_text()
    
    cjk_count = len(re.findall(r'<!-- CJK -->', content))
    check_count = len(re.findall(r'<!-- CHECK', content))
    
    print(f"\nPage 224 (FIGURES+CJK)")
    print(f"  Current state: {cjk_count} CJK markers, {check_count} CHECK comments")
    print(f"  Issue: Challenging mixed CJK/figure content")
    print(f"  Action: MANUAL REVIEW REQUIRED")
    print(f"  → Consider extracting fresh from Google Vision")
    print(f"  → Validate Chinese character accuracy")
    
    # Get Google Vision version for comparison
    google_text = extract_google_vision_page(224)
    print(f"  → Google Vision has {len(google_text)} chars vs cleaned {len(content)} chars")

def improve_page_228():
    """FIGURES: Clean up garbled decorative elements, keep captions."""
    md_file = Path('build/ocr/cleaned_with_notes/p_0228.md')
    content = md_file.read_text()
    
    cjk_count = len(re.findall(r'<!-- CJK -->', content))
    check_count = len(re.findall(r'<!-- CHECK', content))
    
    print(f"\nPage 228 (FIGURES)")
    print(f"  Current state: {cjk_count} CJK markers, {check_count} CHECK comments")
    print(f"  Status: Figure captions well preserved")
    print(f"  Action: Remove garbled decorative elements, keep meaningful content")
    
    # Check for figure captions
    if 'Fig.' in content:
        fig_captions = len(re.findall(r'Fig\.\s+\d+', content))
        print(f"  → Found {fig_captions} figure captions (GOOD)")
    
    if 'Chui-hsin' in content or 'Chin-chang' in content:
        print(f"  → Chinese names/sources preserved (GOOD)")
    
    # Identify lines that are pure garble
    lines = content.split('\n')
    garble_lines = []
    for i, line in enumerate(lines):
        # Heuristic: lines with only special chars and CJK, no Latin words
        if len(line) > 10 and not re.search(r'[a-zA-Z]{3,}', line):
            if re.search(r'[^\w\s\-\.\,\;\:\(\)\[\]<!-->]', line):
                garble_lines.append(i)
    
    print(f"  → {len(garble_lines)} potentially garbled lines (can be removed)")

def main():
    print("OCR CRITICAL PAGE IMPROVEMENT ANALYSIS")
    print("=" * 70)
    
    improved_242 = improve_page_242()
    improve_page_224()
    improve_page_228()
    
    print("\n" + "=" * 70)
    print("Summary: 3 critical pages analyzed")
    print("  Page 242: Safe to clean up (CJK markers)")
    print("  Page 224: Needs manual review (heavy CJK issues)")
    print("  Page 228: Can be improved (remove garble, keep captions)")

if __name__ == '__main__':
    main()
