# Comprehensive Formatting Audit Report
## "Sources of Shang History: The Oracle-Bone Inscriptions of Bronze Age China"

**Audit Date:** 2026-04-30  
**Current State:** 191-page PDF (8.4 MB), 4,816 total LaTeX lines across 5 chapters  
**Status:** Compiled and rendering successfully

---

## 1. CURRENT STATE ASSESSMENT

### Document Structure
- **Compilation:** XeTeX with xeCJK for CJK font support (Noto Serif CJK SC)
- **Engine:** xdvipdfmx, PDF 1.7
- **Pages:** 191 pages in A4 format
- **Chapters:** 5 main chapters (ch01.tex: 618 lines, ch02.tex: 851 lines, ch03.tex: 1120 lines, ch04.tex: 1405 lines, ch05.tex: 822 lines)
- **Macro Support:** Minimal Phase 3 macro set (only `\origsecnum{}`, `\authorbyline{}`, `\ednote{}`)
- **CJK Content:** Fully supported with proper font selection

### Critical Issue: Oracle Inscriptions are Unformatted
The primary structural problem in the book is that **oracle bone inscriptions—the core content of this scholarly work**—are presented as continuous text blocks without any visual formatting structure. These inscriptions represent a distinct semantic unit that requires special presentation.

---

## 2. ORACLE BONE INSCRIPTION FORMATTING ISSUES (WITH SPECIFIC EXAMPLES)

### Current Format Problem
Each inscription currently appears as plain text with labels like `(Preface:)`, `(Charge:)`, `(Prognostication:)`, and `(Verification:)` embedded inline, followed by content that runs continuously into the next section.

### Example 1: Simple Paired Inscriptions (ch02.tex, lines 414-427)
**Current LaTeX:**
```latex
THE VERIFICATION
PAIR OF COMPLEMENTARY CHARGES
positive, left side
(Ping-pien 235.2)
Crack-making on chi-mao (day 16),
Ch'üch divined:
``It will rain.''
The king, reading the cracks (said):
``It will rain; it will be a jen day.''
On jen-wu (day 19) it really did rain.
negative, right side
(Ping-pien 235.1)
Crack-making on chi-mao (day 16),
Ch'üch divined:
``It will not perhaps rain.''
```

**Issue:** 
- No visual distinction between "positive, left side" vs "negative, right side" 
- Attribution `(Ping-pien 235.2)` not highlighted or formatted
- Content is a single paragraph, not structured
- In printed book, these likely appear with indentation, possibly in a table or list format

**What it should look like:**
- Two columns or side-by-side layout for positive/negative pairs
- Clear visual separation of inscription components
- Attribution (Ping-pien reference) visually distinguished
- Each component (Preface, Charge, Prognostication, Verification) on its own line or block

---

### Example 2: Complex Multi-Line Inscription (ch02.tex, lines 430-451)
**Current LaTeX:**
```latex
In period I, verifications (and prognostications) might provide considerable detail; for
example:
(Preface:)
(Charge:)
(Prognostication:)

negative, left side
(Ping-pien 1.4)
PAIR OF COMPLEMENTARY CHARGES
Crack-making on kuei-ch'ou (day 50),
Cheng divined:
``From today to ting-ssu (day 54) we
will not perhaps harm the Chou.''
positive, right side
(Ping-pien 1.3)
Crack-making on kuei-ch'ou (day 50),
Cheng divined:
``From today to ting-ssu (day 54) we
will harm the Chou.''
The king, reading the cracks, said:
``(Down to) ting-ssu (day 54) we
should not perhaps harm (them);
on the coming chia-tzu (day 1) we
will harm (them).''
```

**Issue:**
- Labels `(Preface:)`, `(Charge:)`, `(Prognostication:)` exist but have no content—they're just markers
- "PAIR OF COMPLEMENTARY CHARGES" appears out of logical order
- Structural relationships between components are implicit, not explicit
- Line breaks within quoted passages are preserved from OCR but not semantically marked
- The logical structure is:
  - negative charge (left side): lines 1-7
  - positive charge (right side): lines 8-14
  - combined prognostication/verification: lines 15-21

**Expected Structure:** Each inscription should be a discrete, visually bounded unit with clear labeling of all four components.

---

