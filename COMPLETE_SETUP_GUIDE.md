# Drum Label Generator - Complete Setup Guide

**Production-ready Python script for GHS-compliant A5 drum labels**

---

## Files You Need to Download

Download these files from Claude and place in a new folder called `drum-label-generator/`:

### Core Files (Required)
1. **drum_label_generator.py** - Main script (15KB)
2. **config.py** - Configuration settings
3. **requirements.txt** - Python dependencies
4. **sample_data.csv** - Example data format

### Optional Files
5. **setup.sh** - Automated setup script (Linux/Mac)
6. **test_installation.py** - Installation validation
7. **README.md** - Detailed documentation
8. **QUICK_REFERENCE.md** - Command cheat sheet
9. **CHANGELOG.md** - Version history

### Archive Options
- **drum-label-generator.zip** - Complete project in one file (12KB)
- **drum-label-generator.tar.gz** - Complete project compressed

---

## Installation (5 Minutes)

### Step 1: Create Project Folder

```bash
mkdir drum-label-generator
cd drum-label-generator
```

### Step 2: Place Downloaded Files

Move all downloaded files into this folder.

### Step 3: Install Dependencies

**Automatic (if you have setup.sh):**
```bash
chmod +x setup.sh
bash setup.sh
```

**Manual:**
```bash
pip install reportlab pandas openpyxl python-barcode qrcode Pillow
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 4: Create Required Folders

```bash
mkdir ghs_pictograms
mkdir output
```

---

## GHS Pictograms Setup (10 Minutes)

### Download Pictograms

Visit: https://unece.org/transport/standards/transport-dangerous-goods/ghs-pictograms

Or search: "GHS pictograms PNG download"

### Required Files (9 total)

Download and save to `ghs_pictograms/` folder:

- **GHS01.png** - Explosive
- **GHS02.png** - Flammable  
- **GHS03.png** - Oxidising
- **GHS04.png** - Compressed Gas
- **GHS05.png** - Corrosive
- **GHS06.png** - Toxic
- **GHS07.png** - Harmful/Irritant
- **GHS08.png** - Health Hazard
- **GHS09.png** - Environmental

**Important:** Name files exactly as shown (case doesn't matter).

---

## Configuration (2 Minutes)

Edit `config.py` and update these lines:

```python
# Line 34-37: Company Details
COMPANY_NAME = "Valorem Chemicals Pty Ltd"
COMPANY_ADDRESS = "Sydney, NSW, Australia"  
COMPANY_PHONE = "+61 (0)2 XXXX XXXX"
COMPANY_EMAIL = "info@valoremchemicals.com.au"
```

Optional layout adjustments:

```python
# Pictogram size (default 20mm)
PICTOGRAM_SIZE = 20

# Font sizes
FONT_SIZE_BODY = 9
FONT_SIZE_HEADER = 10

# Row height (default 12mm)
ROW_HEIGHT = 12
```

---

## Data Preparation

### Required CSV Columns

Your CSV/Excel file MUST include:

```csv
product_code,product_name,batch_number
```

### Example Row

```csv
VAL-VM-100,Trilene CP-1100 Viscosity Modifier,LN240815
```

### Optional Columns (Add as Needed)

```csv
supplier
net_weight (e.g., "180 kg")
gross_weight (e.g., "200 kg")
un_number (e.g., "UN3082")
proper_shipping_name
hazard_class (e.g., "9")
packing_group (e.g., "III")
ghs_pictograms (e.g., "GHS02,GHS07")
hazard_statements (e.g., "H315: Skin irritation|H319: Eye irritation")
precautionary_statements (e.g., "P280: Wear gloves|P305: Rinse eyes")
emergency_contact (e.g., "+61 1800 XXX XXX (24hr)")
manufacture_date (format: DD/MM/YYYY)
expiry_date (format: DD/MM/YYYY)
storage_instructions
qr_data (custom QR code content)
```

### Important Formatting

**Multiple GHS pictograms:**
Use commas, no spaces: `GHS02,GHS07,GHS09`

**Multiple hazard statements:**
Use pipe separator: `H315: Skin irritation|H319: Eye irritation|H411: Aquatic toxicity`

**Dates:**
Format as: `15/08/2024` (DD/MM/YYYY)

See `sample_data.csv` for complete examples.

---

## First Test Run

### Validate Installation

```bash
python3 test_installation.py
```

This checks:
- Dependencies installed
- Folders created
- GHS pictograms present
- Sample data valid
- Generates test label

### Generate Sample Labels

```bash
python3 drum_label_generator.py sample_data.csv
```

Check `output/` folder for PDFs.

### Expected Output

```
Loaded 3 records from sample_data.csv
Generated: output/drum_label_VAL-VM-100_LN240815_20241114_103022.pdf
Generated: output/drum_label_VAL-AD-250_KI240722_20241114_103022.pdf
Generated: output/drum_label_VAL-BO-500_EM240910_20241114_103022.pdf

