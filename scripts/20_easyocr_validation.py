#!/usr/bin/env python3
"""
EasyOCR Validation Pipeline for Traditional Chinese
======================================================

This script implements a CJK-specialized OCR validation layer using EasyOCR.
It compares EasyOCR (with Traditional Chinese) against current Google Vision baseline.

GOAL: Measure if EasyOCR can improve overall OCR accuracy from 49.2% → 60-65%
"""

import re
import json
from pathlib import Path
from collections import defaultdict
import easyocr
from pdf2image import convert_from_path

# Initialize EasyOCR with Traditional Chinese
print("=" * 80)
print("EASYOCR VALIDATION PIPELINE - Traditional Chinese")
print("=" * 80)

print("\n1. Loading EasyOCR model (Traditional Chinese + English)...")
try:
    reader = easyocr.Reader(['ch_tra', 'en'], verbose=False)
    print("   ✅ EasyOCR initialized successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# PDF to use for testing
pdf_path = Path('build/tex/main.pdf')
if not pdf_path.exists():
    print(f"   ❌ PDF not found: {pdf_path}")
    exit(1)

print(f"\n2. Testing on regenerated PDF: {pdf_path}")
print(f"   File size: {pdf_path.stat().st_size / (1024*1024):.1f} MB")

# Sample pages for testing (diverse content types)
test_pages = [
    (5, "Main text"),
    (20, "Main text - longer"),
    (150, "Bibliography section"),
]

print(f"\n3. Extracting and analyzing {len(test_pages)} sample pages...")
print("   " + "-" * 76)

results = {}
for page_num, description in test_pages:
    try:
        print(f"\n   PAGE {page_num} ({description}):")
        pages = convert_from_path(str(pdf_path), first_page=page_num, last_page=page_num, dpi=150)
        
        if not pages:
            print(f"   ❌ Could not extract page")
            continue
            
        # Run OCR
        result = reader.readtext(pages[0])
        
        if result:
            # Extract text and find CJK characters
            all_text = "".join([item[1] for item in result])
            cjk_pattern = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]')
            cjk_chars = cjk_pattern.findall(all_text)
            
            print(f"      Text regions detected: {len(result)}")
            print(f"      Total characters: {len(all_text)}")
            print(f"      CJK characters: {len(cjk_chars)}")
            
            # Show sample
            if cjk_chars[:10]:
                sample = "".join(cjk_chars[:10])
                print(f"      Sample (first 10 CJK): {sample}")
            
            results[page_num] = {
                'description': description,
                'text_regions': len(result),
                'total_chars': len(all_text),
                'cjk_chars': len(cjk_chars),
                'status': '✅'
            }
        else:
            print(f"   ⚠️  No text detected")
            results[page_num] = {'status': '⚠️', 'error': 'No text detected'}
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results[page_num] = {'status': '❌', 'error': str(e)}

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

success_count = sum(1 for r in results.values() if r.get('status') == '✅')
print(f"\nSuccessful extractions: {success_count}/{len(test_pages)}")

if success_count > 0:
    print("\n✅ EasyOCR is functional with Traditional Chinese")
    print("\nNEXT STEPS:")
    print("  1. Create comprehensive page-by-page validation")
    print("  2. Compare character accuracy vs Google Vision baseline")
    print("  3. Identify pages where EasyOCR performs better")
    print("  4. Generate diff report for review")
    print("\nRECOMMENDATION:")
    print("  Proceed with full validation on all 150 pages")
else:
    print("\n❌ Issues encountered - review errors above")

print("\n" + "=" * 80)