### Example 3: Plastron Set with Multiple Charges (ch03.tex, lines 726-794)
**Current LaTeX:**
```latex
(Preface:)
(Charge:)
(Preface:)
(Charge:)
PAIRS OF COMPLEMENTARY CHARGES
Negative charge (left side)
(2) Crack-making on hsin-yu (day 58), Ch üeh divined:
``This season, the king should not follow Wang Ch'eng to attack the Hsia
Wei, for if he does, we) will not perhaps receive assistance in this case.'' [FOOTNOTE]
(4) Crack-making on hsin-yu (day 58), Ch'üeh divined:
``(This season) the king should not follow Chih Kuo (to attack the Pa-fang. for if he does, we will not perhaps receive assistance in this case).''
Positive charge (right side)
(1) Crack-making on hsin-yu (day 58), Ch'üch divined:
``This season, the king should follow Wang Ch'eng to attack the Hsia Wei, (for if he does, we will receive assistance in this case.''
(3) Crack-making on hsin-yu (day 58), Ch'üeh divined:
``(This season) the king should follow Chih Kuo (to attack the Pa-fang, for if he does, we will receive assistance in this case).''
```

**Issue:**
- Multiple numbered items `(1)`, `(2)`, `(3)`, `(4)` should be a formatted list, not plain text
- "Negative charge (left side)" vs "Positive charge (right side)" could be clear section headers or table cells
- The structure spans multiple items that should be grouped visually
- Numbered items suggest an implicit enumeration that deserves explicit formatting
- Footnotes embedded mid-text disrupt the inscription flow

**What Oracle Bones Require:**
- Clear visualization that items (1), (2), (3), (4) form two pairs
- Pair 1: (1) positive + (2) negative
- Pair 2: (3) positive + (4) negative
- Each pair should visually cluster together

---

### Inscription Statistics

**Total Oracle Inscriptions Found:**
- ch02.tex: 6 instances of `(Preface:)` marker (approximately 2 major inscription blocks)
- ch03.tex: 8 instances of `(Preface:)` marker (approximately 4 major inscription blocks)
- ch04.tex: 0 instances found (but likely has other structured content)
- **Estimated Total:** ~50-100 oracle inscriptions across the book (based on 851/1120/1405 line counts and density)

**Forms Observed:**
1. **Simple pairs** (positive/negative charges side-by-side on one shell)
2. **Complex multi-charge sets** (4-8 numbered items forming logical pairs)
3. **Plastron sets** (same charge repeated across 5 separate shells with numbered variations)
4. **Detailed verifications** (with prognostication results shown alongside charge)

---

## 3. OTHER STRUCTURAL CONTENT ISSUES

### Issue A: Numbered List Items as Plain Text

**Pattern:** Items like `(1)`, `(2)`, `(3)` appear throughout inscriptions but are not formatted as LaTeX lists.

**Examples:**
- ch02.tex line 720-722: Chinese characters with item numbers `(1)` through `(10)`
- ch03.tex line 786-794: Item numbers `(1)` through `(8)` describing "Fu" (ancestors)