Generation complete. Output saved to 'output/'
```

---

## Production Usage

### From Unleashed Export

1. Export product data to CSV/Excel
2. Ensure columns match required format (see above)
3. Run generator:

```bash
python3 drum_label_generator.py your_export.csv
```

### Weekly Batch Labels

```bash
# Monday morning routine
python3 drum_label_generator.py weekly_drums_20241114.csv

# Print all PDFs from output/ folder
```

### Single Product Label

Create a CSV with one row:

```csv
product_code,product_name,batch_number,net_weight,manufacture_date
VAL-VM-100,Trilene CP-1100,LN240815,180 kg,15/08/2024
```

Generate:

```bash
python3 drum_label_generator.py single_drum.csv
```

---

## Customisation

### Barcode Format

Edit `drum_label_generator.py` around line 130:

**Default (product + batch):**
```python
barcode_data = str(row.get('product_code', '')) + str(row.get('batch_number', ''))
```

**Just batch number:**
```python
barcode_data = str(row.get('batch_number', ''))
```

**Include date:**
```python
barcode_data = f"{row.get('product_code', '')}_{row.get('manufacture_date', '')}"
```

### QR Code Content

Default QR data: `product_code|batch_number|manufacture_date`

To customise, add `qr_data` column to CSV:

```csv
qr_data
"https://valoremchemicals.com.au/batch/LN240815"
```

Or edit script to change default format.

### Layout Changes

All measurements in `config.py`:

```python
# A5 page size
PAGE_WIDTH = 148  # mm
PAGE_HEIGHT = 210  # mm

# Margins
MARGIN_TOP = 8
MARGIN_LEFT = 8

# Column widths (2-column table)
LABEL_COL_WIDTH = 45   # Left column
VALUE_COL_WIDTH = 95   # Right column

# Element sizes
PICTOGRAM_SIZE = 20    # mm
BARCODE_HEIGHT = 15    # mm
QR_SIZE = 25          # mm
```

---

## Troubleshooting

### "GHS pictogram not found"

**Problem:** Script can't find GHS01.png (or other codes)

**Solution:**
1. Check `ghs_pictograms/` folder exists
2. Verify PNG files are named exactly: `GHS01.png` through `GHS09.png`
3. Check CSV has correct codes: `GHS02,GHS07` (no spaces)

### "Missing required columns"

**Problem:** CSV doesn't have required fields

**Solution:**
Ensure CSV includes minimum columns:
- `product_code`
- `product_name`
- `batch_number`

### Barcode won't scan

**Problem:** Printed barcode not readable

**Solution:**
1. Increase barcode height in `config.py`:
   ```python
   BARCODE_HEIGHT = 20  # Was 15
   ```
2. Ensure batch numbers are alphanumeric only (no spaces or special characters)
3. Print at higher DPI (600+ recommended)

### Content cut off / overlapping

**Problem:** Label text runs off page

**Solution:**
1. Reduce font sizes in `config.py`:
   ```python
   FONT_SIZE_BODY = 8  # Was 9
   ```
2. Decrease row height:
   ```python
   ROW_HEIGHT = 10  # Was 12
   ```
3. Shorten text in CSV data

### Module not found errors

**Problem:** `ImportError: No module named 'reportlab'`

**Solution:**
```bash
pip install reportlab pandas openpyxl python-barcode qrcode Pillow
```

Or:
```bash
pip install -r requirements.txt
```

If using Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

---

## Advanced Features

### Batch Processing Large Files

For >500 labels, process in chunks:

```python
import pandas as pd

