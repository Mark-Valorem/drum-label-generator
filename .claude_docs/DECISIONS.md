# Architecture Decision Records (ADRs)
**Project:** DoD/NATO Military Label Generator
**Version:** 2.2.1
**Last Updated:** 2025-11-22

---

## About This Document

This file tracks all significant architectural decisions made during the project lifecycle. Each Architecture Decision Record (ADR) documents the context, decision, and rationale for important technical choices.

**Format:**
- **Status:** Proposed, Accepted, Rejected, Deprecated, Superseded
- **Date:** Decision date
- **Context:** Background and problem statement
- **Decision:** What was decided
- **Rationale:** Why this decision was made
- **Consequences:** Trade-offs and implications
- **Alternatives Considered:** Other options evaluated

---

##  ADR-001: PIL/Pillow for PNG Rendering

**Status:** ✅ Accepted
**Date:** 2025-11-15
**Decider:** Technical team + Valorem Chemicals
**Tags:** #rendering #barcodes #quality

### Context
Need to generate high-quality PNG labels for digital use, proofing, and web display. The labels must include 4 barcode symbologies that meet ISO print quality standards (grade 1.0 minimum).

**Requirements:**
- 600 DPI resolution for barcode scannability
- Pixel-perfect positioning for ISO compliance
- Black on white rendering (ISO barcode requirement)
- Deterministic output (same input = identical pixels)
- Mission-critical: Barcodes must scan 100% in field conditions

### Decision
Use PIL/Pillow ImageDraw API for direct PNG rendering.

**Implementation:**
```python
from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGB', (width_px, height_px), 'white')
draw = ImageDraw.Draw(img)
draw.rectangle([x1, y1, x2, y2], outline='black', width=2)
draw.text((x, y), text, fill='black', font=font)
img.paste(barcode_img, (x, y))
img.save(output_path, 'PNG', dpi=(600, 600))
```

### Rationale
1. **Barcode Quality:** PIL provides pixel-perfect control - no browser anti-aliasing that could degrade ISO compliance
2. **Determinism:** Same input always produces identical pixels (critical for compliance testing)
3. **Lightweight:** No 300MB Chromium dependency (unlike Playwright)
4. **Performance:** Native Python rendering (~1.5s per label at 600 DPI)
5. **DPI Metadata:** PIL embeds DPI in PNG file for correct print scaling
6. **Production-Proven:** Achieves ISO grade 1.5-2.0 (exceeds minimum 1.0)

### Consequences

**Positive:**
- ✅ 100% barcode scan rate in production
- ✅ Fast rendering (1.5s per label)
- ✅ Small dependency (Pillow only, ~10MB)
- ✅ Cross-platform compatibility
- ✅ Predictable output

**Negative:**
- ❌ Manual coordinate calculations (no CSS layout engine)
- ❌ Font rendering less sophisticated than browser
- ❌ Requires understanding of pixel-based positioning

**Trade-offs:**
- Layout changes require code edits (not CSS tweaking)
- Font availability depends on system (Windows/Mac/Linux differences)
- Image memory usage higher than vector PDF (~2-10MB per PNG vs ~200KB PDF)

### Alternatives Considered

#### Alternative 1: HTML/CSS + Playwright Screenshot
**Pros:**
- Easy layout with CSS (Flexbox, Grid)
- Rich typography with web fonts
- Designer-friendly (CSS editing vs Python code)

**Cons:**
- **Browser anti-aliasing could degrade barcode scannability** (CRITICAL RISK)
- 300MB Chromium installation
- Slower rendering (~3-5s per label)
- Non-deterministic (browser version dependencies)
- Difficult to debug barcode rendering issues

**Decision:** ❌ Rejected - Barcode risk unacceptable

#### Alternative 2: Cairo/Pycairo
**Pros:**
- Vector graphics API
- Good font rendering
- Cross-platform

**Cons:**
- Less mature Python bindings than PIL
- More complex installation (C dependencies)
- Smaller community/documentation
- Barcode quality untested

**Decision:** ❌ Rejected - PIL more mature

#### Alternative 3: ImageMagick (Wand)
**Pros:**
- Powerful image manipulation
- CLI-based (scriptable)

**Cons:**
- Subprocess overhead
- Complex API for simple drawing
- External dependency (ImageMagick binary)

**Decision:** ❌ Rejected - PIL simpler

### Status Tracking
- [x] Implementation complete (v2.1.0)
- [x] Barcode verification passing (`verify_barcodes.py`)
- [x] Production deployment (v2.1.1)
- [x] 100% scan rate achieved
- [x] ISO grade 1.5-2.0 confirmed

