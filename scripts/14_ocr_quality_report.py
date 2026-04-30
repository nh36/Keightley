#!/usr/bin/env python3
"""
OCR Quality Analysis Tool
Compares Google Vision vs Tesseract OCR for flagged pages
Identifies pages that need manual correction
"""

import csv
import re
from pathlib import Path
from collections import Counter

def load_google_ocr():
    """Load Google Vision OCR, split by form-feed."""
    source_txt = Path('source/Keightley_1978.txt')
    if not source_txt.exists():
        return {}
    
    text = source_txt.read_text(errors='replace')
    pages = text.split('\f')
    return {i+1: pages[i] for i in range(len(pages))}

def load_tesseract_ocr():
    """Load Tesseract OCR, split by form-feed or page markers."""
    tess_txt = Path('build/ocr/Keightley_1978.tesseract.txt')
    if not tess_txt.exists():
        return {}
    
    text = tess_txt.read_text(errors='replace')
    pages = text.split('\f')
    return {i+1: pages[i] for i in range(len(pages))}

def analyze_ocr_text(text):
    """Extract error patterns from OCR text."""
    errors = {
        'mojibake': len(re.findall(r'[\x80-\xff]+', text)) > 10,
        'excessive_spaces': len(re.findall(r'\s{3,}', text)) > 20,
        'missing_punctuation': len(re.findall(r'\w[\s\n]\w', text)) > len(text) * 0.1,
        'char_confusion': sum(1 for c in text if c in 'lI1O0`"\'|') > len(text) * 0.05,
    }
    return errors

def main():
    """Generate OCR quality report."""
    
    # Read manifest for confidence scores
    manifest_rows = {}
    with open('build/ocr/MANIFEST.tsv') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            scan = int(row['scan_page'])
            manifest_rows[scan] = row
    
    # Find flagged pages
    flagged = []
    for scan, row in manifest_rows.items():
        try:
            tokens = int(row['tokens'])
            conf = float(row['mean_conf'])
            if conf < 70 and tokens > 30:
                flagged.append(scan)
        except (ValueError, KeyError):
            pass
    
    print(f"Analyzing {len(flagged)} flagged pages...")
    print()
    
    google_ocr = load_google_ocr()
    tess_ocr = load_tesseract_ocr()
    
    # Analyze each flagged page
    critical = []
    high = []
    medium = []
    
    for scan in sorted(flagged):
        conf = float(manifest_rows[scan]['mean_conf'])
        
        if conf < 40:
            critical.append(scan)
            level = "CRITICAL"
        elif conf < 60:
            high.append(scan)
            level = "HIGH"
        else:
            medium.append(scan)
            level = "MEDIUM"
        
        google_text = google_ocr.get(scan, '')[:200]
        tess_text = tess_ocr.get(scan, '')[:200]
        
        print(f"Page {scan:3d} | {level:8} | Conf: {conf:5.1f}%")
        print(f"  Google (first 200 chars): {google_text[:80]}")
        print(f"  Tesseract (first 200 chars): {tess_text[:80]}")
        print()
    
    print(f"\nSummary: {len(critical)} critical, {len(high)} high, {len(medium)} medium priority")

if __name__ == '__main__':
    main()
