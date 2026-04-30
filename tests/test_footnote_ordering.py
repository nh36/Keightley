"""Regression tests for footnote marker ordering and placement."""
import sys
from pathlib import Path
import re

def test_footnote_markers_in_order():
    """Test that footnote markers appear in strictly increasing order within each chapter."""
    issues = []
    
    for tex_file in sorted(Path('tex/chapters').glob('*.tex')):
        # Extract footnote numbers in order of appearance
        content = tex_file.read_text()
        footnotes = re.findall(r'\\footnote\[(\d+)\]', content)
        footnote_nums = [int(n) for n in footnotes]
        
        if not footnote_nums:
            continue
        
        # Check if they're in order
        prev_num = 0
        for i, fn in enumerate(footnote_nums):
            if fn <= prev_num:
                issues.append({
                    'file': tex_file.name,
                    'position': i,
                    'prev': prev_num,
                    'current': fn,
                    'message': f'Footnote {fn} appears after {prev_num} (out of order)'
                })
            prev_num = fn
    
    if issues:
        print("✗ Footnote ordering issues found:")
        for issue in issues[:5]:
            print(f"  {issue['file']}: {issue['message']}")
        return False
    else:
        print("✓ All footnote markers appear in order")
        return True


def test_no_orphaned_footnotes():
    """Test that footnotes don't appear in arbitrary locations (e.g., multiple on same line)."""
    issues = []
    
    for md_file in sorted(Path('build/ocr/cleaned_with_notes').glob('p_*.md')):
        content = md_file.read_text()
        
        # Look for multiple footnotes on the same line
        for line_num, line in enumerate(content.split('\n'), 1):
            footnotes = re.findall(r'FOOTNOTE(?:-UNANCHORED)?:(\d+)', line)
            if len(footnotes) > 1:
                issues.append({
                    'file': md_file.name,
                    'line': line_num,
                    'count': len(footnotes),
                    'message': f'Found {len(footnotes)} footnote markers on single line'
                })
    
    if issues:
        print("✗ Multiple footnotes on single line:")
        for issue in issues[:5]:
            print(f"  {issue['file']} line {issue['line']}: {issue['message']}")
        return False
    else:
        print("✓ No orphaned footnote markers")
        return True


def test_footnotes_near_markers():
    """Test that anchored footnotes are near expected in-text markers."""
    issues = []
    
    for md_file in sorted(Path('build/ocr/cleaned_with_notes').glob('p_*.md')):
        content = md_file.read_text()
        
        # Find all footnotes and check if they're anchored near actual markers
        for m in re.finditer(r'<!--\s*FOOTNOTE:(\d+)\s*-->(.*?)<!--\s*/FOOTNOTE\s*-->', content, re.DOTALL):
            fn_num = int(m.group(1))
            fn_body = m.group(2).strip()[:50]
            
            # Check if there's a reasonable marker nearby (within 50 chars before the footnote)
            pos = m.start()
            before_text = content[max(0, pos-100):pos]
            
            # Look for superscript markers or digit markers
            has_marker = bool(re.search(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]|\b' + str(fn_num) + r'\b', before_text))
            
            if not has_marker:
                # This footnote might be arbitrarily placed
                issues.append({
                    'file': md_file.name,
                    'fn': fn_num,
                    'body_start': fn_body,
                    'message': f'Footnote {fn_num} appears without nearby marker'
                })
    
    if issues:
        print(f"⚠ Found {len(issues)} potentially misplaced footnotes:")
        for issue in issues[:10]:
            print(f"  {issue['file']} FN {issue['fn']}: {issue['message']}")
        return False
    else:
        print("✓ All footnotes appear near expected markers")
        return True


if __name__ == "__main__":
    all_pass = True
    all_pass = test_footnote_markers_in_order() and all_pass
    all_pass = test_no_orphaned_footnotes() and all_pass
    all_pass = test_footnotes_near_markers() and all_pass
    
    if all_pass:
        print("\n✓ All footnote regression tests passed")
        sys.exit(0)
    else:
        print("\n✗ Some regression tests failed")
        sys.exit(1)
