# DoD/NATO Label Generator v2.1.1

**Military specification labels for Valorem Chemicals**

Generates compliant PDF and PNG labels for Department of Defense (DoD) and NATO military supply chain products with multiple barcode symbologies per MIL-STD-129 and ISO specifications.

---

## Overview

This is version 2.1.1, featuring high-resolution PNG output alongside PDF generation. The DoD label system implements:

- **4 Barcode types** across 21 data fields
- **Military specification compliance** (MIL-STD-129, NATO STANAG)
- **ISO barcode standards** (ISO/IEC 15417, 16388, 16022)
- **GS1 compliance** for logistics tracking
- **NATO Stock Number (NSN)** integration

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**New dependencies for v2.0.0:**
- `pylibdmtx==0.1.10` - Data Matrix 2D barcodes
- `segno==1.6.6` - Additional barcode support

### 2. Prepare Data File

Create CSV with these columns (21 fields total):

**Required:**
- `product_description` - Product name
- `nato_stock_no` - 13-digit NSN (format: nnnn-nn-nnn-nnnn)
- `niin` - 9-digit NIIN (extracted from NSN)
- `batch_lot_no` - Batch/lot number (max 10 characters)
- `date_of_manufacture` - Format: DD/MM/YYYY
- `shelf_life_months` - Numeric (for calculating expiry)

**Optional:**
- `nato_code`, `jsd_reference`, `specification`
- `batch_lot_managed` - Y/N
- `contractor_details` - Pipe-separated (|) multi-line
- `capacity_net_weight` - With units (e.g., "20 LI", "55 US GAL")
- `safety_movement_markings` - Hazmat info
- `test_report_no`
- `unit_of_issue` - DR (Drum), etc.
- `hazardous_material_code` - UN codes, class, packing group
- `serial_number` - Optional for GS1 Matrix

See [sample_data_dod.csv](sample_data_dod.csv) for complete example.

### 3. Generate Labels

**PDF Labels (A4):**
```bash
python dod_label_generator.py sample_data_dod.csv
```
PDFs saved to `output/` folder.

**PNG Labels (High-Resolution):**
```bash
# Default A5 size at 600 DPI
python dod_label_generator_png.py sample_data_dod.csv --size A5

# Available sizes: A5, A6, 4x6, 4x4, 3x2, A4
python dod_label_generator_png.py sample_data_dod.csv --size 4x6

# Generate all sizes at once
python dod_label_generator_png.py sample_data_dod.csv --all-sizes

# Custom DPI (default 600)
python dod_label_generator_png.py sample_data_dod.csv --dpi 300
```
PNGs saved to `output/png/` folder with 10mm bleed margins and cut-lines.

### 4. Verify Barcodes

```bash
python verify_barcodes.py
```

Validates all 4 barcode types against specifications.

---

## Barcode Specifications

### Field 7: Batch Lot No. Linear Barcode
- **Symbology:** Code 128 (ISO/IEC 15417)
- **Format:** an..10 (max 10 alphanumeric characters)
- **Data:** Batch/lot number from Field 5
- **Example:** "FM251115A", "110610-01"
- **HRI:** Below barcode, exclude control characters
- **Min Height:** 5.1mm
- **Quality:** Grade 1.0/0.5/660

### Field 16: NIIN Linear Barcode
- **Symbology:** Code 39 (ISO/IEC 16388)
- **Format:** n9 (exactly 9 numeric digits)
- **Data:** NIIN from Field 15 (last 9 digits of NSN)
- **Example:** 660357879, 992245252
- **HRI:** Below barcode, exclude start/stop asterisks
- **Quality:** Grade 1.0/0.5/660

### Field 20: Use by Date Linear Barcode
- **Symbology:** Code 128 or GS1-128 (ISO/IEC 15417)
- **Format (Legacy):** an9 ("DD MMM YY")
- **Format (GS1):** AI 17 + (17)YYMMDD (n6)
- **Data:** Calculated from manufacture date + shelf life
- **Example:** "15 NOV 28" or "(17)281115"
- **HRI:** Include AI in brackets for GS1-128
- **Quality:** Grade 1.0/0.5/660

