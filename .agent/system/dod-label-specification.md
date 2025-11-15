# DoD/NATO Label Specification v2.0.0

**version:** v2.0.0
**Created:** 2025-11-15
**Last Updated:** 2025-11-15

## Overview

This document describes the Department of Defense (DoD) and NATO military supply label format for Valorem Chemicals products. This is a complete redesign from the GHS chemical labels (v1.x), implementing military specification requirements with multiple barcode symbologies.

## Label Purpose

Military supply labels for products distributed through NATO/DoD supply chains, including:
- NATO Stock Number (NSN) tracking
- Batch/lot traceability
- Expiry date management
- GS1 compliance for logistics
- Military specification adherence

## Data Fields (21 Total)

### Field 1: NATO Code
- **Type:** Text
- **Example:** H-576 (Fuchs OM-33), blank (DCI 4A)
- **Display:** In header section with JSD Reference

### Field 2: JSD Reference
- **Type:** Text
- **Example:** OM-33 (Fuchs OM-33), AL-61 (DCI 4A)
- **Display:** In header section with NATO Code

### Field 3: Specification
- **Type:** Text
- **Example:** DEF STAN 91-39 Issue 4, MIL-PRF-25017
- **Display:** In specification row

### Field 4: Product Description
- **Type:** Text
- **Example:** Fuchs OM-11, DCI 4A
- **Display:** Large text at top of label

### Field 5: Batch Lot No.
- **Type:** Alphanumeric (variable length)
- **Example:** Order-Specific, Order-Specific
- **Display:** In table row
- **Note:** Used as source for Field 7 barcode

### Field 6: Batch Lot Managed
- **Type:** Boolean (Y/N)
- **Example:** Y
- **Display:** In table row

### Field 7: Batch Lot No. Linear Barcode
- **Type:** Code 128 barcode
- **Data Source:** Field 5 (Batch Lot No.)
- **Symbology:** Code 128 (ISO/IEC 15417)
- **Format:** an..10 (alphanumeric, max 10 characters)
- **Example Data:** "BT-Y", "110610-01"
- **HRI:** Below barcode, exclude control characters
- **Minimum Height:** 5.1mm
- **Quality:** Grade 1.0/0.5/660 per ISO/IEC 15416
- **Color:** Black on white

### Field 8: Date of Manufacture
- **Type:** Date
- **Example:** Order-Specific
- **Display:** In table row
- **Note:** Used to calculate Field 13 and Field 19

### Field 9: Contractor's Details
- **Type:** Multi-line text
- **Example:** "Valorem Chemicals Pty Ltd\nAddress"
- **Display:** Full-width row in label body

### Field 10: Capacity or Net Weight
- **Type:** Text with units
- **Example:** 20 LI, 55 US GAL
- **Display:** In table row

### Field 11: NATO Stock No.
- **Type:** 13-digit NSN (NATO Stock Number)
- **Format:** nnnn-nn-nnn-nnnn
- **Example:** 9150-66-035-7879, 6850-99-224-5252
- **Display:** Prominently in header area
- **Note:** NIIN (last 9 digits) extracted for Field 15 and Field 16

### Field 12: Safety and Movement Markings
- **Type:** Multi-line text
- **Example:** "Not Applicable or blank", "UN1307, Flammable Liquid, Class 3, PG III"
- **Display:** Full-width row in label body

### Field 13: Re-Test Date NATO/JSD products
- **Type:** Calculated date
- **Calculation:** Date of Manufacture + Shelf Life
- **Display:** In table row

### Field 14: Test Report No.
- **Type:** Text
- **Example:** - / Blank
- **Display:** In table row

### Field 15: NIIN
- **Type:** 9-digit numeric
- **Extraction:** Last 9 digits of Field 11 (NATO Stock No.)
- **Example:** 660357879, 992245252
- **Display:** As text in designated area
- **Note:** Used as source for Field 16 barcode and GS1 Matrix (Field 21)

### Field 16: NIIN Linear Barcode
- **Type:** Code 39 barcode
- **Data Source:** Field 15 (NIIN only, 9 digits)
- **Symbology:** Code 39 (ISO/IEC 16388)
- **Format:** n9 (9 numeric characters, no separators)
- **Example Data:** 660357879, 992245252
- **Character Set:** 0-9, A-Z, $, %, +, -, /, * (start/stop)
- **Structure:** 9 elements per character (5 bars, 4 spaces; 3 wide, 6 narrow)
- **HRI:** Below barcode, exclude start/stop characters (*)
- **Quality:** Grade 1.0/0.5/660 per ISO/IEC 15416
- **Color:** Black on white