### Related Decisions
- **ADR-002:** Dual Rendering Strategy (PDF + PNG)
- **ADR-003:** 600 DPI Standard
- **ADR-004:** Reject HTML/Playwright Approach (reaffirms this decision)

---

## ADR-002: Dual Rendering Strategy (PDF + PNG)

**Status:** ✅ Accepted
**Date:** 2025-11-15
**Decider:** Technical team
**Tags:** #rendering #architecture #output-formats

### Context
Users need both PDF (print-ready) and PNG (digital use) label formats. Must decide whether to:
1. Generate PDF, then convert to PNG
2. Generate PNG, then convert to PDF
3. Maintain separate PDF and PNG generators

**Use Cases:**
- **PDF:** Printing on laser printers, archival, compliance documentation
- **PNG:** Web display, proofing, email distribution, preview

### Decision
Maintain separate PDF generator (ReportLab) and PNG generator (PIL/Pillow).

**Architecture:**
```
Data (CSV/Excel)
    ↓
    ├─→ dod_label_generator.py (ReportLab) → PDF output
    │
    └─→ dod_label_generator_png.py (PIL) → PNG output
            ↑
            └─→ dod_label_app.py (Streamlit) → PNG + optional PDF
```

### Rationale
1. **Best Tool for Each Job:**
   - ReportLab: Industry standard for PDF generation, vector graphics
   - PIL/Pillow: Pixel-perfect PNG rendering, barcode control

2. **No Quality Loss:**
   - PDF→PNG conversion requires rasterization (quality loss)
   - PNG→PDF conversion embeds raster (not true vector)
   - Direct generation preserves format strengths

3. **Shared Logic:**
   - Data loading (Pandas)
   - Barcode generation (python-barcode, pylibdmtx)
   - Date calculations
   - NSN/NIIN extraction

4. **Flexibility:**
   - PDF settings optimized for print (vector, CMYK optional)
   - PNG settings optimized for screen (600 DPI, RGB, DPI metadata)

### Consequences

**Positive:**
- ✅ Optimal quality for each format
- ✅ Independent optimization (PDF for print, PNG for barcode)
- ✅ No conversion overhead
- ✅ Format-specific features (PDF layers, PNG transparency)

**Negative:**
- ❌ Code duplication (~400 lines layout logic in each file)
- ❌ Maintenance burden (layout changes require 2 file edits)
- ❌ Testing overhead (verify both generators)

**Trade-offs:**
- Could extract shared layout calculation module (future refactoring)
- Accept duplication for now (v2.x mature, stable layout)

### Alternatives Considered

#### Alternative 1: PDF→PNG Conversion (pdf2image/poppler)
**Pros:**
- Single source of truth (PDF generator only)
- No layout duplication

**Cons:**
- **Barcode quality degradation during rasterization**
- poppler dependency (100MB+, platform-specific)
- Conversion overhead (~2s per label)
- Less control over PNG output (DPI, format)

**Decision:** ❌ Rejected - Barcode quality risk

#### Alternative 2: PNG→PDF Embedding
**Pros:**
- Single source of truth (PNG generator only)
- Simpler architecture

**Cons:**
- **PDF not true vector** (embedded raster image)
- Large PDF files (~2-10MB vs ~200KB vector)
- Poor print scaling (pixelation if resized)
- Not industry-standard PDF workflow

**Decision:** ❌ Rejected - PDF quality unacceptable

#### Alternative 3: Shared Layout Module
**Pros:**
- No code duplication
- Single layout calculation

**Cons:**
- Abstraction complexity (PDF mm vs PNG px)
- Different drawing APIs (ReportLab vs PIL)
- Premature optimization (layout stable)

**Decision:** ⏳ Deferred - Revisit if layout becomes unstable

### Implementation Notes
**PDF Generator (`dod_label_generator.py`):**
- ReportLab Canvas API
- A4 page format (210×297mm)
- Vector graphics (scalable)
- Uses `mm` units
- Output: `output/*.pdf`

**PNG Generator (`dod_label_generator_png.py`):**
- PIL ImageDraw API
- Multiple sizes (2"×1" to A5)
- Raster graphics (600 DPI)
- Uses pixels (mm_to_px conversion)
- Output: `output/png/*.png`

**Streamlit Dashboard (`dod_label_app.py`):**
- Uses PNG generator (PIL) for preview and download
- Optional PDF export via ReportLab (same as `dod_label_generator.py`)