### Field 21: GS1 Matrix 2D Barcode
- **Symbology:** GS1 Data Matrix ECC 200 (ISO/IEC 16022)
- **GS1 Application Identifiers:**
  - AI 7001: NSN (13 digits)
  - AI 10: Batch/Lot (up to 20 characters)
  - AI 17: Expiry Date (YYMMDD)
  - AI 21: Serial Number (up to 20 characters, optional)
- **Example:** (7001)6135660357879(10)FM251115A(17)281115
- **Format:** Square matrix (preferred)
- **Scanner:** Requires 2D imaging (not laser)
- **Max Capacity:** 2,335 alphanumeric characters
- **Quality:** ISO/IEC 15415

---

## Label Layout

### PDF (A4) / PNG (Multiple Sizes)

```
┌─────────────────────────────────────────────────────────────┐
│                   [Product Description]                      │
│                                                              │
│                   [NATO Stock Number]                        │
│                                                              │
│  [NIIN Barcode]  Unit: DR   Hazmat: UN1307  [Data Matrix]   │
│  NIIN: 660357879                                             │
│                                                              │
│  [Batch Barcode]              [Use by Date Barcode]          │
│  Batch Managed: Y             Use by Date: 30 OCT 2028       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ NATO Code & JSD:   H-576      OM-33                    │ │
│  │ Specification:     DEF STAN 91-39 Issue 4              │ │
│  │ Batch Lot No.:     FM251115A                           │ │
│  │ Date of Mfg:       15 NOV 2025                         │ │
│  │ Capacity:          20 LI                               │ │
│  │ Re-Test Date:      30 OCT 2028                         │ │
│  │ Test Report No.:   -                                   │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ Safety & Movement: -                                   │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ Valorem Chemicals Pty Ltd                              │ │
│  │ 123 Industrial Drive                                   │ │
│  │ Sydney NSW 2000, Australia                             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### PNG Label Sizes

| Size | Dimensions | Pixels (600 DPI) | Use Case |
|------|------------|------------------|----------|
| A5 | 148×210mm | 3968×5433px | Standard label |
| A6 | 105×148mm | 2835×3968px | Small container |
| 4x6 | 101.6×152.4mm | 2400×3600px | Thermal printer |
| 4x4 | 101.6×101.6mm | 2400×2400px | Square label |
| 3x2 | 76×51mm | 1795×1205px | Small tag |
| A4 | 210×297mm | 5433×7677px | Full page |

**Note:** All PNG labels include 10mm bleed margins and dashed cut-lines.

---

## Data Field Reference

| # | Field Name | Type | Example | Required |
|---|------------|------|---------|----------|
| 1 | NATO Code | Text | H-576 | Optional |
| 2 | JSD Reference | Text | OM-33 | Optional |
| 3 | Specification | Text | DEF STAN 91-39 Issue 4 | Optional |
| 4 | Product Description | Text | Fuchs OM-11 | **Yes** |
| 5 | Batch Lot No. | an..10 | FM251115A | **Yes** |
| 6 | Batch Lot Managed | Y/N | Y | Optional |
| 7 | Batch Lot Barcode | Code 128 | (auto-generated) | Auto |
| 8 | Date of Manufacture | DD/MM/YYYY | 15/11/2025 | **Yes** |
| 9 | Contractor's Details | Multi-line | (company info) | Optional |
| 10 | Capacity/Net Weight | Text | 20 LI | Optional |
| 11 | NATO Stock No. | 13 digits | 9150-66-035-7879 | **Yes** |
| 12 | Safety Markings | Text | UN1307, Class 3 | Optional |
| 13 | Re-Test Date | Calculated | (auto-calculated) | Auto |
| 14 | Test Report No. | Text | -/Blank | Optional |
| 15 | NIIN | 9 digits | 660357879 | **Yes** |
| 16 | NIIN Barcode | Code 39 | (auto-generated) | Auto |
| 17 | Unit of Issue | Text | DR | Optional |
| 18 | Hazmat Code | Text | UN1307, 3, III | Optional |
| 19 | Use by Date | Calculated | 15/11/2028 | Auto |
| 20 | Use by Date Barcode | Code 128 | (auto-generated) | Auto |
| 21 | GS1 Matrix Barcode | Data Matrix | (auto-generated) | Auto |

---

## Product Examples

### Fuchs OM-33 [200kg Drum]

```csv
nato_code,jsd_reference,specification,product_description,batch_lot_no,batch_lot_managed,date_of_manufacture,contractor_details,capacity_net_weight,nato_stock_no,niin,safety_movement_markings,shelf_life_months,test_report_no,unit_of_issue,hazardous_material_code,serial_number
H-576,OM-33,DEF STAN 91-39 Issue 4,Fuchs OM-11,FM251115A,Y,15/11/2025,"Valorem Chemicals Pty Ltd|123 Industrial Drive|Sydney NSW 2000|Australia",20 LI,9150-66-035-7879,660357879,Not Applicable or blank,36,-/Blank,DR,Not Applicable or blank,
```

### DCI 4A [55 US GAL]

```csv
,AL-61,MIL-PRF-25017,DCI 4A,DC251115B,Y,15/11/2025,"Valorem Chemicals Pty Ltd|123 Industrial Drive|Sydney NSW 2000|Australia",55 US GAL,6850-99-224-5252,992245252,"UN1307, Flammable Liquid, Class 3, PG III",24,-/Blank,DR,"UN1307, 3, III",
```

---

## Compliance

### Military Standards
- **MIL-STD-129:** Military Marking for Shipment and Storage
- **NATO STANAG:** Standardization Agreements (applicable)

### ISO Barcode Standards
- **ISO/IEC 15417:** Code 128 specification
- **ISO/IEC 16388:** Code 39 specification
- **ISO/IEC 16022:** Data Matrix specification
- **ISO/IEC 15416:** Linear barcode print quality test
- **ISO/IEC 15415:** 2D symbol print quality test

### GS1 Standards
- **GS1 General Specifications:** Application Identifier usage
- **GS1 Australia:** www.gs1au.org for compliance testing

### Print Quality Requirements
All barcodes must meet:
- **Minimum grade:** 1.0/0.5/660
  - 1.0 = minimum symbol grade
  - 0.5mm = aperture diameter
  - 660nm = wavelength (red light)
- **Color:** Black on white background
- **Verification:** Per respective ISO standards

---

## Troubleshooting

### "NIIN must be exactly 9 digits"
**Cause:** NIIN field contains non-numeric or wrong length
**Solution:** Ensure NIIN field has exactly 9 numeric digits (last 9 of NSN)

### "Data Matrix generation failed"
**Cause:** pylibdmtx not installed correctly
**Solution:**
```bash
pip uninstall pylibdmtx
pip install pylibdmtx==0.1.10
```

### Barcode won't scan
**Cause:** Print quality below specification
**Solution:**
- Print at minimum 600 DPI
- Use high-contrast black/white
- Verify barcode grade with ISO/IEC verifier
- Ensure quiet zones not encroached

### GS1 Matrix scanner issues
**Cause:** Using laser scanner instead of 2D imager
**Solution:** Data Matrix requires 2D imaging scanner, not laser

---

## Testing

### Verify Installation

```bash
python verify_barcodes.py
```

Expected output:
```
[OK] PASS  Field 7: Batch Lot Code 128
[OK] PASS  Field 16: NIIN Code 39
[OK] PASS  Field 20: Use by Date Code 128
[OK] PASS  Field 21: GS1 Data Matrix

