# Project Brief - DoD/NATO Military Label Generator
**Version:** 2.2.0
**Last Updated:** 2025-11-22
**Client:** Valorem Chemicals Pty Ltd
**Project Type:** Military Supply Chain Labeling System

---

## Executive Summary

High-precision label generation system for Department of Defense (DoD) and NATO military supply chain compliance. Produces scannable labels with 4 barcode symbologies at 600 DPI, meeting MIL-STD-129 and ISO barcode standards for mission-critical supply chain tracking.

---

## Business Context

### Client
**Valorem Chemicals Pty Ltd**
- Chemical manufacturer and distributor
- NATO/DoD supply chain contractor
- Australian-based operations
- Products: Military-grade lubricants, hydraulic fluids, chemical agents

### Purpose
Generate compliant labels for military products distributed through:
- NATO supply chains (Allied Forces)
- U.S. Department of Defense procurement
- International defense logistics networks

### Critical Requirements
1. **Barcode Scannability:** ISO grade 1.0 minimum (mission-critical)
2. **Print Quality:** 600 DPI for reliable field scanning
3. **Compliance:** MIL-STD-129, NATO STANAG, GS1 standards
4. **Traceability:** NSN/NIIN tracking, batch/lot management
5. **Durability:** Labels must survive harsh storage/transport conditions

---

## Visual Design Specification

### Label Format
**Primary Format:** 21-field military specification label
**Standard Size:** 4" × 6" (101.6mm × 152.4mm)
**Range:** 2" × 1" up to A4 (210mm × 297mm)

### Layout Structure

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│          [PRODUCT DESCRIPTION - LARGE BOLD]              │
│                                                          │
│               NATO Stock No: nnnn-nn-nnn-nnnn            │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  [NIIN Barcode Code 39]  Unit: DR  Hazmat: UN1307  [2D] │
│  NIIN: 660357879                                         │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  [Batch Lot Code 128]            [Date Code 128]        │
│  Batch Lot Managed: Y             Use by: 15 NOV 2027   │
│                                                          │
├──────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────┐ │
│ │ NATO Code: H-576          JSD Reference: OM-33     │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ Specification: DEF STAN 91-39 Issue 4              │ │
│ ├──────────────────────┬─────────────────────────────┤ │
│ │ Batch Lot No.        │ FM251115A                   │ │
│ ├──────────────────────┼─────────────────────────────┤ │
│ │ Date of Manufacture  │ 15/11/2025                  │ │
│ ├──────────────────────┼─────────────────────────────┤ │
│ │ Capacity/Net Weight  │ 20 LI                       │ │
│ ├──────────────────────┼─────────────────────────────┤ │
│ │ Re-Test Date         │ 15/11/2028                  │ │
│ ├──────────────────────┼─────────────────────────────┤ │
│ │ Test Report No.      │ -                           │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ Field 12: Safety & Movement Markings               │ │
│ │ Not Applicable                                     │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ Contractor's Details:                              │ │
│ │ Valorem Chemicals Pty Ltd                          │ │
│ │ 123 Industrial Drive, Sydney NSW 2000, Australia   │ │
│ └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Typography

**Fonts (ReportLab):**
- Header: Helvetica-Bold, 18pt
- Subheader: Helvetica-Bold, 14pt
- Body: Helvetica, 10pt
- Small: Helvetica, 8pt

**Fonts (PIL PNG):**
- Dynamically scaled based on label size
- Base: 4" × 6" reference (scale factor 1.0)
- Range: 0.4× (2"×1") to 1.5× (A4)
- TrueType fonts via `ImageFont.truetype()`

### Color Scheme

**All elements:** Black on white (ISO barcode requirement)
- Primary text: RGB(0, 0, 0) / #000000
- Background: RGB(255, 255, 255) / #FFFFFF
- Borders: 1-2px black outlines
- No color printing required (monochrome laser printer compatible)

### Spacing & Margins

**Bleed:** 5mm (reduced from 10mm for smaller labels)
**Cut-lines:** Displayed in preview, cropped in final output
**Internal padding:** 5mm from label edge
**Field spacing:** 2-3mm between fields
**Barcode quiet zones:** 10× module width (Code 128/39), per ISO spec

---

## Data Model - 21 Fields

### Header Fields (1-4)
1. **NATO Code** - Text (e.g., "H-576", blank)
2. **JSD Reference** - Text (e.g., "OM-33", "AL-61")
3. **Specification** - Text (e.g., "DEF STAN 91-39 Issue 4")
4. **Product Description** - Text (e.g., "Fuchs OM-11", "DCI 4A")