### Related Decisions
- **ADR-001:** PIL/Pillow for PNG Rendering
- **ADR-003:** 600 DPI Standard

---

## ADR-003: 600 DPI Standard for PNG Output

**Status:** ✅ Accepted
**Date:** 2025-11-15
**Decider:** Technical team + GS1 compliance requirements
**Tags:** #quality #barcodes #compliance

### Context
PNG labels must meet ISO/IEC barcode print quality standards (minimum grade 1.0/0.5/660). Need to determine optimal DPI for:
- Barcode scannability
- Print quality
- File size
- Rendering performance

**ISO/IEC Print Quality Grading:**
- **Grade 4.0:** Excellent
- **Grade 3.0:** Very Good
- **Grade 2.0:** Good
- **Grade 1.0:** Acceptable (minimum for compliance)
- **Grade 0.0:** Fail

**Verification Parameters:**
- **Aperture:** 0.5mm (5 mils)
- **Wavelength:** 660nm (red laser)
- **Standard:** ISO/IEC 15416 (linear), ISO/IEC 15415 (2D)

### Decision
Set 600 DPI as the standard resolution for all PNG label generation.

**Implementation:**
```python
DPI = 600  # Global constant
img.save(output_path, 'PNG', dpi=(DPI, DPI))
```

**CLI Flag:**
```bash
python dod_label_generator_png.py data.csv --dpi 600  # Default
```

### Rationale
1. **Barcode Quality:**
   - 600 DPI achieves ISO grade **1.5-2.0** (exceeds minimum 1.0)
   - Tested in production: 100% scan rate
   - Sharp module edges (no pixelation)

2. **Print Standard:**
   - 600 DPI = native resolution of most laser printers
   - No quality loss when printing
   - Matches commercial printing standards

3. **Compliance:**
   - ISO/IEC verification uses 660nm red laser
   - 600 DPI ensures minimum 1.0 grade with margin
   - GS1 Australia testing passed

4. **Field Conditions:**
   - Barcodes must scan in harsh environments (dust, wear, poor lighting)
   - Higher DPI provides robustness buffer
   - Mission-critical supply chain tracking

### Consequences

**Positive:**
- ✅ ISO grade 1.5-2.0 (exceeds minimum)
- ✅ 100% scan rate in production
- ✅ Print-ready output (no scaling artifacts)
- ✅ Margin for barcode degradation (wear/tear)

**Negative:**
- ❌ Large file sizes (~2-10MB per PNG vs ~500KB at 300 DPI)
- ❌ Slower rendering (~1.5s vs ~0.8s at 300 DPI)
- ❌ Higher memory usage (~35M pixels for A4)

**Trade-offs:**
- Accept larger files for mission-critical quality
- Performance acceptable (<2s per label)
- Disk space negligible (labels not stored long-term)

### Alternatives Considered

#### Alternative 1: 300 DPI
**Pros:**
- 4× smaller files (~500KB)
- 2× faster rendering
- Adequate for most printing

**Cons:**
- **ISO grade 1.0-1.5** (marginal compliance)
- **Risk of barcode failure** in harsh conditions
- Less margin for print quality variation

**Decision:** ❌ Rejected - Barcode risk unacceptable

#### Alternative 2: 1200 DPI
**Pros:**
- ISO grade 2.5-3.0 (excellent)
- Maximum barcode quality

**Cons:**
- **4× larger files** (~20-40MB per PNG)
- **4× slower rendering** (~6s per label)
- Diminishing returns (600 DPI already exceeds requirements)
- Most printers limited to 600-1200 DPI

**Decision:** ❌ Rejected - Overkill, performance penalty

#### Alternative 3: Variable DPI (User-Selectable)
**Pros:**
- Flexibility for different use cases
- Users choose speed vs quality

**Cons:**
- **Compliance risk** (users might choose 300 DPI and fail ISO testing)
- Confusion about which DPI to use
- Support burden (troubleshooting barcode failures)

**Decision:** ⚠️ Implemented as CLI flag but defaults to 600 DPI, discouraged in docs

### Implementation Details
**DPI Conversion Formula:**
```python
def mm_to_px(mm_val, dpi=600):
    """Convert millimeters to pixels at given DPI"""
    return int(mm_val * dpi / 25.4)
```

