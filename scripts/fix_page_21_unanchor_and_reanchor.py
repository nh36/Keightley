#!/usr/bin/env python3
"""Fix page 21 by unanchoring FN 4 and 9, then re-anchoring at correct positions."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CWN_FILE = ROOT / "build" / "ocr" / "cleaned_with_notes" / "p_0021.md"

content = CWN_FILE.read_text()

print("=" * 70)
print("PAGE 21: Unanchor FN 4 and 9")
print("=" * 70)

# Step 1: Convert anchored FN 4 to unanchored
print("\nStep 1: Convert FN 4 from anchored to unanchored")
pattern_4 = r'<!-- FOOTNOTE:4 -->(.+?)<!-- /FOOTNOTE -->'
match_4 = re.search(pattern_4, content, re.DOTALL)
if match_4:
    body = match_4.group(1)
    # Replace with unanchored version
    unanchored_4 = f'<!-- FOOTNOTE-UNANCHORED:4 -->{body}<!-- /FOOTNOTE -->'
    content = content[:match_4.start()] + content[match_4.end():]
    content += f"\n{unanchored_4}\n"
    print("  ✓ FN 4 converted to unanchored")
else:
    print("  ✗ FN 4 not found")

# Step 2: Convert anchored FN 9 to unanchored
print("Step 2: Convert FN 9 from anchored to unanchored")
pattern_9 = r'<!-- FOOTNOTE:9 -->(.+?)<!-- /FOOTNOTE -->'
match_9 = re.search(pattern_9, content, re.DOTALL)
if match_9:
    body = match_9.group(1)
    # Replace with unanchored version
    unanchored_9 = f'<!-- FOOTNOTE-UNANCHORED:9 -->{body}<!-- /FOOTNOTE -->'
    content = content[:match_9.start()] + content[match_9.end():]
    content += f"\n{unanchored_9}\n"
    print("  ✓ FN 9 converted to unanchored")
else:
    print("  ✗ FN 9 not found")

# Step 3: Save and verify
CWN_FILE.write_text(content)
print("\n✓ Saved page 21 with FN 4 and 9 unanchored")

# Verify
print("\nVerification:")
markers = re.findall(r'<!-- FOOTNOTE:(\d+) -->', content)
print(f"  Anchored footnotes: {markers}")
unanchored = re.findall(r'<!-- FOOTNOTE-UNANCHORED:(\d+) -->', content)
print(f"  Unanchored footnotes: {unanchored}")