**Impact:** 
- 5-10 instances where numbered items should use `\begin{enumerate}` or `\begin{itemize}`
- Visual clarity lost—readers can't distinguish item numbering from parenthetical asides
- Searchability reduced (numbers aren't tagged as list items)

### Issue B: Attribution Lines Not Highlighted

**Pattern:** Lines like `(Ping-pien 235.2)`, `(Ching-hua 2 [fig. 14], left side [S401.4])` provide bibliographic reference but appear as plain text.

**Examples:**
- ch02.tex line 416, 424, 435, 442, 454
- ch03.tex line 731, 743, etc.

**Current:** Embedded in regular paragraph text  
**Expected:** Should be visually distinct (italic, smaller font, boxed, or emphasized) to show they are metadata/references

### Issue C: Quoted Passages and Dialogue

**Pattern:** Multiple levels of quotation:
1. Diviner's charge (initial prophecy) - double quotes
2. King's prognostication (royal interpretation) - nested quotes
3. Verification (outcome) - plain text

**Example (ch02.tex, lines 417-422):**
```
Crack-making on chi-mao (day 16),
Ch'üch divined:
``It will rain.''
The king, reading the cracks (said):
``It will rain; it will be a jen day.''
On jen-wu (day 19) it really did rain.
```

**Issue:**
- Charge `It will rain` (diviner's statement) could be in a different font/color
- King's prognostication `It will rain; it will be a jen day` (royal voice) could be indented or quoted-block style
- Verification (actual outcome) is unformatted plain text
- Mixing of three distinct voices without visual hierarchy

### Issue D: Dedication Page Formatting

**Current (tex/frontmatter/dedication.tex, lines 8-16):**
```latex
SHIMA KUNIO
AND TO THE NUMEROUS OTHER SCHOLARS
WHOSE LABORS OVER THE PAST THREE-QUARTERS OF A CENTURY
HAVE ADVANCED THE COURSE OF ORACLE-BONE SCHOLARSHIP
WASHINGTON
OF
UNIVERSITYO
LIBRARY
SEATTLE
```

**Issue:**
- Line breaks are wrong (OCR error: "UNIVERSITYO" and "OF/LIBRARY/SEATTLE" out of order)
- Should be formatted as a dedication block with proper centering and hierarchy
- Missing structural markup (should likely use `\vspace`, `\centering`, `\Large`, etc.)

---

## 4. COMPARISON WITH EXPECTED PRINTED FORMAT

### Expected Oracle Inscription Layout (Academic Standard)

Based on the markdown source (p_0060.md) and structure, oracle inscriptions in the printed book likely follow this format:

```
┌─────────────────────────────────────────┐
│ (Ping-pien 235.2)                       │ ← Attribution/Reference
├─────────────────────┬───────────────────┤
│   POSITIVE          │   NEGATIVE        │ ← Charge Type
│   (left side)       │   (right side)    │ ← Shell Position
├─────────────────────┼───────────────────┤
│ Crack-making on     │ Crack-making on   │
│ chi-mao (day 16)    │ chi-mao (day 16)  │
│                     │                   │
│ Ch'üch divined:     │ Ch'üch divined:   │
│ "It will rain."     │ "It will not      │
│                     │  perhaps rain."   │
│                     │                   │
│ The king, reading   │ [No king          │
│ the cracks (said):  │  prognostication] │
│ "It will rain; it   │                   │
│ will be a jen day." │                   │
│                     │                   │
│ On jen-wu (day 19)  │ [Unverified]      │
│ it really did rain. │                   │
└─────────────────────┴───────────────────┘
```

**What the PDF currently shows:**
- Same content as above **but as one continuous text block**, with labels embedded inline
- No table structure, no visual columns, no clear delineation
- Attribution not visually prominent
- Shell position ("left side" / "right side") appears as regular text label

### Frontmatter (Page II - Dedication Area)

**Expected:**
- Dedication centered and elegantly formatted
- Clear visual distinction from body text
- Proper typography with appropriate spacing

**Current Issue:**
- OCR errors in line order (e.g., "UNIVERSITYO" suggests "UNIVERSITY OF")
- Line breaks don't make logical sense
- No structural formatting applied

---

## 5. FORMATTING IMPROVEMENT PLAN (PRIORITIZED BY IMPACT)

### Priority 1 (HIGHEST IMPACT) - Oracle Inscription Formatting
**Scope:** ~50-100 inscriptions across book  
**Effort:** HIGH (requires custom LaTeX environment)  
**Impact:** Affects ~20-25% of book content, dramatically improves readability

**Recommended Approach:**
1. Create custom LaTeX environment for oracle inscriptions: `\begin{inscription}...\end{inscription}`
2. Define `\inscriptionpair` macro for left/right inscription pairs
3. Use `tabularx` or `tabulary` for paired layout
4. Clearly separate: Attribution → Preface → Charge → Prognostication → Verification

**Implementation Steps:**
- [ ] Define `\begin{inscriptionpair}` environment in preamble.tex
- [ ] Add macro `\inscriptionattr{reference}` for attribution
- [ ] Add macro `\inscriptioncomponent{label}{content}` for each part
- [ ] Apply formatting to all ~6-8 identified inscription sections
- [ ] Test PDF rendering to ensure readability

### Priority 2 (HIGH IMPACT) - Numbered List Formatting
**Scope:** 5-10 instances of numbered items  
**Effort:** MEDIUM (relatively straightforward find-and-replace)  
**Impact:** Affects ~5% of content; improves semantic clarity and searchability

**Recommended Approach:**
1. Replace inline `(1) ... (2) ... (3)...` with LaTeX enumerate environment
2. Apply consistent formatting to numbered items across all chapters

**Implementation Steps:**
- [ ] Identify all numbered item sequences in ch02-ch04
- [ ] Convert to `\begin{enumerate}\item` format
- [ ] Test for any side effects on spacing/layout

### Priority 3 (MEDIUM IMPACT) - Attribution/Reference Formatting  
**Scope:** ~20-30 attribution lines (e.g., `(Ping-pien 235.2)`)  
**Effort:** MEDIUM (macro definition + targeted application)  
**Impact:** Affects metadata presentation; helps readers trace sources

**Recommended Approach:**
1. Create macro `\inscriptionref{source}` for consistent formatting
2. Format refs as: small caps, italic, or enclosed in brackets with distinct styling
3. Apply to all oracle inscription references

### Priority 4 (MEDIUM-LOW IMPACT) - Quoted Passages and Dialogue
**Scope:** ~30-50 instances of mixed quotation levels  
**Effort:** MEDIUM-HIGH (requires careful analysis of each passage)  
**Impact:** Affects readability and voice differentiation; helps readers understand perspectives

**Recommended Approach:**
1. Use `\begin{quote}` or `\begin{quoting}` environment for diviner's charges
2. Use `\begin{quotation}` for longer prognostications
3. Mark verification outcomes with different font (e.g., `\textit{}` or `\textbf{}`)
4. Color-code or tag different speakers (Diviner, King, Narrator)

### Priority 5 (LOW-MEDIUM IMPACT) - Frontmatter Correction and Formatting
**Scope:** Dedication page and possibly other frontmatter  
**Effort:** LOW (mostly text correction + macro application)  
**Impact:** Affects ~1-2 pages; improves first impression

**Recommended Approach:**
1. Correct OCR errors in dedication.tex (e.g., "UNIVERSITYO" → "UNIVERSITY")
2. Reorder lines to logical sequence
3. Apply centering, spacing, and font size macros

---

## 6. RECOMMENDED LaTeX ENVIRONMENTS AND MACROS TO IMPLEMENT

### 6.1 Core Oracle Inscription Environment

```latex
% Define in preamble.tex

% Simple inscription reference/attribution
\newcommand{\inscriptionref}[1]{%
  {\small\textit{(#1)}}%
}

% Single component (Preface, Charge, etc.)
\newcommand{\inscriptioncomponent}[2]{%
  \noindent\textbf{#1:}\quad #2\par
}

% Simple single inscription
\newenvironment{inscription}
{%
  \par\medskip
  \begin{framed}  % or \begin{fboxed}, requires fancybox package
}
{%
  \end{framed}
  \medskip
}

% Paired inscriptions (positive/negative, left/right)
\newenvironment{inscriptionpair}[2]
{%
  \par\medskip
  \noindent\begin{tabularx}{\textwidth}{Xc X}
  \multicolumn{3}{l}{\inscriptionref{#1}} \\
  \addlinespace
  \textbf{#2 (left)} & & \textbf{Positive (right)} \\
  \midrule
}
{%
  \end{tabularx}
  \medskip
}

% Numbered list items (for multi-charge sets)
\newcommand{\inscriptionitem}[2]{%
  \item[(#1)] #2\par
}
```

### 6.2 Enhanced Version with More Flexibility

```latex
% More sophisticated inscription structure

\newcommand{\inscriptionlabel}[1]{%
  \textbf{\uppercase{#1}}:~%
}

\newcommand{\inscriptionlabelsmall}[1]{%
  \textbf{(#1)}~%
}

\newenvironment{inscriptionblock}[1]
{%
  \par\medskip
  \noindent
  {\small\textit{Reference: #1}}\par
  \vspace{0.5\baselineskip}
  \parindent=0pt
  \leftskip=2em
}
{%
  \leftskip=0pt
  \medskip
}

% For displaying charge + prognostication + verification together
\newenvironment{inscriptionfull}
{%
  \begin{quote}
  \setlength{\parindent}{0pt}
}
{%
  \end{quote}
}
```

### 6.3 Table-Based Oracle Inscription Pair

```latex
\usepackage{booktabs}
\usepackage{array}

\newenvironment{oraclepair}[1]
{%
  \par\medskip
  {\small\textit{#1}}\par
  \begin{center}
  \begin{tabular}{|p{3in}|p{3in}|}
  \hline
  \centering\bfseries POSITIVE (LEFT) & \centering\bfseries NEGATIVE (RIGHT) \\
  \hline
}
{%
  \hline
  \end{tabular}
  \end{center}
  \medskip
}
```

### 6.4 Dedication and Frontmatter Formatting

```latex
% For dedication pages
\newenvironment{dedication}
{%
  \clearpage
  \vspace*{\fill}
  \begin{center}
  \Large
}
{%
  \end{center}
  \vfill
  \clearpage
}

% For section epigraphs or quotes
\newcommand{\epigraph}[2]{%
  \par\medskip
  \begin{quote}
  \textit{#1}
  \par\noindent\raggedleft---#2
  \end{quote}
  \medskip
}
```

### 6.5 Required Package Additions

```latex
\usepackage{fancybox}      % For framed boxes around inscriptions
\usepackage{array}          % For better table column control
\usepackage{tabularx}       % For flexible-width tables
\usepackage{booktabs}       % For professional table formatting
\usepackage{xcolor}         % For potential color-coding of different voices
\usepackage{soul}           % For highlighting/underlining options
```

---

## 7. IMPLEMENTATION PRIORITY & ESTIMATED EFFORT

| Priority | Task | Files Affected | Est. Lines | Effort | Impact |
|----------|------|-----------------|-----------|---------|--------|
| 1 | Define `inscriptionpair` env + macros | preamble.tex | 30-50 | HIGH | 20-25% |
| 1 | Apply to ch02.tex inscriptions | ch02.tex | 40-60 | MEDIUM | 10% |
| 2 | Apply to ch03.tex inscriptions | ch03.tex | 60-80 | MEDIUM | 8% |
| 3 | Format numbered lists | ch02-04.tex | 10-20 | LOW-MEDIUM | 2-3% |
| 4 | Mark attribution lines | ch02-04.tex | 20-30 | LOW | 1-2% |
| 5 | Create quote/dialogue markup | ch02-04.tex | 50-100 | MEDIUM-HIGH | 3-5% |
| 6 | Fix frontmatter OCR errors | frontmatter/ | 5-10 | LOW | <1% |
| 7 | Test PDF rendering | all | - | LOW | - |

**Total Estimated Effort:** 3-5 working days for full implementation  
**Recommendation:** Start with Priority 1 (oracle inscriptions) to address the most visible formatting issue

---

## 8. TESTING STRATEGY

After implementing changes:

1. **Visual Inspection:**
   - [ ] PDF renders without errors
   - [ ] Inscriptions display with proper table structure/formatting
   - [ ] No overlapping text or layout issues
   - [ ] Fonts render correctly (especially CJK characters in references)

2. **Functionality Tests:**
   - [ ] Footnotes within inscriptions still function
   - [ ] Cross-references (e.g., fig. 11, fig. 13) still work
   - [ ] Table of contents updates correctly if sections renumbered

3. **Comparison:**
   - [ ] New formatted inscriptions compared to original book images (if available)
   - [ ] Readability assessment: Can reader quickly parse inscription components?
   - [ ] Verify page counts haven't dramatically increased (reflow should be minimal)

4. **Build Verification:**
   - [ ] `xelatex` compiles without warnings or errors
   - [ ] Final PDF file size reasonable (should stay ~8-10 MB)
   - [ ] All pages render and are searchable

---

## 9. SUMMARY & RECOMMENDATIONS

### Key Findings

1. **Oracle inscriptions are the primary formatting gap** — These comprise 20-25% of book content and are currently displayed as continuous text blocks rather than structured, visually distinct units.

2. **Minimal macro support limits presentation options** — Only 3 Phase 3 macros are defined; no structural formatting for inscriptions, lists, or block quotes.

3. **OCR sources preserve logical structure but lose formatting** — The markdown source files (p_0060.md, etc.) show clear structural markers (Preface:, Charge:, positive/negative) that aren't being rendered in LaTeX.

4. **Multiple levels of quotation and voice** need visual differentiation (diviner vs. king vs. narrator).

5. **Frontmatter has OCR errors** that should be corrected and properly formatted.

### Recommended Next Steps

1. **Implement Phase 4: Oracle Inscription Formatting**
   - Define `\inscriptionpair`, `\inscriptionref`, and related macros in preamble.tex
   - Apply to 2-3 examples in ch02.tex as proof-of-concept
   - Review PDF rendering before full rollout

2. **Establish formatting conventions** for other scholarly content
   - Numbered lists, block quotes, dialogue
   - Consider color-coding or font styling for different voices

3. **Document all new macros** for future editing/maintenance

4. **Plan Phase 5** (Citations) to include formatting of Ping-pien references, S-codes, and other scholarly citations

---

**End of Report**