Results: 4/4 tests passed
```

### Generate Test Labels

```bash
python dod_label_generator.py sample_data_dod.csv
```

Check `output/` for PDF files.

---

## Differences from v1.x (GHS Labels)

| Feature | v1.x (GHS) | v2.x (DoD/NATO) |
|---------|------------|-----------------|
| **Purpose** | Chemical hazard labels | Military supply labels |
| **Page Size** | A5 (148×210mm) | A4 (210×297mm) |
| **Barcodes** | 1 type (Code 128) + QR | 4 types (128, 39, 128, Matrix) |
| **Data Fields** | ~18 fields | 21 fields |
| **Compliance** | GHS Rev 7, WHS 2011 | MIL-STD-129, ISO, GS1 |
| **Pictograms** | 9 GHS pictograms | None |
| **Traceability** | Batch + QR code | NSN + NIIN + GS1 Matrix |

---

## Migration from v1.x

The v1.x GHS chemical label generator remains available:

**For GHS labels (v1.x):**
```bash
python drum_label_generator.py sample_data.csv
```

**For DoD labels (v2.x):**
```bash
python dod_label_generator.py sample_data_dod.csv
```

Both systems can coexist. Use appropriate script for your label type.

---

## Advanced Usage

### Custom Shelf Life Calculation

Default shelf life is 24 months. Override per product:

```csv
shelf_life_months
36  # 3 years for Fuchs OM-33
24  # 2 years for DCI 4A
```

### Serial Number Tracking

Add serial numbers to GS1 Data Matrix (Field 21):

```csv
serial_number
SN20251115001
SN20251115002
```

Serial number will be encoded with AI 21 in Data Matrix.

### GS1-128 vs Legacy Code 128

For Field 20 (Use by Date), code automatically uses legacy Code 128 format ("DD MMM YY"). To use GS1-128 with AI 17, modify `dod_label_generator.py` line 275:

```python
# Change to GS1-128 format
gs1_formatted = f"17{expiry_date_obj.strftime('%y%m%d')}"
use_by_barcode = self.generate_code128(gs1_formatted)
```

**Note:** Submit to GS1 Australia for compliance testing if using GS1-128.

---

## Files

### Core Files
- `dod_label_generator.py` - PDF label generator (A4)
- `dod_label_generator_png.py` - PNG label generator (600 DPI, multiple sizes)
- `sample_data_dod.csv` - Example data for 2 products
- `verify_barcodes.py` - Barcode verification suite

### Output Folders
- `output/` - Generated PDF labels
- `output/png/` - Generated PNG labels

### Documentation
- `README_DOD.md` - This file
- `.agent/system/dod-label-specification.md` - Complete technical specification

### Legacy (v1.x)
- `drum_label_generator.py` - GHS chemical labels
- `sample_data.csv` - GHS example data

---

## Support

**Technical Questions:** Mark Anderson, Valorem Chemicals Pty Ltd

**GS1 Compliance:** www.gs1au.org

**ISO Standards:** www.iso.org

**MIL-STD Documents:** www.dla.mil

---

## Version History

- **v2.1.1 (2025-11-21):** PNG output support
  - New `dod_label_generator_png.py` for high-resolution PNG output
  - Multiple label sizes: A5, A6, 4x6", 4x4", 3x2", A4
  - 600 DPI resolution (configurable)
  - 10mm bleed margins with cut-lines
  - Fixed NIIN/Batch Lot barcode overlap issue
  - Direct PIL/Pillow rendering (no poppler dependency)

- **v2.1.0 (2025-11-21):** GS1 Data Matrix fix
  - Corrected NSN encoding (full 13 digits, no hyphens)
  - Added GS separators (ASCII 29) between AI fields
  - Fixed date format to DD MMM YYYY
  - Proper nan/empty value handling

- **v2.0.0 (2025-11-15):** Complete redesign for DoD/NATO military supply labels
  - 4 barcode symbologies (Code 128, Code 39, GS1 Data Matrix)
  - 21-field data schema
  - MIL-STD-129, ISO, and GS1 compliance
  - NSN/NIIN integration
  - A4 page format

- **v1.0.0 (2025-11-14):** Initial GHS chemical label system
  - A5 labels with GHS pictograms
  - Australian WHS compliance
  - Single barcode type

---

## License

Internal use for Valorem Chemicals Pty Ltd.

For military supply chain and defense contractor applications only.

---

**Built for Valorem Chemicals Pty Ltd**
DoD/NATO Military Supply Label Generator v2.1.1
