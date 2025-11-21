# Label Generator for Valorem Chemicals

**v2.2.0: DoD/NATO Military Labels | v1.0: GHS Chemical Labels**

This project generates print-ready PDF and PNG labels for Valorem Chemicals Pty Ltd, supporting both military supply chain and chemical hazard labeling requirements.

---

## 🚀 Quick Start

### Web Dashboard (NEW in v2.2.0) ✨

```bash
# Install dependencies
pip install -r requirements_web.txt

# Launch web dashboard
streamlit run dod_label_app.py
```

Open http://localhost:8501 in your browser for drag-and-drop label generation!

---

### DoD/NATO Command Line (v2.1+)

```bash
# Install dependencies
pip install -r requirements.txt

# Generate PDF labels
python dod_label_generator.py sample_data_dod.csv

# Generate high-resolution PNG labels (600 DPI)
python dod_label_generator_png.py sample_data_dod.csv --size A5

# Generate PNG labels in all sizes
python dod_label_generator_png.py sample_data_dod.csv --all-sizes

# Verify all 4 barcode types
python verify_barcodes.py
```

**Output:** PDF labels in `output/`, PNG labels in `output/png/`

**See:** [README_DOD.md](README_DOD.md) for complete documentation

---

### GHS Chemical Labels (v1.0)

```bash
# Install dependencies
pip install -r requirements.txt

# Generate GHS labels
python drum_label_generator.py sample_data.csv
```

**Output:** A5 labels with GHS pictograms in `output/` folder

---

## 📦 What's Included

### Version 2.2.0 (DoD/NATO) - WEB DASHBOARD ✨
- **NEW: Streamlit Web Dashboard** for easy label generation
  - Drag-and-drop CSV/Excel upload
  - Per-row label size selection (8 sizes)
  - Real-time label preview
  - Download as PNG, PDF, or ZIP
  - Dark/light mode toggle
- **Military specification labels** per MIL-STD-129
- **Field 12: Safety & Movement Markings** always displayed prominently
- **PDF and PNG output formats:**
  - PDF: A4 format (210mm × 297mm)
  - PNG: Multiple sizes (2"×1", 3"×2", 4"×2", 4"×3", 4"×4", 4"×6", A6, A5)
  - 600 DPI high-resolution output
  - Bleed margins with cut-line
- **4 barcode symbologies:**
  - Code 128 for Batch Lot No. (ISO/IEC 15417)
  - Code 39 for NIIN (ISO/IEC 16388)
  - Code 128 for Use by Date
  - GS1 Data Matrix ECC 200 (ISO/IEC 16022) with proper GS1 AI encoding
- **GS1 Data Matrix** with Application Identifiers:
  - AI 7001: Full NSN (13 digits, no hyphens)
  - AI 10: Batch/Lot number
  - AI 17: Expiry date (YYMMDD)
  - AI 21: Serial number (if applicable)
- **Date format:** DD MMM YYYY (e.g., "15 NOV 2027")
- **21-field data schema** with NSN/NIIN tracking
- **Products:** Fuchs OM-33, DCI 4A

### Version 1.0 (GHS)
- **Chemical hazard labels** per GHS Revision 7
- **GHS pictograms** (9 types)
- **Barcodes and QR codes** for traceability
- **A5 format** (148mm × 210mm)
- **Australian WHS compliant**

---

## 📁 Project Files

### DoD/NATO System (v2.2+)
```
dod_label_app.py                 # Streamlit web dashboard (NEW)
dod_label_generator.py           # CLI PDF label generator
dod_label_generator_png.py       # CLI PNG label generator (600 DPI)
sample_data_dod.csv              # Example: 2 products
verify_barcodes.py               # Barcode validation suite
requirements_web.txt             # Web dashboard dependencies
README_DOD.md                    # Complete documentation
.agent/system/dod-label-specification.md  # Technical spec
```

### GHS System (v1.0)
```
drum_label_generator.py          # Main generator (413 lines)
sample_data.csv                  # Example: 3 products
config.py                        # Configuration
test_installation.py             # Setup validation
ghs_pictograms/                  # 9 GHS PNG files
```

---

## 🔧 Installation