### Identification Fields (5-7)
5. **Batch Lot No.** - Alphanumeric (e.g., "FM251115A")
6. **Batch Lot Managed** - Boolean (Y/N)
7. **Batch Lot Barcode** - Code 128 (auto-generated from Field 5)

### Manufacturing Fields (8-10)
8. **Date of Manufacture** - Date (DD/MM/YYYY)
9. **Contractor's Details** - Multi-line text (pipe-separated)
10. **Capacity or Net Weight** - Text with units (e.g., "20 LI", "55 US GAL")

### NSN/NIIN Fields (11, 15-16)
11. **NATO Stock No.** - 13 digits (nnnn-nn-nnn-nnnn)
15. **NIIN** - 9 digits (auto-extracted from Field 11, last 9 digits)
16. **NIIN Barcode** - Code 39 (auto-generated from Field 15)

### Field 12: CRITICAL - Always Display
12. **Safety & Movement Markings** - Multi-line text
   - **Header box required:** "Field 12: Safety & Movement Markings"
   - Background: RGB(240, 240, 240) light gray
   - Content: UN numbers, hazard class, packing group, or "-"
   - Example: "UN1307, Flammable Liquid, Class 3, PG III"

### Quality & Testing Fields (13-14)
13. **Re-Test Date** - Calculated (Manufacture Date + Shelf Life)
14. **Test Report No.** - Text (usually "-" or blank)

### Logistics Fields (17-18)
17. **Unit of Issue** - Text (e.g., "DR" for drum)
18. **Hazardous Material Code** - Text (e.g., "UN1307, 3, III")

### Expiry Fields (19-20)
19. **Use by Date** - Calculated (Manufacture Date + Shelf Life)
20. **Use by Date Barcode** - Code 128/GS1-128 (YYMMDD format)

### GS1 2D Barcode (21)
21. **GS1 Data Matrix** - 2D barcode with Application Identifiers
   - AI 7001: NSN (13 digits)
   - AI 10: Batch/Lot Number
   - AI 17: Expiry Date (YYMMDD)
   - AI 21: Serial Number (optional)
   - Separator: FNC1 (ASCII 29 / 0x1D)

---

## Barcode Specifications

### Code 128 (Fields 7, 20)
**Standard:** ISO/IEC 15417
**Use Cases:**
- Field 7: Batch Lot Number (alphanumeric)
- Field 20: Use by Date (YYMMDD format)

**Visual Requirements:**
- Minimum height: 5.1mm
- Quiet zones: 10× module width
- Human-Readable Interpretation (HRI): Below barcode
- Color: Black bars on white background
- Quality: ISO grade 1.0 minimum (600 DPI ensures grade 1.5-2.0)

### Code 39 (Field 16)
**Standard:** ISO/IEC 16388
**Use Case:** NIIN (9 digits)

**Visual Requirements:**
- Character set: 0-9 only for NIIN
- Structure: 9 elements per character (3 wide, 6 narrow)
- HRI: Exclude start/stop asterisks (*)
- Quiet zones: 10× narrow bar width
- Color: Black bars on white background
- Quality: ISO grade 1.0 minimum

### GS1 Data Matrix ECC 200 (Field 21)
**Standard:** ISO/IEC 16022
**Use Case:** Comprehensive product data

**Visual Requirements:**
- Format: Square (preferred) or rectangular
- Module size: Uniform, scalable
- Error correction: ECC 200 (default)
- Finder pattern: Perimeter L-shape + timing patterns
- Color: Black cells on white background
- Quality: ISO/IEC 15415 grade 1.0/0.5/660

**Data Encoding Example:**
```
[FNC1]7001915066035787910FM251115A[GS]17271115[GS]21SN123456
```
- `[FNC1]` = ASCII 29 (GS1 separator)
- `7001` = AI for NSN
- `9150660357879` = NSN (13 digits, no hyphens)
- `[GS]` = ASCII 29 (group separator)
- `10` = AI for Batch/Lot
- `FM251115A` = Batch number
- `17` = AI for Expiry Date
- `271115` = 15 Nov 2027 (YYMMDD)
- `21` = AI for Serial Number
- `SN123456` = Serial number

---

## Label Size Matrix