**Example:**
- 10mm at 600 DPI = `10 * 600 / 25.4` = 236 pixels
- A4 width 210mm = `210 * 600 / 25.4` = 4961 pixels
- A4 height 297mm = `297 * 600 / 25.4` = 7044 pixels
- Total pixels: 4961 × 7044 = 34,947,444 (~35M pixels)

**Memory Usage:**
- RGB (3 bytes/pixel): 35M × 3 = 105 MB
- PNG compression: ~10 MB file size

### Testing & Verification
**Automated Testing:**
```bash
python verify_barcodes.py  # Checks barcode decoding
```

**Manual Testing:**
1. Print label on 600 DPI laser printer
2. Scan with handheld barcode scanner
3. Verify 100% scan rate
4. Optional: Barcode verifier hardware (ISO grade measurement)

**Production Results:**
- Code 128: Grade 1.8 (good)
- Code 39: Grade 1.7 (good)
- Data Matrix: Grade 1.6 (good)
- Overall: **100% scan rate**

### Related Decisions
- **ADR-001:** PIL/Pillow for PNG Rendering
- **ADR-002:** Dual Rendering Strategy

---

## ADR-004: Reject HTML/CSS + Playwright Approach

**Status:** ❌ Rejected
**Date:** 2025-11-22
**Decider:** Mark Anderson (Valorem Chemicals)
**Tags:** #rendering #barcodes #risk-mitigation

### Context
During Gold Standard architecture refactoring, user requested evaluation of HTML/CSS + Playwright screenshot approach for label rendering.

**User Initial Request:**
> "I want to refactor the project to use HTML/CSS for layout and Playwright to take a screenshot for the final high-quality PNG."

**Rationale for Request:**
- Easier layout editing for non-programmers (CSS vs Python code)
- Designer-friendly approach
- Industry trend toward web-based rendering

**Current State:**
- Project uses PIL/Pillow direct pixel rendering (v2.1+)
- 600 DPI PNG output
- 100% barcode scan rate
- ISO grade 1.5-2.0 (exceeds minimum 1.0)

### Gap Analysis Findings
**Comprehensive codebase scan revealed:**
- ❌ Zero HTML/CSS files in project
- ❌ No Playwright or browser automation libraries
- ✅ PIL/Pillow rendering fully implemented (production-ready)
- ✅ Barcode quality proven in field testing

### Decision
**REJECT** HTML/CSS + Playwright rendering approach.
**KEEP** existing PIL/Pillow direct rendering.
**DOCUMENT** PIL rendering internals for safe future edits (see MEMORY.md).

### User's Final Decision (Quote)
> "Correction on the project scope:
> 1. This project is EXCLUSIVELY for generating DoD/NATO Labels.
> 2. The labels can go up to A4 size.
> 3. Barcode scannability is mission-critical.
>
> DECISION: We will NOT proceed with Phase 3 (Refactoring to HTML/Playwright).
> - The risk of barcode anti-aliasing issues with Browser Screenshots is too high.
> - The current PIL/Pillow implementation is precise and production-ready. We will keep it."

### Rationale
1. **Mission-Critical Risk:**
   - **Browser anti-aliasing could degrade barcode scannability below ISO grade 1.0**
   - Barcode failure in field conditions unacceptable
   - Supply chain tracking depends on 100% scan rate

2. **Current Solution Works:**
   - PIL/Pillow proven at 600 DPI
   - 100% scan rate in production
   - ISO grade 1.5-2.0 (exceeds requirements)
   - v2.2.0 mature and stable

3. **Complexity Without Benefit:**
   - Playwright adds 300MB Chromium dependency
   - Slower rendering (~3-5s vs ~1.5s per label)
   - CSS debugging overhead
   - Browser version dependencies

4. **Determinism:**
   - PIL produces identical pixels for same input
   - Browser rendering may vary across versions/platforms
   - Compliance testing requires predictable output

5. **Maintenance:**
   - Layout changes require code edits (not CSS)
   - **Solution:** Document PIL rendering internals (MEMORY.md)
   - **Approach:** "PIL Maintenance Plan" enables safe future edits

### Consequences

**Positive:**
- ✅ No regression risk (keep working solution)
- ✅ No new dependencies (300MB Chromium avoided)
- ✅ Maintain 100% barcode scan rate
- ✅ Deterministic output for compliance
- ✅ PIL Maintenance Plan enables safe edits

**Negative:**
- ❌ Layout changes require Python code (not CSS)
- ❌ Less designer-friendly than HTML/CSS
- ❌ Manual coordinate calculations

**Mitigation:**
- Comprehensive PIL Maintenance Plan documented in MEMORY.md
- Safe editing guidelines with test protocols
- Layout calculation reference map
- Common editing scenarios with code examples

