# Changelog

## Version 2.1.1 (2025-11-21)

**PNG Output Support**

New Features:
- New `dod_label_generator_png.py` script for high-resolution PNG output
- 600 DPI output resolution (configurable via --dpi flag)
- Multiple label sizes: A5, A6, 4x6", 4x4", 3x2", A4
- 10mm bleed margins on all sides for print trimming
- Dashed cut-line around label boundary
- Direct PIL/Pillow rendering (no poppler/pdf2image dependency)
- Fixed NIIN/Batch Lot barcode overlap issue from v2.1.0

Usage:
```bash
python dod_label_generator_png.py sample_data_dod.csv --size A5
python dod_label_generator_png.py sample_data_dod.csv --all-sizes
python dod_label_generator_png.py sample_data_dod.csv --dpi 300
```

Output: `output/png/` folder

---

## Version 2.1.0 (2025-11-21)

**GS1 Data Matrix Fix**

Fixed:
- NSN encoding now uses full 13-digit NSN (no hyphens) per GS1 spec
- Added FNC1/GS separators (ASCII 29) between variable-length AI fields
- Date format corrected to DD MMM YYYY for display fields
- Proper handling of nan/empty values (displays "-" instead of "nan")
- Layout improvements for field visibility

GS1 Data Matrix encoding:
```
7001{NSN_13digits}<GS>10{BatchLot}<GS>17{YYMMDD}
```

---

## Version 2.0.0 (2025-11-15)

**DoD/NATO Military Labels - Major Release**

Complete redesign from GHS chemical labels to military supply labels:
- 4 barcode symbologies (Code 128, Code 39, GS1 Data Matrix)
- 21-field data schema with NSN/NIIN integration
- MIL-STD-129, ISO/IEC, and GS1 compliance
- A4 page format (210×297mm)
- Barcode verification suite (`verify_barcodes.py`)
- Products: Fuchs OM-33 (NATO H-576), DCI 4A (JSD AL-61)

---

## Version 1.0.0 (2024-11-13)

**Initial Release - GHS Chemical Labels**

Features:
- A5 drum label generation from CSV/Excel
- GHS pictogram support (9 standard hazard symbols)
- Code128 barcode generation
- QR code generation with custom data
- 2-column table layout with regulatory information
- UN dangerous goods classification fields
- Hazard and precautionary statements
- Storage instructions and emergency contact
- Batch processing for multiple labels
- Configurable layout and styling
- British English formatting
- Valorem Chemicals branding

Supported Data Sources:
- CSV files
- Excel files (.xlsx, .xls)

Output:
- Print-ready A5 PDFs
- Individual file per drum/batch

## Roadmap

**Version 1.1 (Planned)**
- Multi-label per page (A4 with 2×A5)
- Unleashed API integration
- Automated email distribution
- Label revision tracking

**Version 1.2 (Future)**
- QR code batch traceability lookup
- Template variants (different layouts)
- Barcode format options (EAN-13, QR as barcode)
- AICIS compliance fields

**Version 2.0 (Long-term)**
- Web interface for label generation
- Integration with ERP systems
- Automated scheduled printing
- Label inventory management

## Known Issues

- GHS pictograms must be manually downloaded (licensing restrictions)
- Large batches (>500 labels) may require processing in chunks
- Barcode validation limited to alphanumeric characters

## Contributing

Report issues or suggest features to Mark Anderson.

## Licence

Internal use for Valorem Chemicals Pty Ltd.
