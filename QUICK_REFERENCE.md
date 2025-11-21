# Quick Reference Card

**v2.2.0 | DoD/NATO Military Labels + GHS Chemical Labels**

---

## Installation

```bash
pip install -r requirements_web.txt  # For web dashboard
pip install -r requirements.txt       # For CLI tools
```

---

## Web Dashboard (NEW in v2.2.0) ✨

```bash
streamlit run dod_label_app.py
```

Open http://localhost:8501 - drag & drop CSV/Excel, select label sizes per row, download PNG/PDF/ZIP.

---

## DoD/NATO Command Line (v2.1+)

### Generate PDF Labels
```bash
python dod_label_generator.py sample_data_dod.csv
```

### Generate PNG Labels (High-Resolution)
```bash
# Default A5 at 600 DPI
python dod_label_generator_png.py sample_data_dod.csv --size A5

# Other sizes: A6, 4x6, 4x4, 3x2, A4
python dod_label_generator_png.py sample_data_dod.csv --size 4x6

# All sizes at once
python dod_label_generator_png.py sample_data_dod.csv --all-sizes

# Custom DPI
python dod_label_generator_png.py sample_data_dod.csv --dpi 300
```

### Verify Barcodes
```bash
python verify_barcodes.py
```

**Output:** PDF in `output/`, PNG in `output/png/`

### 4 Barcode Types
| Field | Type | Standard | Content |
|-------|------|----------|---------|
| 7 | Code 128 | ISO 15417 | Batch Lot No. |
| 16 | Code 39 | ISO 16388 | NIIN (9 digits) |
| 20 | Code 128 | ISO 15417 | Use by Date |
| 21 | GS1 Data Matrix | ISO 16022 | NSN + Batch + Expiry |

### GS1 Data Matrix Encoding
```
7001{NSN_13digits}<GS>10{BatchLot}<GS>17{YYMMDD}
```
- AI 7001: NSN (13 digits, no hyphens)
- AI 10: Batch/Lot (variable length)
- AI 17: Expiry date (YYMMDD)
- `<GS>` = ASCII 29 separator

### Date Formats
- **Display (Fields 8, 13, 19):** DD MMM YYYY (e.g., "15 NOV 2027")
- **Barcode (Field 17):** YYMMDD (e.g., "271115")

### DoD CSV Columns (Key Fields)
```
nato_code, jsd_reference, specification, product_description,
batch_lot_no, batch_lot_managed, date_of_manufacture,
contractor_details, capacity_net_weight, nato_stock_no, niin,
safety_movement_markings, shelf_life_months, test_report_no,
unit_of_issue, hazardous_material_code, serial_number
```

---

## GHS Chemical Labels (v1.0)

### Generate Labels
```bash
python drum_label_generator.py sample_data.csv
python drum_label_generator.py data.xlsx
```

### Test Installation
```bash
python test_installation.py
```

**Output:** A5 labels with GHS pictograms in `output/` folder

### GHS CSV Columns
**Required:** `product_code`, `product_name`, `batch_number`

**Optional:** `net_weight`, `un_number`, `ghs_pictograms`, `hazard_statements`

### GHS Data Formats
- Pictograms: `GHS02,GHS07,GHS09` (comma-separated)
- Hazard statements: `H315: Skin irritation|H319: Eye irritation` (pipe-separated)

---

## Customisation (GHS Labels)

### Company Details
Edit `config.py`:
```python
COMPANY_NAME = "Valorem Chemicals Pty Ltd"
COMPANY_PHONE = "+61 (0)2 XXXX XXXX"
```

### Layout
Edit `config.py`:
```python
PICTOGRAM_SIZE = 20  # mm
FONT_SIZE_BODY = 9
ROW_HEIGHT = 12
```

---

## Troubleshooting

### DoD Labels
| Issue | Solution |
|-------|----------|
| Barcode verification fails | Run `python verify_barcodes.py` to diagnose |
| "nan" appearing in fields | Check CSV for empty cells |
| NSN format error | Use 13 digits: `nnnn-nn-nnn-nnnn` |
| Data Matrix won't scan | Ensure 600 DPI print quality |

### GHS Labels
| Issue | Solution |
|-------|----------|
| Labels cut off | Reduce font sizes in `config.py` |
| Barcode won't scan | Use alphanumeric only, increase height |
| Pictograms missing | Add GHS01.png-GHS09.png to `ghs_pictograms/` |

---

## PNG Label Sizes

| Size | Dimensions | Pixels (600 DPI) |
|------|------------|------------------|
| A5 | 148×210mm | 3968×5433px |
| A6 | 105×148mm | 2835×3968px |
| 4x6 | 101.6×152.4mm | 2400×3600px |
| 4x4 | 101.6×101.6mm | 2400×2400px |
| 3x2 | 76×51mm | 1795×1205px |
| A4 | 210×297mm | 5433×7677px |

All PNG labels include 10mm bleed margins and cut-lines.

---

## File Structure

```
project/
├── dod_label_generator.py     # DoD/NATO PDF labels
├── dod_label_generator_png.py # DoD/NATO PNG labels (600 DPI)
├── drum_label_generator.py    # GHS labels (v1.0)
├── verify_barcodes.py         # Barcode validation
├── config.py                  # GHS customisation
├── sample_data_dod.csv        # DoD example data
├── sample_data.csv            # GHS example data
├── ghs_pictograms/            # GHS PNG files
├── output/                    # Generated PDFs
└── output/png/                # Generated PNGs
```

---

## Compliance

**DoD/NATO:** MIL-STD-129, ISO 15417/16388/16022, GS1 specs

**GHS:** GHS Rev 7, WHS Regulations 2011, ADG Code

---

## Support

Issues or features: Mark Anderson, Valorem Chemicals Pty Ltd