| Size Name | Dimensions (mm) | Dimensions (inches) | DPI | Pixels (W×H) | Use Case |
|-----------|-----------------|---------------------|-----|--------------|----------|
| 2" × 1" | 50.8 × 25.4 | 2.0 × 1.0 | 600 | 1204 × 602 | Small product tags |
| 3" × 2" | 76.2 × 50.8 | 3.0 × 2.0 | 600 | 1807 × 1204 | Medium product labels |
| 4" × 2" | 101.6 × 50.8 | 4.0 × 2.0 | 600 | 2409 × 1204 | Shipping labels |
| 4" × 3" | 101.6 × 76.2 | 4.0 × 3.0 | 600 | 2409 × 1807 | Expanded info |
| 4" × 4" | 101.6 × 101.6 | 4.0 × 4.0 | 600 | 2409 × 2409 | Square labels |
| **4" × 6"** | **101.6 × 152.4** | **4.0 × 6.0** | **600** | **2409 × 3614** | **DoD standard** ⭐ |
| A6 | 105 × 148 | 4.13 × 5.83 | 600 | 2491 × 3508 | European small |
| A5 | 148 × 210 | 5.83 × 8.27 | 600 | 3508 × 4976 | European standard |
| A4 | 210 × 297 | 8.27 × 11.69 | 600 | 4976 × 7044 | Full-page labels |

**Default:** 4" × 6" (DoD/NATO standard shipping label size)

---

## Compliance Requirements

### Military Standards
- **MIL-STD-129:** Military Marking for Shipment and Storage
- **MIL-STD-130:** Identification Marking of U.S. Military Property
- **NATO STANAG:** Standardization Agreements for Supply Classification

### Barcode Standards
- **ISO/IEC 15417:** Code 128 specification
- **ISO/IEC 16388:** Code 39 specification
- **ISO/IEC 16022:** Data Matrix specification
- **ISO/IEC 15416:** Linear barcode print quality verification
- **ISO/IEC 15415:** 2D barcode print quality verification

### GS1 Standards
- **GS1 General Specifications:** Application Identifier definitions
- **GS1 Data Matrix Guideline:** 2D barcode implementation
- **GS1 Australia:** Regional compliance body and testing authority

**Mandatory Testing:**
- Submit Data Matrix samples to GS1 Australia for compliance verification
- Minimum print quality grade: 1.0 (600 DPI typically achieves 1.5-2.0)

### Print Quality Targets

| Barcode Type | Standard | Min Grade | Aperture | Wavelength | Typical @ 600 DPI |
|--------------|----------|-----------|----------|------------|-------------------|
| Code 128 | ISO/IEC 15416 | 1.0 | 0.5mm (5 mils) | 660nm (red) | 1.5-2.0 (excellent) |
| Code 39 | ISO/IEC 15416 | 1.0 | 0.5mm (5 mils) | 660nm (red) | 1.5-2.0 (excellent) |
| Data Matrix | ISO/IEC 15415 | 1.0 | 0.5mm (5 mils) | 660nm (red) | 1.5-2.0 (excellent) |

**Grade Scale:** 0.0 (fail) → 1.0 (acceptable) → 2.0 (good) → 3.0 (very good) → 4.0 (excellent)

---

## Sample Products

### Product 1: Fuchs OM-11
**Category:** Military-grade lubricant
**NATO Code:** H-576
**JSD Reference:** OM-33
**NSN:** 9150-66-035-7879
**NIIN:** 660357879 (auto-extracted)
**Specification:** DEF STAN 91-39 Issue 4
**Batch Example:** FM251115A
**Shelf Life:** 36 months
**Capacity:** 20 LI (liters)
**Safety Markings:** Not Applicable (-)
**Hazmat Classification:** Non-hazardous

### Product 2: DCI 4A
**Category:** Decontamination chemical
**NATO Code:** (blank)
**JSD Reference:** AL-61
**NSN:** 6850-99-224-5252
**NIIN:** 992245252 (auto-extracted)
**Specification:** MIL-PRF-25017
**Batch Example:** DC251115B
**Shelf Life:** 24 months
**Capacity:** 55 US GAL (gallons)
**Safety Markings:** UN1307, Flammable Liquid, Class 3, PG III
**Hazmat Classification:** UN1307, Class 3, PG III

---

## User Interface (Streamlit Dashboard v2.2)

### Features
1. **File Upload:**
   - Drag-and-drop CSV/Excel files
   - Automatic data validation
   - Preview before generation

2. **Data Editing:**
   - Editable table (st.data_editor)
   - Per-row label size selection (dropdown)
   - Real-time validation