```bash
pip install -r requirements.txt
```

**Dependencies:**
- reportlab 4.0.7 - PDF generation
- pandas 2.1.4 - Data processing
- python-barcode 0.16.1 - Linear barcodes
- pylibdmtx 0.1.10 - Data Matrix (v2.0)
- qrcode 8.2 - QR codes
- Pillow 10.1.0 - Image processing
- openpyxl 3.1.2 - Excel support
- segno 1.6.6 - Additional barcodes (v2.0)

---

## 📋 Usage

### DoD Labels (v2.1+)

**Generate PDF labels:**
```bash
python dod_label_generator.py your_data.csv
```

**Generate PNG labels (high-resolution):**
```bash
# Default A5 size at 600 DPI
python dod_label_generator_png.py your_data.csv --size A5

# Available sizes: A5, A6, 4x6, 4x4, 3x2, A4
python dod_label_generator_png.py your_data.csv --size 4x6

# Generate all sizes at once
python dod_label_generator_png.py your_data.csv --all-sizes

# Custom DPI (default 600)
python dod_label_generator_png.py your_data.csv --dpi 300
```

**Verify barcodes:**
```bash
python verify_barcodes.py
```

**Required CSV columns:**
- `product_description`, `nato_stock_no`, `niin`
- `batch_lot_no`, `date_of_manufacture`, `shelf_life_months`

See [README_DOD.md](README_DOD.md) for all 21 fields.

---

### GHS Labels (v1.0)

**Generate labels:**
```bash
python drum_label_generator.py your_data.csv
# or
python drum_label_generator.py your_data.xlsx
```

**Required CSV columns:**
- `product_code`, `product_name`, `batch_number`

**Optional columns:**
- `supplier`, `net_weight`, `un_number`, `ghs_pictograms`
- `hazard_statements`, `precautionary_statements`, etc.

See full documentation in this file below.

---

## ✅ Compliance

### DoD/NATO (v2.0)
- MIL-STD-129: Military Marking for Shipment and Storage ✓
- NATO STANAG: Standardization Agreements ✓
- ISO/IEC 15417 (Code 128), 16388 (Code 39), 16022 (Data Matrix) ✓
- GS1 General Specifications ✓
- Print quality: Grade 1.0/0.5/660 ✓

### GHS (v1.0)
- GHS Revision 7 ✓
- WHS Regulations 2011 (Cth) ✓
- Australian Dangerous Goods Code (ADG) ✓
- UN dangerous goods classification ✓

---

## 🧪 Testing

### DoD Labels (v2.0)
```bash
python verify_barcodes.py
```
**Expected output:**
```
[OK] PASS  Field 7: Batch Lot Code 128
[OK] PASS  Field 16: NIIN Code 39
[OK] PASS  Field 20: Use by Date Code 128
[OK] PASS  Field 21: GS1 Data Matrix

Results: 4/4 tests passed
```

### GHS Labels (v1.0)
```bash
python test_installation.py
python drum_label_generator.py sample_data.csv
```

---

## 📊 Example Products

### DoD Labels (v2.0)

**Fuchs OM-33** [200kg Drum]
- NSN: 9150-66-035-7879
- NIIN: 660357879
- NATO Code: H-576
- Batch: FM251115A
- Spec: DEF STAN 91-39 Issue 4

**DCI 4A** [55 US GAL]
- NSN: 6850-99-224-5252
- NIIN: 992245252
- JSD Ref: AL-61
- Batch: DC251115B
- Hazmat: UN1307, Class 3, PG III

### GHS Labels (v1.0)

- **Trilene CP-1100** (GHS07, GHS09, UN3082)
- **Calcium Sulfonate** (GHS07)
- **PAO 4 Base Oil** (no pictograms)

---

## 📚 Documentation

- **[README_DOD.md](README_DOD.md)** - Complete DoD/NATO documentation (406 lines)
- **[CLAUDE.md](CLAUDE.md)** - AI agent documentation (v2.0)
- **[.agent/README.md](.agent/README.md)** - Documentation index
- **[.agent/system/dod-label-specification.md](.agent/system/dod-label-specification.md)** - Complete technical spec

---

