# Changelog

## Version 1.0.0 (2024-11-13)

**Initial Release**

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
