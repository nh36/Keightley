# Figures, Tables, and Oracle Inscription Handling Audit

## Current State

### What's Missing

**The plates/figures.tex is a STUB** - it's been marked for "Phase 7 (figures pipeline)" but never implemented.

The original 1978 PDF contains:
- 30 photographed figures (rubbings of oracle bones, technical diagrams, etc.)
- 33 tables with comparison data and measurements
- All embedded as scanned images in the original PDF

Our current output:
- ❌ NO actual figure images in the PDF
- ❌ NO table images/formatting
- ✓ Figure captions preserved as text (e.g., "Fig. 25. Rules of thumb for dating (S289.4)")
- ✓ Oracle inscription references preserved (e.g., "Ping-pien 235")

### What This Means

**For Oracle Bone Studies, This is a Problem**

The book isn't primarily a text reference—it's a visual reference to actual oracle bone artifacts:
- Figure captions reference specific rubbings (Ping-pien 235, Yi-pien 1410, etc.)
- Tables show comparative data with visual references
- Technical diagrams explain scapula/plastron anatomy
- Scholars need to see the actual rubbings to verify transcriptions

Without the figures:
- ❌ Cannot verify oracle bone transcriptions against rubbings
- ❌ Cannot see technical diagrams showing placement/structure
- ❌ Cannot compare Period I vs II vs III examples visually
- ✓ But: Text descriptions and archive references (S numbers) are intact

### Current Handling Approach

**Markdown layer** (build/ocr/cleaned_with_notes/p_*.md):
- Pages 200-229 are figure pages
- p_0200 has just "Figures" + garbled header marks
- p_0224 (oracle bones) was heavily cleaned by Opus agent, kept captions
- P_0226, P_0227, P_0228 similar - captions extracted, images lost
- Pages 230-326 are main bibliography, lost figure references

**LaTeX layer** (tex/plates/):
- `figures.tex` is a STUB (placeholder with comments, no content)
- `tables.tex` contains table content (extracted as text from markdown)
- No `\includegraphics{}` commands - no image inclusion at all

**Result**: Output PDF has text-only versions of what was originally a heavily illustrated book

---

## The Three Categories of Content We're Losing

### 1. Oracle Bone Rubbings (Highest Priority)

**Original**: Photographed rubbings showing actual inscriptions
**Current**: Caption text like "Ping-pien 235" with archive reference

**Examples**:
- Fig. 8: Typical period I display inscription
- Fig. 14: Complete inscription unit and complementary charges  
- Figs. 15-21: Various period examples with crack notations

**Impact**: Scholars cannot verify transcriptions against visual evidence

### 2. Technical Diagrams (Medium Priority)

**Original**: Line drawings showing scapula/plastron anatomy
**Current**: Captions like "Technical nomenclature of the bovid scapula"

**Examples**:
- Fig. 1: Bovid scapula nomenclature (with labeled parts)
- Fig. 3: Turtle plastron nomenclature
- Fig. 6: Hollow arrangement diagrams

**Impact**: Cannot understand spatial layout of inscriptions

### 3. Comparison Tables (Medium Priority)

**Original**: Multi-page tables with visual data
**Current**: Text table extraction (might work if markdown captured it)

**Examples**:
- Table 3: Plastron measurements and comparison
- Table 7: Charge and divination correlation
- Appendices with detailed listings

**Impact**: Measurements and visual comparisons are harder to parse

---

## What Would Be Needed to Fix This

### Option A: Extract Figures from Original PDF
```
1. Extract image stream from original PDF (each page is embedded image)
2. Split page images into individual figure regions
3. Save as separate image files (PNG/PDF)
4. Embed in LaTeX with \includegraphics{}
5. Time: 2-4 days, requires manual region identification
```

### Option B: Use Original PDF as Reference Layer
```
1. Keep our text-based PDF for searchability
2. Create side-by-side reader with original PDF linked
3. Cross-reference by page number
4. Time: 1 day, but requires different workflow
```