### Field 17: Unit of Issue
- **Type:** Text (unit code)
- **Example:** DR (Drum)
- **Display:** In designated area on label

### Field 18: Hazardous Material Code
- **Type:** Text
- **Example:** Not Applicable or blank, UN1307, 3, III
- **Display:** In designated area on label

### Field 19: Use by Date
- **Type:** Date
- **Calculation:** Date of Manufacture + Shelf Life
- **Format:** DD MMM YY (for display)
- **Example:** 15 JUN 18
- **Display:** In table row
- **Note:** Used as source for Field 20 barcode

### Field 20: Use by Date Linear Barcode
- **Type:** Code 128 or GS1-128 barcode
- **Data Source:** Field 19 (Use by Date)
- **Symbology:** Code 128 or GS1-128 (ISO/IEC 15417)
- **Format Options:**
  - Legacy: an9 ("DD MMM YY") - Example: "15 JUN 18"
  - GS1: AI 17 (17)YYMMDD (n6) - Example: (17)180615
- **HRI:**
  - Legacy: "15 JUN 18"
  - GS1-128: "(17)180615" (include AI in brackets)
- **Quality:** Grade 1.0/0.5/660 per ISO/IEC 15416
- **Color:** Black on white
- **Note:** Submit for GS1 Australia compliance if using GS1-128

### Field 21: GS1 Matrix 2D Barcode
- **Type:** GS1 Data Matrix (ECC 200)
- **Symbology:** Data Matrix (ISO/IEC 16022)
- **Data Elements (GS1 Application Identifiers):**
  - NSN: AI 7001, n13 (NIIN without separators)
  - Batch/Lot: AI 10, an..20
  - Expiry Date: AI 17, n6 (YYMMDD format)
  - Serial Number: AI 21, an..20 (if applicable)
- **Example Encoding:** (7001)6135014354921(10)BT-Y(17)180615
- **Format:** Square (preferred) or rectangular
- **Error Correction:** ECC 200
- **Separator:** FNC1 (ASCII 29) between AI elements
- **Maximum Capacity:** 2,335 alphanumeric characters
- **Requires:** 2D imaging scanners
- **HRI:** Optional (primary AI recommended if included)
- **Quality:** Verify per ISO/IEC 15415
- **Color:** Black on white
- **Compliance:** Submit for GS1 Australia testing
- **Reference:** www.gs1au.org

## Label Layout

### Header Section
```
[Field 4: Product Description] - Large, prominent

[Field 11: NATO Stock No.] - Centered, bold
```

### Left Column (Top Section)
```
[Field 16: NIIN Linear Barcode]    [Field 17: Unit of Issue]    [Field 18: Hazardous Material Code]    [Field 21: GS1 Matrix 2D Barcode]

[Field 15: NIIN]
```

### Barcode Section (Middle)
```
[Field 7: Batch Lot No. Linear Barcode]                    [Field 20: Use by Date Linear Barcode]

[Field 6: Batch Lot Managed]                               [Field 19: Use by Date]
```