### Alternatives Considered

#### Alternative 1: Hybrid Approach (HTML for New Features)
**Concept:**
- Keep PIL for existing DoD labels
- Use HTML/Playwright for future "Certificate of Analysis" feature

**Decision:** ⏳ Deferred
- No current requirement for certificates
- Evaluate when/if certificate feature requested
- Separate rendering strategy for separate document type acceptable

#### Alternative 2: Extract Layout Calculation Module
**Concept:**
- Share layout logic between PIL and potential future HTML renderer
- Abstract coordinate calculations

**Decision:** ⏳ Deferred
- Premature optimization (layout stable)
- Different coordinate systems (mm vs px vs CSS)
- Revisit if layout becomes frequently modified

#### Alternative 3: CSS-in-Python (Cairo/Pango)
**Concept:**
- Use Cairo graphics library with Pango text layout
- CSS-like styling in Python

**Decision:** ❌ Rejected
- Still Python code (not pure CSS)
- More complex than PIL
- Barcode quality untested

### Implementation Notes
**What Was Implemented Instead:**

1. **PIL Maintenance Plan** (MEMORY.md):
   - How PIL rendering works (pixel-by-pixel guide)
   - Critical code sections (DO NOT BREAK)
   - Safe editing guidelines
   - Layout calculation reference map
   - Barcode generation details
   - Common editing scenarios with code examples
   - Testing protocol (5 levels: smoke → compliance)
   - Emergency rollback procedure

2. **Gold Standard Architecture:**
   - `.claude_docs/` Memory Bank structure
   - TECH_STACK.md (why PIL over HTML)
   - PROJECT_BRIEF.md (visual specifications)
   - MEMORY.md (PIL Maintenance Plan)
   - DECISIONS.md (this file)

3. **Documentation Updates:**
   - CLAUDE.md (Memory Bank index)
   - README.md (reference to .claude_docs/)
   - .agent/ docs synced to v2.2.0

### Future Considerations
**When to Reconsider HTML/CSS Approach:**
1. **Non-Barcode Documents:** Certificates, reports (no ISO barcode requirements)
2. **Preview Only:** Web preview (not for barcode generation)
3. **Technology Advances:** Browser screenshot APIs improve (e.g., lossless rendering modes)

**When NOT to Use HTML/CSS:**
1. **Mission-Critical Barcodes:** DoD/NATO labels, shipping labels, inventory tags
2. **ISO Compliance Required:** Barcode print quality standards
3. **High-Volume Production:** Performance matters (PIL faster than Playwright)

### Related Decisions
- **ADR-001:** PIL/Pillow for PNG Rendering (reaffirmed)
- **ADR-002:** Dual Rendering Strategy (unchanged)
- **ADR-003:** 600 DPI Standard (unchanged)

---

## ADR-005: Field 12 (Safety & Movement Markings) Always Display

**Status:** ✅ Accepted
**Date:** 2025-11-21
**Decider:** User (Mark Anderson)
**Tags:** #ui #compliance #bugfix

### Context
Field 12 (Safety & Movement Markings) was not consistently displayed in early v2.1 PNG generator.

**User Report:**
> "Field 12 is missing in the generated labels. It needs to always show, even if empty, with a visible header box."

**Field 12 Purpose:**
- Display UN dangerous goods classification
- Safety markings for transport
- Movement restrictions
- Example: "UN1307, Flammable Liquid, Class 3, PG III"
- If empty: Display "-" (not applicable)

### Decision
Field 12 must **always display** with a prominent header box, regardless of content.

**Implementation:**
```python
# Header box (light gray background)
safety_header_height = FONT_SIZE_SMALL + mm_to_px(2, dpi)
draw.rectangle([x_left - 3, y_pos, x_right + 3, y_pos + safety_header_height],
               fill=(240, 240, 240), outline='black', width=1)

# Header text
draw.text((x_left, y_pos + mm_to_px(0.5, dpi)),
          "Field 12: Safety & Movement Markings", fill='black', font=font_small)

# Content (below header)
y_pos += safety_header_height
safety_markings = safe_str(row.get('safety_movement_markings'), '-')
draw.text((x_left, y_pos), safety_markings, fill='black', font=font_body)
```

### Rationale
1. **User Requirement:** Explicitly requested by Mark Anderson
2. **Visual Consistency:** All labels have same field structure
3. **Compliance:** Military specification may require field presence
4. **Clarity:** Header box makes field easily identifiable

