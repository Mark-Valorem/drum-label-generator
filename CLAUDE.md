# Drum Label Generator - AI Agent Documentation

**version:** v2.0.0
**Last Updated:** 2025-11-15

## Project Overview

Python-based label generator for Valorem Chemicals Pty Ltd supporting both:
- **v2.0 (DoD/NATO):** Military supply labels with 4 barcode types (A4 format)
- **v1.0 (GHS):** Chemical hazard labels with GHS pictograms (A5 format)

Generates print-ready PDF labels from CSV/Excel data with multiple barcode symbologies and regulatory compliance.

**Tech Stack:**
- Runtime: Python 3.x
- PDF Generation: ReportLab 4.0.7
- Data Processing: Pandas 2.1.4
- Barcodes: python-barcode 0.16.1, qrcode 8.2, pylibdmtx 0.1.10, segno 1.6.6
- Image Processing: Pillow 10.1.0
- Excel Support: openpyxl 3.1.2

## Documentation Structure

This project uses a .agent folder for maintaining AI agent context:
- `.agent/tasks/` - Implementation plans and PRDs for completed features
- `.agent/system/` - Architecture, database schemas, API documentation
- `.agent/sops/` - Standard operating procedures for common tasks
- `.agent/README.md` - Master index of all documentation
- `archive/` - Archived/deprecated files

## Rules for AI Agent

1. **Before Implementation**: Always read `.agent/README.md` first to understand available context
2. **After Implementation**: Run `/update-doc` to document the work and update SOPs
3. **On Mistakes**: When corrected, generate SOP to prevent recurrence
4. **Research Tasks**: Use sub-agents for research-heavy features to isolate context
5. **After Discrete Tasks**: Run `/compact` to clean conversation history
6. **Version Control**: All documentation updates automatically commit and push to GitHub

## Code Style Guidelines

- Use Python PEP 8 style conventions
- Keep functions focused and single-purpose
- Use descriptive variable names (e.g., `product_code`, `batch_number`, `niin`, `nsn`)
- Document complex logic with inline comments
- Use type hints where appropriate
- Write docstrings for all classes and public methods
- Follow conventional commits format for Git messages

## Testing Requirements

**DoD Labels (v2.0):**
- Run `verify_barcodes.py` to validate all 4 barcode types
- Test Code 128, Code 39, and Data Matrix against ISO specs
- Verify GS1 Application Identifier encoding
- Test with both product examples (Fuchs OM-33, DCI 4A)
- Validate barcode print quality meets grade 1.0/0.5/660

**GHS Labels (v1.0):**
- Test label generation with sample data before production use
- Validate barcode/QR code readability after printing
- Verify GHS pictogram display for all hazard codes
- Test edge cases (missing data, special characters, long text)
- Run `test_installation.py` after environment changes
- Maintain test data in `sample_data.csv`

## Common Commands

**Installation:**
```bash
pip install -r requirements.txt
python test_installation.py  # For v1.0 GHS labels
python verify_barcodes.py    # For v2.0 DoD barcode validation
```

**Generate DoD/NATO Labels (v2.0):**
```bash
python dod_label_generator.py sample_data_dod.csv
```

**Generate GHS Chemical Labels (v1.0):**
```bash
python drum_label_generator.py sample_data.csv
python drum_label_generator.py data.xlsx
```

**Verify Barcodes (v2.0):**
```bash
python verify_barcodes.py
```

**Check Output:**
```bash
ls output/
```

## Project-Specific Conventions

**File Naming:**
- DoD labels (v2.0): `dod_label_{product_description}_{batch_number}_{timestamp}.pdf`
- GHS labels (v1.0): `drum_label_{product_code}_{batch_number}_{timestamp}.pdf`
- GHS pictograms: `GHS01.png` through `GHS09.png` (case-insensitive)

**Data Format (DoD v2.0):**
- CSV/Excel with 21 fields: `product_description`, `nato_stock_no`, `niin`, `batch_lot_no`, `date_of_manufacture`, etc.
- NSN format: nnnn-nn-nnn-nnnn (13 digits)
- NIIN: Last 9 digits of NSN (auto-extracted)
- Contractor details pipe-separated: `Company|Address|City|Country`
- Dates in DD/MM/YYYY format
- Shelf life in months (for expiry calculation)

**Data Format (GHS v1.0):**
- CSV/Excel with required columns: `product_code`, `product_name`, `batch_number`
- GHS codes comma-separated: `GHS02,GHS07,GHS09`
- Hazard statements pipe-separated: `H315: Skin irritation|H319: Eye irritation`
- Dates in DD/MM/YYYY format

**Configuration:**
- v2.0 DoD: Settings in `dod_label_generator.py` (A4, 210mm × 297mm)
- v1.0 GHS: Settings in `config.py` (A5, 148mm × 210mm)
- All measurements in millimeters

## Compliance Context

**DoD/NATO Requirements (v2.0):**
- MIL-STD-129: Military Marking for Shipment and Storage
- NATO STANAG: Standardization Agreements
- ISO/IEC 15417 (Code 128), 16388 (Code 39), 16022 (Data Matrix)
- GS1 General Specifications for AI usage
- Print quality: Grade 1.0/0.5/660 per ISO/IEC 15416/15415

**Australian Requirements (v1.0 GHS):**
- WHS Regulations 2011 (Cth)
- GHS Revision 7
- Australian Dangerous Goods Code (ADG)
- UN dangerous goods classification

**Label Requirements:**
- v2.0: NSN/NIIN tracking, 4 barcode types, military specification
- v1.0: GHS hazard pictograms, product identification, emergency contacts

## Key Business Rules

**DoD/NATO Labels (v2.0):**
1. **NSN/NIIN Tracking**: NATO Stock Number required, NIIN auto-extracted from last 9 digits
2. **Barcode Compliance**: All 4 barcodes must meet ISO specifications
3. **Print Quality**: Minimum 600 DPI, grade 1.0/0.5/660 required
4. **GS1 Compliance**: Submit Data Matrix to GS1 Australia for testing
5. **Military Spec**: MIL-STD-129 compliance mandatory

**GHS Chemical Labels (v1.0):**
1. **Batch Traceability**: Every label must include unique batch number
2. **Regulatory Compliance**: UN numbers required for dangerous goods
3. **Print Quality**: Minimum 600 DPI for barcode readability
4. **Archival**: Save all generated PDFs for audit trail
5. **Weatherproofing**: Use durable label stock for outdoor storage

---

*This file should remain concise. Detailed information belongs in .agent/ documentation.*
