"""Regression tests for footnote marker ordering and placement."""
import sys
from pathlib import Path
import re


def _footnote_ordering_issues():
    issues = []

    for tex_file in sorted(Path('tex/chapters').glob('*.tex')):
        content = tex_file.read_text()
        footnotes = re.findall(r'\\footnote\[(\d+)\]', content)
        footnote_nums = [int(n) for n in footnotes]

        if not footnote_nums:
            continue

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

    return issues


def _orphaned_footnote_issues():
    issues = []

    for md_file in sorted(Path('build/ocr/cleaned_with_notes').glob('p_*.md')):
        content = md_file.read_text()

        for line_num, line in enumerate(content.split('\n'), 1):
            footnotes = re.findall(r'FOOTNOTE(?:-UNANCHORED)?:(\d+)', line)
            if len(footnotes) > 1:
                issues.append({
                    'file': md_file.name,
                    'line': line_num,
                    'count': len(footnotes),
                    'message': f'Found {len(footnotes)} footnote markers on single line'
                })

    return issues


def _footnotes_near_markers_issues():
    issues = []

    for md_file in sorted(Path('build/ocr/cleaned_with_notes').glob('p_*.md')):
        content = md_file.read_text()

        for m in re.finditer(r'<!--\s*FOOTNOTE:(\d+)\s*-->(.*?)<!--\s*/FOOTNOTE\s*-->', content, re.DOTALL):
            fn_num = int(m.group(1))
            fn_body = m.group(2).strip()[:50]

            pos = m.start()
            before_text = content[max(0, pos-100):pos]
            has_marker = bool(re.search(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]|\b' + str(fn_num) + r'\b', before_text))

            if not has_marker:
                issues.append({
                    'file': md_file.name,
                    'fn': fn_num,
                    'body_start': fn_body,
                    'message': f'Footnote {fn_num} appears without nearby marker'
                })

    return issues


def check_footnote_markers_in_order():
    """Check that footnote markers appear in strictly increasing order within each chapter."""
    issues = _footnote_ordering_issues()
    return not issues


def check_no_orphaned_footnotes():
    """Check that footnotes don't appear in arbitrary locations (e.g., multiple on same line)."""
    issues = _orphaned_footnote_issues()
    return not issues


def check_footnotes_near_markers():
    """Check that anchored footnotes are near expected in-text markers."""
    issues = _footnotes_near_markers_issues()
    return not issues


if __name__ == "__main__":
    all_pass = True
    all_pass = check_footnote_markers_in_order() and all_pass
    all_pass = check_no_orphaned_footnotes() and all_pass
    all_pass = check_footnotes_near_markers() and all_pass
    if all_pass:
        print("\n✓ All footnote regression tests passed")
    else:
        print("\n✗ Some regression tests failed")
        sys.exit(1)