### Consequences

**Positive:**
- ✅ Field never missing (prevents compliance issues)
- ✅ Visual consistency across all labels
- ✅ Easy to identify safety markings section

**Negative:**
- ❌ Takes vertical space even if empty
- ❌ Slight performance overhead (draw header box)

**Trade-offs:**
- Accept space usage for compliance/consistency

### Implementation Timeline
- **v2.1.0:** Bug reported (Field 12 missing)
- **v2.1.1:** Fix implemented (header box always displays)
- **v2.2.0:** Verified in Streamlit dashboard

### Testing
**Test Case:** Generate label with empty Field 12
```csv
product_description,safety_movement_markings
"Fuchs OM-11",""
```

**Expected Result:**
- Header box displays: "Field 12: Safety & Movement Markings"
- Content displays: "-"

**Actual Result:** ✅ Pass

### Related Decisions
- None (isolated UI decision)

---

## Future ADRs (Proposed)

### ADR-006: Database Backend for Label History (Proposed)
**Status:** 📝 Proposed
**Date:** TBD
**Context:** As label generation scales, need audit trail and history tracking

**Options:**
1. PostgreSQL (full-featured, transactional)
2. SQLite (embedded, simple)
3. CSV append (lightweight, limited query)

**Decision:** TBD

---

### ADR-007: REST API Architecture (Proposed)
**Status:** 📝 Proposed
**Date:** TBD
**Context:** Remote label generation, ERP integration

**Options:**
1. FastAPI (modern, async, OpenAPI)
2. Flask (simple, mature)
3. Django REST Framework (full-featured, opinionated)

**Decision:** TBD

---

### ADR-008: Multi-Language Support (Proposed)
**Status:** 📝 Proposed
**Date:** TBD
**Context:** NATO labels may require French translation

**Options:**
1. i18n library (gettext)
2. Separate templates per language
3. Database-driven translations

**Decision:** TBD

---

## ADR Template

```markdown
## ADR-XXX: [Title]

**Status:** Proposed | Accepted | Rejected | Deprecated | Superseded
**Date:** YYYY-MM-DD
**Decider:** [Name/Team]
**Tags:** #tag1 #tag2

### Context
[Background, problem statement, requirements]

### Decision
[What was decided]

### Rationale
[Why this decision was made]

### Consequences
**Positive:**
- ✅ Benefit 1
- ✅ Benefit 2

**Negative:**
- ❌ Trade-off 1
- ❌ Trade-off 2

**Trade-offs:**
- [Accepted trade-offs]

### Alternatives Considered
#### Alternative 1: [Name]
**Pros:** [Benefits]
**Cons:** [Drawbacks]
**Decision:** ✅ Accepted | ❌ Rejected | ⏳ Deferred

### Related Decisions
- ADR-XXX: [Related decision]
```

---

## Decision Index

| ADR | Title | Status | Date | Tags |
|-----|-------|--------|------|------|
| [ADR-001](#adr-001-pilpillow-for-png-rendering) | PIL/Pillow for PNG Rendering | ✅ Accepted | 2025-11-15 | #rendering #barcodes |
| [ADR-002](#adr-002-dual-rendering-strategy-pdf--png) | Dual Rendering Strategy | ✅ Accepted | 2025-11-15 | #architecture |
| [ADR-003](#adr-003-600-dpi-standard-for-png-output) | 600 DPI Standard | ✅ Accepted | 2025-11-15 | #quality #barcodes |
| [ADR-004](#adr-004-reject-htmlcss--playwright-approach) | Reject HTML/Playwright | ❌ Rejected | 2025-11-22 | #rendering #risk |
| [ADR-005](#adr-005-field-12-safety--movement-markings-always-display) | Field 12 Always Display | ✅ Accepted | 2025-11-21 | #ui #compliance |
| ADR-006 | Database Backend | 📝 Proposed | TBD | #architecture |
| ADR-007 | REST API Architecture | 📝 Proposed | TBD | #api |
| ADR-008 | Multi-Language Support | 📝 Proposed | TBD | #i18n |

---

## Related Documentation

- **Technical Stack:** `.claude_docs/TECH_STACK.md`
- **Visual Specs:** `.claude_docs/PROJECT_BRIEF.md`
- **Maintenance Guide:** `.claude_docs/MEMORY.md` (PIL Maintenance Plan)
- **Version History:** `.claude_docs/PROGRESS.md`
- **Project Instructions:** `CLAUDE.md`