# Read full file
df = pd.read_csv('large_export.csv')

# Process first 100
df.head(100).to_csv('batch_1.csv', index=False)
```

Then generate:
```bash
python3 drum_label_generator.py batch_1.csv
```

### Filter Specific Suppliers

```python
import pandas as pd

df = pd.read_csv('all_products.csv')
lion = df[df['supplier'] == 'Lion Elastomers']
lion.to_csv('lion_only.csv', index=False)
```

### Automate Weekly Labels (Cron Job)

Create script `weekly_labels.sh`:

```bash
#!/bin/bash
cd /path/to/drum-label-generator
python3 drum_label_generator.py /path/to/weekly_export.csv
# Optional: email PDFs to production team
```

Schedule with cron (Monday 8am):
```bash
crontab -e
# Add line:
0 8 * * 1 /path/to/weekly_labels.sh
```

---

## Project Structure

```
drum-label-generator/
├── drum_label_generator.py    # Main script
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── sample_data.csv             # Example data
├── setup.sh                    # Setup script
├── test_installation.py        # Validation
├── README.md                   # Documentation
├── QUICK_REFERENCE.md          # Commands
├── ghs_pictograms/            # GHS PNG files
│   ├── GHS01.png
│   ├── GHS02.png
│   └── ...
└── output/                    # Generated PDFs
    └── drum_label_*.pdf
```

---

## File Output Format

**Filename pattern:**
```
drum_label_{product_code}_{batch_number}_{timestamp}.pdf
```

**Example:**
```
drum_label_VAL-VM-100_LN240815_20241114_143022.pdf
```

**Archive naming:**
Save PDFs with date for traceability:
```
output_20241114/
├── drum_label_VAL-VM-100_LN240815_20241114_143022.pdf
├── drum_label_VAL-AD-250_KI240722_20241114_143022.pdf
└── ...
```

---

## Compliance Notes

### Australian Requirements

**WHS Regulations 2011:**
- Labels must include product identification
- Hazard pictograms required for classified substances
- Emergency contact information mandatory

**GHS Revision 7:**
- Current standard in Australia
- 9 pictograms available
- Hazard statements coded (H-codes)
- Precautionary statements coded (P-codes)

**Dangerous Goods (ADG Code):**
- UN numbers for transport classification
- Proper shipping names
- Hazard class and packing group

### Label Printing

**Recommended specs:**
- Durable weatherproof label stock
- Minimum 600 DPI printing
- UV-resistant ink for outdoor storage
- A5 size (148mm × 210mm)

**Testing:**
- Verify barcode scans correctly
- Check QR code with mobile device
- Ensure text readable at arm's length
- Confirm GHS pictograms clearly visible

### Record Keeping

**Archive PDFs for:**
- Batch traceability
- Regulatory audits
- Quality management (ISO 9001)
- Compliance evidence

Filename timestamps enable easy audit trails.

---

## Support & Updates

**Current Version:** 1.0.0 (2024-11-14)

**Known Limitations:**
- Maximum 5 GHS pictograms per label (space constraint)
- Barcode requires alphanumeric characters only
- Large batches (>500) best processed in chunks

**Future Enhancements:**
- Unleashed API integration (auto-fetch data)
- Web interface for label generation
- Email distribution to production team
- Multi-label per page (A4 with 2×A5)
- Label revision tracking

**Contact:**
Mark Anderson, Valorem Chemicals Pty Ltd

---

## Quick Command Reference

```bash
# Setup
pip install -r requirements.txt
python3 test_installation.py

# Generate labels
python3 drum_label_generator.py data.csv
python3 drum_label_generator.py data.xlsx

# Test sample
python3 drum_label_generator.py sample_data.csv

# Check output
ls output/
```

---

**Built for Valorem Chemicals Pty Ltd**
GHS-compliant drum labelling solution
