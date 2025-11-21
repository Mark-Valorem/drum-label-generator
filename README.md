# Label Generator for Valorem Chemicals

**v2.0: DoD/NATO Military Labels | v1.0: GHS Chemical Labels**

This project generates print-ready PDF labels for Valorem Chemicals Pty Ltd, supporting both military supply chain and chemical hazard labeling requirements.

---

## 🚀 Quick Start

### DoD/NATO Military Labels (v2.0) - NEW

```bash
# Install dependencies
pip install -r requirements.txt

# Generate labels for both products
python dod_label_generator.py sample_data_dod.csv

# Verify all 4 barcode types
python verify_barcodes.py
```

**Output:** A4 labels with 4 barcode types in `output/` folder

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

### Version 2.0 (DoD/NATO) - NEW ✨
- **Military specification labels** per MIL-STD-129
- **4 barcode symbologies:**
  - Code 128 for Batch Lot No. (ISO/IEC 15417)
  - Code 39 for NIIN (ISO/IEC 16388)
  - Code 128 for Use by Date
  - GS1 Data Matrix ECC 200 (ISO/IEC 16022)
- **21-field data schema** with NSN/NIIN tracking
- **A4 format** (210mm × 297mm)
- **Products:** Fuchs OM-33, DCI 4A

### Version 1.0 (GHS)
- **Chemical hazard labels** per GHS Revision 7
- **GHS pictograms** (9 types)
- **Barcodes and QR codes** for traceability
- **A5 format** (148mm × 210mm)
- **Australian WHS compliant**

---

## 📁 Project Files

### DoD/NATO System (v2.0)
```
dod_label_generator.py           # Main generator (454 lines)
sample_data_dod.csv              # Example: 2 products
verify_barcodes.py               # Barcode validation suite
README_DOD.md                    # Complete documentation
.agent/system/dod-label-specification.md  # Technical spec (322 lines)
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

### DoD Labels (v2.0)

**Generate labels:**
```bash
python dod_label_generator.py your_data.csv
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
