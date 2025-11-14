# Quick Reference Card

## Installation

```bash
# One-time setup
bash setup.sh

# Or manually:
pip install -r requirements.txt
python3 test_installation.py
```

## Generate Labels

```bash
# From CSV
python3 drum_label_generator.py data.csv

# From Excel
python3 drum_label_generator.py data.xlsx

# Test with sample data
python3 drum_label_generator.py sample_data.csv
```

## Common Workflows

### Weekly drum batch labels
```bash
# 1. Export from Unleashed to weekly_batch.csv
# 2. Generate labels
python3 drum_label_generator.py weekly_batch.csv

# 3. PDFs saved to output/ folder
# 4. Print on A5 label stock
```

### Single product update
```bash
# 1. Edit sample_data.csv with new batch details
# 2. Keep only the row(s) you need
# 3. Generate
python3 drum_label_generator.py sample_data.csv
```

### Regulatory audit batch
```bash
# Generate labels for specific date range in Excel:
# Filter Unleashed export → Save as audit_batch.xlsx
python3 drum_label_generator.py audit_batch.xlsx

# Archive PDFs for compliance records
```

## Customisation

### Update company details
Edit `config.py`:
```python
COMPANY_NAME = "Valorem Chemicals Pty Ltd"
COMPANY_PHONE = "+61 (0)2 XXXX XXXX"
```

### Adjust layout
Edit `config.py`:
```python
PICTOGRAM_SIZE = 20  # Increase for larger pictograms
FONT_SIZE_BODY = 9   # Decrease for more content
ROW_HEIGHT = 12      # Adjust row spacing
```

### Change barcode format
Edit `drum_label_generator.py`, line ~130:
```python
# Default: product_code + batch_number
barcode_data = str(row.get('product_code', '')) + str(row.get('batch_number', ''))

# Alternative: just batch number
barcode_data = str(row.get('batch_number', ''))

# Alternative: include date
barcode_data = f"{row.get('product_code', '')}_{row.get('manufacture_date', '')}"
```

## Troubleshooting

### Labels cut off
Reduce font sizes or row heights in `config.py`

### Barcode won't scan
- Ensure batch number is alphanumeric only
- Increase `BARCODE_HEIGHT` in config.py
- Print test label and verify resolution

### GHS pictograms missing
- Download PNGs to `ghs_pictograms/` folder
- Name exactly: GHS01.png, GHS02.png, etc.
- Check CSV uses correct codes: "GHS02,GHS07"

### Memory errors with large batches
Process in smaller chunks:
```python
# In Python
import pandas as pd
df = pd.read_csv('large_file.csv')

# Process first 50 rows
df.head(50).to_csv('batch_1.csv', index=False)
```

## CSV Column Reference

**Minimum required:**
- product_code
- product_name  
- batch_number

**Recommended:**
- net_weight
- gross_weight
- manufacture_date
- expiry_date

**For dangerous goods:**
- un_number
- proper_shipping_name
- hazard_class
- packing_group

**For GHS classification:**
- ghs_pictograms (comma-separated: "GHS02,GHS07")
- hazard_statements (pipe-separated: "H315: Skin irritation|H319: Eye irritation")
- precautionary_statements (pipe-separated)

## File Locations

```
drum-label-generator/
├── drum_label_generator.py    # Main script
├── config.py                   # Customisation
├── requirements.txt            # Dependencies
├── sample_data.csv             # Example data
├── ghs_pictograms/            # Add PNG files here
│   └── GHS0X.png
└── output/                    # Generated PDFs
    └── drum_label_*.pdf
```

## Support

Issues or features → Mark Anderson

Common requests:
- Batch processing automation (cron job)
- Unleashed API integration (auto-fetch)
- Email PDFs to production team
- Multi-page layouts (A4 with 2×A5)