## 🔄 Version History

### v2.1.1 (2025-11-21) - PNG Output Support
**Added high-resolution PNG label generation**

New Features:
- New `dod_label_generator_png.py` script for PNG output
- 600 DPI high-resolution output (configurable)
- Multiple label sizes: A5, A6, 4x6", 4x4", 3x2", A4
- 10mm bleed margins on all sides
- Dashed cut-line for print trimming
- Direct PIL/Pillow rendering (no external dependencies like poppler)
- Fixed NIIN/Batch Lot barcode overlap issue

Usage:
```bash
python dod_label_generator_png.py sample_data_dod.csv --size A5
python dod_label_generator_png.py sample_data_dod.csv --all-sizes
```

### v2.1.0 (2025-11-21) - GS1 Data Matrix Fix
**Corrected GS1 Data Matrix encoding per ISO/IEC 16022**

Fixed:
- NSN encoding now uses full 13-digit NSN (no hyphens) instead of constructed value
- Added FNC1/GS separators (ASCII 29) between variable-length AI fields
- Date format corrected to DD MMM YYYY for display fields (8, 13, 19)
- Proper handling of nan/empty values in all fields

GS1 Data Matrix now encodes:
```
7001{NSN_13digits}<GS>10{BatchLot}<GS>17{YYMMDD}
```

### v2.0.0 (2025-11-15) - Major Release
**Complete redesign for DoD/NATO military supply labels**

Added:
- 4 barcode symbologies (Code 128, Code 39, Data Matrix)
- 21-field data schema with NSN/NIIN integration
- MIL-STD-129 and ISO compliance
- A4 page format (210×297mm)
- Barcode verification suite
- GS1 Application Identifier support
- Complete technical documentation

Products:
- Fuchs OM-33 (NATO H-576)
- DCI 4A (JSD AL-61)

### v1.0.0 (2025-11-14) - Initial Release
- GHS chemical label system
- A5 labels with 9 GHS pictograms
- Australian WHS compliance
- Code 128 barcodes and QR codes

---

## 📞 Support

**Technical:** Mark Anderson, Valorem Chemicals Pty Ltd

**Compliance Resources:**
- GS1 Australia: www.gs1au.org
- ISO Standards: www.iso.org
- MIL-STD Documents: www.dla.mil
- UNECE GHS: https://unece.org/transport/standards/transport-dangerous-goods/ghs-pictograms

**GitHub:** https://github.com/Mark-Valorem/drum-label-generator.git

---

## GHS Label Details (v1.0)

### Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add GHS pictogram images**
   - Download from UNECE or use approved versions
   - Place in `ghs_pictograms/` folder
   - Required: GHS01.png through GHS09.png

3. **Prepare CSV with required columns:**
   - `product_code`, `product_name`, `batch_number`

4. **Generate labels**
   ```bash
   python drum_label_generator.py sample_data.csv
   ```

### Configuration

Edit `config.py` to customize:

**Company details:**
```python
COMPANY_NAME = "Valorem Chemicals Pty Ltd"
COMPANY_ADDRESS = "Sydney, NSW, Australia"
COMPANY_PHONE = "+61 (0)2 XXXX XXXX"
```

**Layout dimensions:**
- Page size: A5 (148mm × 210mm)
- Margins, row heights, font sizes
- Pictogram size: 20mm
- Barcode height: 15mm
- QR size: 25mm

### Data Format

**Hazard statements** (pipe-separated):
```
H315: Skin irritation|H319: Eye irritation|H411: Aquatic toxicity
```

**GHS pictograms** (comma-separated):
```
GHS02,GHS07,GHS09
```

**Dates:** DD/MM/YYYY

### Troubleshooting

- **"GHS pictogram not found"**: Check PNG files in `ghs_pictograms/`
- **"Missing required columns"**: Ensure CSV has `product_code`, `product_name`, `batch_number`
- **Barcode errors**: Use alphanumeric characters only
- **Layout issues**: Adjust settings in `config.py`

---

## 📄 License

Internal use for Valorem Chemicals Pty Ltd.

---

**Built for Valorem Chemicals Pty Ltd**
Supporting both military supply chain and chemical hazard labeling
