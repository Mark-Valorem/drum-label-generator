# Drum Label Generator

**GHS-compliant A5 drum label generator for Valorem Chemicals**

Generates print-ready PDF labels from CSV/Excel data including:
- GHS hazard pictograms
- Barcodes (Code128)
- QR codes
- Regulatory information (UN numbers, hazard statements)
- 2-column table layout optimised for A5 format

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add GHS pictogram images

Download GHS pictogram PNGs and place in `ghs_pictograms/` folder.

**Required filenames:**
- `GHS01.png` (Explosive)
- `GHS02.png` (Flammable)
- `GHS03.png` (Oxidising)
- `GHS04.png` (Compressed Gas)
- `GHS05.png` (Corrosive)
- `GHS06.png` (Toxic)
- `GHS07.png` (Harmful)
- `GHS08.png` (Health Hazard)
- `GHS09.png` (Environmental)

**Source:** Download from [UNECE GHS website](https://unece.org/transport/standards/transport-dangerous-goods/ghs-pictograms) or use your organisation's approved versions.

### 3. Prepare your data file

Create a CSV or Excel file with these columns:

**Required columns:**
- `product_code` – Internal SKU/code
- `product_name` – Full product name
- `batch_number` – Manufacturing batch/lot number

**Optional columns:**
- `supplier` – Supplier name
- `net_weight` – Net weight (e.g., "180 kg")
- `gross_weight` – Gross weight
- `un_number` – UN classification (e.g., "UN3082")
- `proper_shipping_name` – Shipping name for dangerous goods
- `hazard_class` – Class (e.g., "9")
- `packing_group` – Packing group (I, II, III)
- `ghs_pictograms` – Comma-separated codes (e.g., "GHS02,GHS07")
- `hazard_statements` – Pipe-separated statements (e.g., "H315: Causes skin irritation|H319: Causes eye irritation")
- `precautionary_statements` – Pipe-separated (e.g., "P280: Wear protective gloves|P305: IF IN EYES rinse with water")
- `emergency_contact` – 24hr emergency phone number
- `manufacture_date` – Format: DD/MM/YYYY
- `expiry_date` – Format: DD/MM/YYYY
- `storage_instructions` – Brief storage guidance
- `qr_data` – Custom QR data (defaults to product_code|batch_number|manufacture_date)

See `sample_data.csv` for a complete example.

### 4. Generate labels

```bash
python drum_label_generator.py sample_data.csv
```

PDFs will be saved to `output/` folder.

---

## Configuration

Edit `config.py` to customise:

**Company details:**
```python
COMPANY_NAME = "Valorem Chemicals Pty Ltd"
COMPANY_ADDRESS = "Sydney, NSW, Australia"
COMPANY_PHONE = "+61 (0)2 XXXX XXXX"
```

**Layout dimensions:**
```python
PAGE_WIDTH = 148  # A5 width in mm
MARGIN_TOP = 8
ROW_HEIGHT = 12
```

**Font sizes:**
```python
FONT_SIZE_HEADER = 10
FONT_SIZE_BODY = 9
```

**Pictogram/barcode sizes:**
```python
PICTOGRAM_SIZE = 20  # mm
BARCODE_HEIGHT = 15  # mm
QR_SIZE = 25  # mm
```

---

## Data Preparation Tips

### From Unleashed (or other ERP)

1. Export product data to CSV
2. Add columns for GHS data (hazard statements, pictograms)
3. Ensure batch numbers are included
4. Run the script

### Hazard statements format

Use pipe delimiter (`|`) to separate multiple statements:

```
H315: Causes skin irritation|H319: Causes serious eye irritation|H411: Toxic to aquatic life
```

### GHS pictograms format

Comma-separated codes (no spaces):

```
GHS02,GHS07,GHS09
```

### Barcode data

Script automatically generates barcode from: `product_code + batch_number`

You can customise this in the script if needed.

### QR code data

If `qr_data` column is empty, defaults to:
```
product_code|batch_number|manufacture_date
```

You can include any data: URLs, batch traceability codes, etc.

---

## Output

**Filename format:**
```
drum_label_{product_code}_{batch_number}_{timestamp}.pdf
```

**Example:**
```
drum_label_VAL-VM-100_LN240815_20241113_143022.pdf
```

Each PDF is A5 size, ready to print on label stock.

---

## Troubleshooting

### "GHS pictogram not found"

Check that PNG files exist in `ghs_pictograms/` and match the codes in your CSV (case-insensitive).

### "Missing required columns"

Ensure your CSV includes at minimum: `product_code`, `product_name`, `batch_number`

### Barcode errors

If batch numbers contain special characters, the script will skip barcode generation for that label. Use alphanumeric characters only.

### QR code too dense

If QR data is very long (>150 characters), reduce the data or increase `QR_SIZE` in config.py

### Layout issues

Adjust these in `config.py`:
- Row heights: `ROW_HEIGHT`
- Margins: `MARGIN_TOP`, `MARGIN_LEFT`, etc.
- Column widths: `LABEL_COL_WIDTH`, `VALUE_COL_WIDTH`

---

## Advanced Usage

### Batch processing from Unleashed export

```bash
# Export from Unleashed to drum_data_20241113.xlsx
python drum_label_generator.py drum_data_20241113.xlsx
```

### Filter specific products

Use pandas to pre-filter your CSV:

```python
import pandas as pd

df = pd.read_csv('all_products.csv')
filtered = df[df['supplier'] == 'Lion Elastomers']
filtered.to_csv('lion_products.csv', index=False)
```

Then run:
```bash
python drum_label_generator.py lion_products.csv
```

### Customise label layout

Edit the `create_label()` method in `drum_label_generator.py`.

Current layout sections:
1. Company header
2. Product name
3. Information table
4. GHS pictograms
5. Hazard statements
6. Precautionary statements
7. Storage instructions
8. Emergency contact
9. Barcode (bottom left)
10. QR code (bottom right)

---

## Compliance Notes

**GHS Revision 7 (Australia)**

This generator supports GHS pictograms and standard hazard/precautionary statements. Ensure your data includes:

- Correct UN numbers (if dangerous goods)
- Accurate hazard classifications
- Appropriate precautionary statements
- 24-hour emergency contact

**Label printing:**

- Use durable label stock (weatherproof for outdoor storage)
- Test print alignment before production run
- Archive PDFs for traceability/audit trail

**Regulatory references:**

- Work Health and Safety Regulations 2011 (Cth)
- Australian Dangerous Goods Code (ADG)
- GHS (Globally Harmonized System) Revision 7

---

## Licence

Internal use for Valorem Chemicals Pty Ltd.

---

## Support

For issues or feature requests, contact Mark Anderson.

**Common feature additions:**

- Multiple labels per page (A4 with 2×A5)
- Integration with Unleashed API (auto-fetch product data)
- Email batch PDFs to production team
- Revision tracking for label versions