3. **Label Preview:**
   - Select any row for preview
   - Full-resolution PNG display
   - Zoom/inspect barcodes

4. **Download Options:**
   - Individual PNGs (ZIP archive)
   - Individual PDFs (ZIP archive)
   - Combined ZIP (all formats)
   - **NEW:** Save to output/ folder checkbox (default: ON)

5. **Settings:**
   - Dark/light mode toggle
   - Help text and tooltips
   - Sample data download

### User Workflow
```
1. Upload CSV/Excel → 2. Edit data (optional) → 3. Preview label →
4. Download (PNG/PDF/ZIP) → 5. Files saved to output/ and browser Downloads
```

---

## Technical Constraints

### Must Maintain
1. **600 DPI Resolution:** Non-negotiable for barcode scannability
2. **PIL/Pillow Rendering:** No HTML/CSS (barcode anti-aliasing risk)
3. **Black on White:** ISO barcode color requirement
4. **Field 12 Always Display:** With header box, even if empty ("-")
5. **ISO Barcode Specs:** Quiet zones, HRI, grade 1.0 minimum

### Must Avoid
1. ❌ **Browser Screenshots:** Anti-aliasing degrades barcode quality
2. ❌ **Lower DPI:** <600 DPI risks ISO compliance failure
3. ❌ **Color Barcodes:** Black on white only per ISO
4. ❌ **Compressed Formats:** JPG/WebP introduce artifacts
5. ❌ **Web Fonts:** Determinism risk across environments

---

## Success Criteria

### Functional Requirements
- ✅ Generate labels from CSV/Excel data
- ✅ 4 barcode types (Code 128 ×2, Code 39, Data Matrix)
- ✅ All 21 fields display correctly
- ✅ Field 12 always shows with header box
- ✅ Multiple label sizes (2"×1" to A4)
- ✅ PNG (600 DPI) + PDF output
- ✅ Streamlit web dashboard
- ✅ Batch processing (50+ labels)

### Quality Requirements
- ✅ Barcode scan rate: 100% (ISO grade 1.0+)
- ✅ Print quality: Laser printer compatible
- ✅ Visual accuracy: Matches specification exactly
- ✅ Data validation: No crashes on malformed input
- ✅ Performance: <2s per label generation

### Compliance Requirements
- ✅ MIL-STD-129 adherence
- ✅ NATO STANAG compliance
- ✅ ISO/IEC barcode standards
- ✅ GS1 Data Matrix testing (submitted to GS1 Australia)

---

## Project Deliverables

### v1.0 (2025-11-14) - GHS Chemical Labels
- ReportLab PDF generator
- GHS pictogram support
- QR code integration
- A5 format labels

### v2.0 (2025-11-15) - DoD/NATO PDF Labels
- Complete redesign for military spec
- 21-field data model
- 4 barcode symbologies
- A4 format labels
- NSN/NIIN tracking

### v2.1 (2025-11-21) - PNG Multi-Size Generator
- PIL/Pillow PNG rendering
- 8 label sizes (2"×1" to A4)
- 600 DPI high-resolution
- Field 12 fix (always display)
- Bleed margins + cut-lines

### v2.2 (2025-11-21) - Streamlit Web Dashboard
- Browser-based UI
- Drag-and-drop upload
- Editable data table
- Per-row label size selection
- Real-time preview
- PNG/PDF/ZIP downloads
- Save to output/ folder option
- VBS launcher for Windows

---

## Future Considerations (NOT APPROVED)

### Potential Enhancements
- Multi-language support (French for NATO)
- PostgreSQL database for label history
- REST API for remote generation
- QR code alternative to Data Matrix

### Explicitly Rejected
- ❌ HTML/CSS + Playwright rendering (barcode risk - **ADR-004**)
- ❌ Lower DPI output (<600) (print quality risk)
- ❌ Colored labels (ISO compliance risk)

---

## Contact & References

**Client:** Valorem Chemicals Pty Ltd
**Project Lead:** Mark Anderson
**Version:** 2.2.0
**Repository:** 2511_DOD Labels

**Standards References:**
- MIL-STD-129: https://quicksearch.dla.mil/
- GS1 Australia: https://www.gs1au.org
- ISO Barcode Standards: https://www.iso.org

**For Technical Details, see:** `.claude_docs/TECH_STACK.md`
**For Maintenance Guide, see:** `.claude_docs/MEMORY.md`
**For Architecture Decisions, see:** `.claude_docs/DECISIONS.md`
