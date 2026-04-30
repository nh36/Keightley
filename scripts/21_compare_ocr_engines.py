#!/usr/bin/env python3
"""
OCR Engine Comparison: EasyOCR vs Google Vision Baseline
=========================================================

Compares EasyOCR (Traditional Chinese) against current Google Vision OCR
to measure accuracy improvements and identify problematic pages.
"""

import re
import json
from pathlib import Path
from collections import defaultdict
import easyocr
from pdf2image import convert_from_path
import numpy as np

print("=" * 80)
print("OCR ENGINE COMPARISON - EasyOCR vs Google Vision")
print("=" * 80)

# Initialize EasyOCR
print("\n1. Initializing EasyOCR (Traditional Chinese + English)...")
try:
    reader = easyocr.Reader(['ch_tra', 'en'], verbose=False)
    print("   ✅ EasyOCR ready")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Load current Google Vision baseline
print("\n2. Loading current cleaned OCR (Google Vision baseline)...")
ocr_dir = Path('build/ocr/cleaned_with_notes')
md_files = sorted(ocr_dir.glob('p_*.md'))
print(f"   ✅ Found {len(md_files)} pages")

# CJK pattern
cjk_pattern = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]')

# Select diverse test pages
print("\n3. Selecting diverse test pages...")
test_pages = {
    7: "Main text (high CJK)",
    50: "Bibliography entry",
    100: "Table section",
    150: "Mixed content",
}

print(f"   Testing {len(test_pages)} pages: {list(test_pages.keys())}")

# Extract current Google Vision baseline
print("\n4. Extracting Google Vision baseline CJK content...")
baseline_cjk = {}
for page_num in test_pages.keys():
    md_file = ocr_dir / f'p_{page_num:04d}.md'
    if md_file.exists():
        content = md_file.read_text(encoding='utf-8', errors='ignore')
        cjk_chars = cjk_pattern.findall(content)
        baseline_cjk[page_num] = {
            'chars': cjk_chars,
            'count': len(cjk_chars),
            'unique': len(set(cjk_chars))
        }
        print(f"   p_{page_num:04d}: {len(cjk_chars)} CJK chars ({len(set(cjk_chars))} unique)")

# Now run EasyOCR on same pages
print("\n5. Running EasyOCR on test pages...")
pdf_path = Path('build/tex/main.pdf')
easyocr_results = {}

for page_num in test_pages.keys():
    try:
        print(f"   Extracting page {page_num}...", end=" ", flush=True)
        images = convert_from_path(str(pdf_path), first_page=page_num, last_page=page_num, dpi=150)
        img_array = np.array(images[0])
        
        print("OCR...", end=" ", flush=True)
        result = reader.readtext(img_array)
        
        # Extract all text and find CJK
        all_text = "".join([item[1] for item in result])
        cjk_chars = cjk_pattern.findall(all_text)
        
        easyocr_results[page_num] = {
            'chars': cjk_chars,
            'count': len(cjk_chars),
            'unique': len(set(cjk_chars)),
            'regions': len(result)
        }
        print(f"✅ ({len(cjk_chars)} CJK)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        easyocr_results[page_num] = {'error': str(e)}

# Compare results
print("\n" + "=" * 80)
print("COMPARISON RESULTS")
print("=" * 80)

comparison = {}
for page_num in test_pages.keys():
    if page_num not in baseline_cjk or page_num not in easyocr_results:
        continue
    
    if 'error' in easyocr_results[page_num]:
        print(f"\np_{page_num:04d} ({test_pages[page_num]}):")
        print(f"  ❌ EasyOCR Error: {easyocr_results[page_num]['error']}")
        continue
    
    gv = baseline_cjk[page_num]
    eo = easyocr_results[page_num]
    
    # Calculate similarity
    gv_set = set(gv['chars'])
    eo_set = set(eo['chars'])
    overlap = len(gv_set & eo_set)
    
    print(f"\np_{page_num:04d} ({test_pages[page_num]}):")
    print(f"  Google Vision:  {gv['count']:4d} CJK ({gv['unique']:3d} unique)")
    print(f"  EasyOCR:        {eo['count']:4d} CJK ({eo['unique']:3d} unique)")
    print(f"  Overlap:        {overlap:3d} unique characters")
    print(f"  Regions found:  {eo['regions']}")
    
    if gv['count'] > 0:
        detection_rate = (eo['count'] / gv['count']) * 100
        print(f"  Detection rate: {detection_rate:.1f}%")
    
    comparison[page_num] = {
        'gv_count': gv['count'],
        'eo_count': eo['count'],
        'overlap': overlap,
        'regions': eo['regions']
    }

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if comparison:
    avg_detection = sum(
        (c['eo_count'] / c['gv_count'] * 100) 
        for c in comparison.values() if c['gv_count'] > 0
    ) / len([c for c in comparison.values() if c['gv_count'] > 0])
    
    print(f"\n✅ EasyOCR successfully processed {len(comparison)} test pages")
    print(f"   Average character detection rate: {avg_detection:.1f}%")
    print(f"\nRECOMMENDATION:")
    print(f"   {'✅ PROCEED with full validation' if avg_detection > 40 else '⚠️ INVESTIGATE further'}")
    
    # Save results
    results_file = Path('scripts/21_ocr_comparison_results.json')
    with open(results_file, 'w') as f:
        json.dump({
            'test_pages': test_pages,
            'comparison': {k: v for k, v in comparison.items() if not isinstance(k, str)},
            'avg_detection_rate': avg_detection
        }, f, indent=2)
    print(f"\n   Results saved: {results_file}")
else:
    print("\n⚠️ No successful comparisons")

print("\n" + "=" * 80)