### Option C: Accept Text-Only Version
```
1. Document that figures are "referenced but not reproduced"
2. Provide archive reference codes (S289.4, Ping-pien 235, etc.)
3. Users can look up rubbings in original or archive
4. Time: None (current state)
5. Trade-off: Reduces utility for verification work
```

---

## Oracle Bone Inscription Handling

### Current Approach: Archive Reference Numbers

Our cleaned markdown preserves archive references:
- **S number**: Shima Kunio's canonical indexing (e.g., S289.4)
- **Collection identifier**: Ping-pien, Yi-pien, Chui-hsin, etc.
- **Drawing reference**: D suffix indicates drawing vs rubbing

**Example from p_0224**:
```
Fig. 25. Rules of thumb for dating (S289.4).
Fig. 26. Period III writing style (Chia-t'u 42).
```

These references are:
- ✓ Correct and preserved
- ✓ Sufficient for scholars who have access to original sources
- ✓ Maintained in all cleaned markdown
- ✗ But useless without ability to see the actual rubbings

### Transcriptions

**Current state**: Not in the plates section, but scattered through chapters

In chapters 1-5, oracle inscriptions are discussed with:
- ✓ Transcriptions in Wade-Giles romanization
- ✓ English translations and interpretations
- ✓ References to specific rubbings (e.g., "Ping-pien 8.2")
- ✓ Footnotes with scholarly debate

Example from ch01.tex:
```
"Ping-pien 10; 12.1-2, 5-6; 14.1-2; 16.1-2 (fig. 15)..."
```

This works reasonably well because:
- Scholars interested in specific inscriptions can look them up
- References are precise and unambiguous
- But: Cannot verify transcription accuracy without seeing rubbing

---

## Recommendation

### What to Do About Figures

**SHORT TERM** (Current approach - acceptable for now):
- Keep text-only output
- Ensure all archive references (S numbers, Ping-pien, etc.) are preserved
- Document in PDF metadata: "Figures referenced by archive code; see original PDF for images"
- This is suitable for: Text search, bibliographic reference, scholarly discussion
- This is NOT suitable for: Verification of oracle bone transcriptions

**MEDIUM TERM** (If this becomes a primary distribution format):
- Extract figures from original PDF as separate image files
- Embed in LaTeX with caption references
- Effort: 2-4 days of manual work
- Would produce a complete visual reference work

**LONG TERM** (For scholarly edition):
- Create dual-layer system: searchable text + facsimile images
- Use PDF layers or dual PDFs
- Provide interactive alignment of transcription to rubbing
- Effort: 1-2 weeks, but creates research tool

---

## Impact Assessment

### For Different User Types

**Casual reader**: ✓ Current text-only works fine
**Bibliographer**: ✓ Archive references sufficient
**Oracle bone specialist**: ✗ NEEDS figures for verification
**Historian**: ~ Text works, but misses visual context

### Book's Original Purpose

This book is titled "Sources of Shang History" and is fundamentally:
1. A scholarly reference to oracle bone artifacts
2. A teaching text with visual examples
3. A collection of transcriptions with supporting evidence

**Without figures**, it becomes:
- ✓ A text reference (searchable, readable)
- ✗ Not a proper reproduction of the original work
- ✗ Unsuitable for direct scholarly quotation of oracle content

---

## Conclusion

The current approach has:
- ✅ Preserved all textual content
- ✅ Maintained archive references
- ✅ Produced a searchable, readable document
- ❌ Lost the visual evidence layer
- ❌ Reduced utility for oracle bone scholars

**For the book's intended use**, including figures should be considered if:
1. This is meant to be a primary research tool (not just reference)
2. Oracle bone specialists will be using it
3. Verification of transcriptions matters

**Current state is acceptable for**: General reference, text searching, bibliographic use

**Not suitable for**: Direct oracle bone research without access to originals
