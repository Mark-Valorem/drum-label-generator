# Drum Label Generator - AI Agent Documentation

**version:** v1.0.0
**Last Updated:** 2025-11-14

## Project Overview

Python-based GHS-compliant drum label generator for Valorem Chemicals Pty Ltd. Generates print-ready A5 PDF labels from CSV/Excel data including GHS pictograms, barcodes, QR codes, and regulatory information for chemical drums.

**Tech Stack:**
- Runtime: Python 3.x
- PDF Generation: ReportLab 4.0.7
- Data Processing: Pandas 2.1.4
- Barcode/QR: python-barcode 0.15.1, qrcode 7.4.2
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
- Use descriptive variable names (e.g., `product_code`, `batch_number`)
- Document complex logic with inline comments
- Use type hints where appropriate
- Write docstrings for all classes and public methods
- Follow conventional commits format for Git messages

## Testing Requirements

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
python test_installation.py
```

**Generate Labels:**
```bash
python drum_label_generator.py sample_data.csv
python drum_label_generator.py data.xlsx
```

**Test Setup:**
```bash
python test_installation.py
```

**Check Output:**
```bash
ls output/
```

## Project-Specific Conventions

**File Naming:**
- Output PDFs: `drum_label_{product_code}_{batch_number}_{timestamp}.pdf`
- GHS pictograms: `GHS01.png` through `GHS09.png` (case-insensitive)

**Data Format:**
- CSV/Excel with required columns: `product_code`, `product_name`, `batch_number`
- GHS codes comma-separated: `GHS02,GHS07,GHS09`
- Hazard statements pipe-separated: `H315: Skin irritation|H319: Eye irritation`
- Dates in DD/MM/YYYY format

**Configuration:**
- All settings in `config.py` (fonts, margins, sizes, company details)
- Measurements in millimeters
- A5 page size (148mm × 210mm)

## Compliance Context

**Australian Requirements:**
- WHS Regulations 2011 (Cth)
- GHS Revision 7
- Australian Dangerous Goods Code (ADG)
- UN dangerous goods classification

**Label Requirements:**
- GHS hazard pictograms for classified substances
- Product identification and batch traceability
- Emergency contact information (24-hour)
- Proper shipping names for dangerous goods

## Key Business Rules

1. **Batch Traceability**: Every label must include unique batch number
2. **Regulatory Compliance**: UN numbers required for dangerous goods
3. **Print Quality**: Minimum 600 DPI for barcode readability
4. **Archival**: Save all generated PDFs for audit trail
5. **Weatherproofing**: Use durable label stock for outdoor storage

---

*This file should remain concise. Detailed information belongs in .agent/ documentation.*