### Information Table (Bottom Section)
```
┌─────────────────────────────────────┬────────────────┬─────────────────────┐
│ NATO Code & JSD Reference:          │ [Field 1]      │ [Field 2]           │
├─────────────────────────────────────┴────────────────┴─────────────────────┤
│ Specification:                      [Field 3]                              │
├─────────────────────────────────────┬────────────────────────────────────────┤
│ Batch Lot No.                       │ [Field 5]                              │
├─────────────────────────────────────┼────────────────────────────────────────┤
│ Date of Manufacture                 │ [Field 8]                              │
├─────────────────────────────────────┼────────────────────────────────────────┤
│ Capacity or Net Weight              │ [Field 10]                             │
├─────────────────────────────────────┼────────────────────────────────────────┤
│ Re-Test Date NATO/JSD products      │ [Field 13]                             │
├─────────────────────────────────────┼────────────────────────────────────────┤
│ Test Report No.                     │ [Field 14]                             │
├─────────────────────────────────────┴────────────────────────────────────────┤
│ [Field 12: Safety and Movement Markings]                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ [Field 9: Contractor's Details]                                             │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Barcode Technical Requirements Summary

### Code 128 (Fields 7, 20)
- **Standard:** ISO/IEC 15417
- **Characteristics:** Variable length, continuous, self-checking, bi-directional
- **Character Set:** All 128 ASCII characters (0-9, A-Z, special)
- **Data Format:** Variable length up to specified limits
- **Minimum Height:** 5.1mm (nominal)
- **Quiet Zones:** Must not be encroached by HRI or other elements
- **Verification:** ISO/IEC 15416, minimum grade 1.0/0.5/660

### Code 39 (Field 16)
- **Standard:** ISO/IEC 16388
- **Characteristics:** Variable length, discrete, self-checking, bi-directional
- **Character Set:** 0-9, A-Z, $, %, +, -, /, * (43 characters total)
- **Maximum Length:** 32 characters (30 data + 2 start/stop)
- **Element Structure:** 9 elements per char (5 bars, 4 spaces; 3 wide, 6 narrow)
- **HRI:** Exclude start/stop asterisks (*)
- **Verification:** ISO/IEC 15416, minimum grade 1.0/0.5/660

### GS1 Data Matrix (Field 21)
- **Standard:** ISO/IEC 16022
- **Type:** 2D matrix with perimeter finder pattern
- **Error Correction:** ECC 200 (default)
- **Format:** Square (preferred) or rectangular
- **Module:** Square, uniform size
- **Scanner:** Requires 2D imaging (not laser)
- **GS1 Compliance:** FNC1 character (ASCII 29) required as first character and between AIs
- **Verification:** ISO/IEC 15415
- **Testing:** GS1 Australia compliance testing required

## Print Quality Standards

All barcodes must meet:
- **Minimum Grade:** 1.0/0.5/660
  - 1.0 = minimum symbol grade
  - 0.5 = aperture diameter (mm)
  - 660 = wavelength (nm, red light)
- **Color:** Black bars/modules on white background
- **Verification:** Per respective ISO standards
- **Contrast:** High contrast required for reliable scanning

## GS1 Application Identifier (AI) Reference

| AI   | Data Content          | Format  | Length      |
|------|-----------------------|---------|-------------|
| 10   | Batch/Lot Number      | an      | ..20        |
| 17   | Expiration Date       | n       | 6 (YYMMDD)  |
| 21   | Serial Number         | an      | ..20        |
| 7001 | NSN                   | n       | 13          |

## Data Validation Rules

1. **NIIN Extraction:** Last 9 digits of NSN (Field 11)
2. **Date Calculations:**
   - Field 13 (Re-Test Date) = Field 8 + Shelf Life
   - Field 19 (Use by Date) = Field 8 + Shelf Life
3. **Barcode Data Length:**
   - Field 7 (Batch Lot): max 10 characters
   - Field 16 (NIIN): exactly 9 numeric digits
   - Field 20 (Use by Date): 9 characters (legacy) or variable (GS1)
   - Field 21 (GS1 Matrix): up to 2,335 alphanumeric

## Compliance References

- **ISO/IEC 15417:** Code 128 specification
- **ISO/IEC 16388:** Code 39 specification
- **ISO/IEC 16022:** Data Matrix specification
- **ISO/IEC 15416:** Linear barcode print quality
- **ISO/IEC 15415:** 2D barcode print quality
- **GS1 General Specifications:** www.gs1au.org
- **MIL-STD-129:** Military marking for shipment and storage
- **NATO STANAG:** Applicable standardization agreements

## Product Examples

### Fuchs OM-33 [200kg Drum]
- NATO Code: H-576
- JSD Reference: OM-33
- Specification: DEF STAN 91-39 Issue 4
- Product Description: Fuchs OM-11
- NATO Stock No.: 9150-66-035-7879
- NIIN: 660357879
- Unit of Issue: DR (Drum)
- Capacity: 20 LI
- Hazardous Material: Not Applicable or blank
- Batch Lot Managed: Y

### DCI 4A [55 US GAL]
- NATO Code: (blank)
- JSD Reference: AL-61
- Specification: MIL-PRF-25017
- Product Description: DCI 4A
- NATO Stock No.: 6850-99-224-5252
- NIIN: 992245252
- Unit of Issue: DR (Drum)
- Capacity: 55 US GAL
- Hazardous Material: UN1307, Flammable Liquid, Class 3, PG III
- Batch Lot Managed: Y

## Version History

- **v2.0.0 (2025-11-15):** Complete redesign from GHS chemical labels to DoD/NATO military supply labels
- **v1.0.0 (2025-11-14):** Initial GHS chemical label system
