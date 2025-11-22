# Technical Stack Documentation
**Version:** 2.2.0
**Last Updated:** 2025-11-22
**Project:** DoD/NATO Military Label Generator

---

## Runtime Environment

**Python Version:** 3.x (3.8+)
**Platform:** Cross-platform (Windows, macOS, Linux)
**Deployment:** Local CLI tools + Streamlit web dashboard

---

## Core Dependencies

### PDF Generation
```
reportlab==4.0.7
```
- **Purpose:** PDF label generation with ReportLab Canvas API
- **Usage:** `dod_label_generator.py`, `drum_label_generator.py`
- **Pattern:** Direct canvas manipulation with coordinate-based layout
- **Output:** A4 (210×297mm) and A5 (148×210mm) PDF documents
- **Features:** Text rendering, image embedding, table layouts

### Image Processing & PNG Generation
```
Pillow==10.1.0
```
- **Purpose:** High-resolution PNG label rendering
- **Usage:** `dod_label_generator_png.py`, `dod_label_app.py`
- **Pattern:** PIL ImageDraw API for pixel-perfect rendering at 600 DPI
- **Critical:** Mission-critical barcode scannability requires precise pixel control
- **Features:**
  - Direct pixel manipulation (`ImageDraw.rectangle()`, `ImageDraw.text()`)
  - TrueType font rendering
  - Image compositing (paste barcode images onto canvas)
  - DPI metadata embedding
  - Multiple label sizes (2"×1" through A4)

**Why PIL/Pillow over HTML/CSS + Playwright:**
1. **Barcode Precision:** No browser anti-aliasing that could degrade barcode scannability
2. **Pixel-Perfect Control:** Exact positioning at 600 DPI for ISO compliance
3. **Zero Browser Overhead:** No Chromium (300MB), faster rendering
4. **Production-Proven:** v2.2.0 with 600 DPI scannable barcodes in production
5. **Deterministic Output:** Same input always produces identical pixels

### Data Processing
```
pandas==2.1.4
openpyxl==3.1.2
```
- **Purpose:** CSV/Excel data import and manipulation
- **Usage:** All generator scripts
- **Features:**
  - CSV parsing (`pd.read_csv()`)
  - Excel support (`.xlsx` via openpyxl)
  - Data validation and cleaning
  - Batch label generation

### Barcode Generation (DoD v2.x + GHS v1.0)

#### Linear Barcodes
```
python-barcode==0.16.1
```
- **Symbologies:**
  - Code 128 (Field 7: Batch Lot Number) - ISO/IEC 15417
  - Code 39 (Field 16: NIIN) - ISO/IEC 16388
  - Code 128/GS1-128 (Field 20: Use by Date)
- **Output:** PNG images at configurable DPI
- **Features:** Quiet zones, human-readable text, checksum validation

#### 2D Barcodes
```
pylibdmtx==0.1.10  # Data Matrix
qrcode==8.2        # QR Code (v1.0 GHS only)
segno==1.6.6       # Additional barcode support
```
- **Data Matrix (Field 21):**
  - GS1 Data Matrix ECC 200 - ISO/IEC 16022
  - FNC1 separator character (ASCII 29)
  - Application Identifiers: AI 7001 (NSN), AI 10 (Batch), AI 17 (Expiry), AI 21 (Serial)
  - **Critical:** Print quality grade 1.0/0.5/660 per ISO/IEC 15415
- **QR Code:**
  - Used in v1.0 GHS chemical labels only
  - Not used in DoD/NATO labels

### Web Dashboard (v2.2.0+)
```
streamlit>=1.28.0
```
- **Purpose:** Browser-based label generation interface
- **File:** `dod_label_app.py`
- **Features:**
  - Drag-and-drop file upload (CSV/Excel)
  - Editable data table with per-row label size selection
  - Real-time PNG preview
  - Download options: PNG, PDF, ZIP archive
  - Checkbox: Save to output folders
  - Dark/light mode support
- **Deployment:** `streamlit run dod_label_app.py` (localhost:8501)
- **Launcher:** `Start_Label_Dashboard.vbs` (Windows)

---

## Rendering Architecture

### Dual Rendering Strategy

**Why Two Rendering Engines?**
- **ReportLab (PDF):** Industry standard for print-ready PDF documents
- **PIL/Pillow (PNG):** Pixel-perfect rendering for digital use, proofing, web display

### ReportLab Canvas Rendering (PDF)

**Files:** `dod_label_generator.py`, `drum_label_generator.py`

**Pattern:**
```python
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

c = canvas.Canvas(output_path, pagesize=A4)
c.setFont('Helvetica-Bold', 14)
c.drawString(x * mm, y * mm, text)
c.drawImage(barcode_path, x * mm, y * mm, width=50*mm, height=15*mm)
c.save()
```

**Characteristics:**
- Coordinate system: Millimeters converted to points (72 DPI)
- Origin: Bottom-left corner (PDF standard)
- Font handling: ReportLab font registry
- Output: Vector PDF (scalable, print-ready)

### PIL ImageDraw Rendering (PNG)

**Files:** `dod_label_generator_png.py`, `dod_label_app.py`

**Pattern:**
```python
from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGB', (width_px, height_px), 'white')
draw = ImageDraw.Draw(img)
draw.rectangle([x1, y1, x2, y2], outline='black', width=2)
draw.text((x, y), text, fill='black', font=font)
img.paste(barcode_img, (x, y))
img.save(output_path, 'PNG', dpi=(600, 600))
```

**Characteristics:**
- Coordinate system: Pixels at 600 DPI
- Origin: Top-left corner
- Font handling: TrueType fonts via `ImageFont.truetype()`
- Output: Raster PNG (600 DPI, with DPI metadata)
- Critical conversion: `mm_to_px()` function (line 54 in png generator)

### DPI Conversion Formula

```python
def mm_to_px(mm_val, dpi=600):
    """Convert millimeters to pixels at given DPI"""
    return int(mm_val * dpi / 25.4)
```

**Example:**
- 10mm at 600 DPI = `10 * 600 / 25.4` = 236 pixels
- 210mm (A4 width) at 600 DPI = 4961 pixels

---

## Label Sizes Configuration

### Supported Sizes (v2.1+)

| Size Name | Dimensions (mm) | Use Case |
|-----------|-----------------|----------|
| 2" × 1" | 50.8 × 25.4 | Small product labels |
| 3" × 2" | 76.2 × 50.8 | Medium product labels |
| 4" × 2" | 101.6 × 50.8 | Standard shipping labels |
| 4" × 3" | 101.6 × 76.2 | Expanded information |
| 4" × 4" | 101.6 × 101.6 | Square labels |
| **4" × 6"** (default) | 101.6 × 152.4 | **Standard DoD label** |
| A6 | 105 × 148 | European small format |
| A5 | 148 × 210 | European standard format |
| A4 | 210 × 297 | Full-page labels |

**Configuration Location:** `dod_label_app.py` lines 38-47, `dod_label_generator_png.py` lines 32-41

---

## Barcode Technology Stack

### Code 128 (Batch Lot Number - Field 7)

**Standard:** ISO/IEC 15417
**Library:** python-barcode
**Pattern:** `BATCH123456`
**Features:**
- High-density linear barcode
- Full ASCII character set
- Automatic checksum
- Quiet zones (10× module width)

**Generation:**
```python
from barcode import Code128
from barcode.writer import ImageWriter

code128 = Code128(batch_lot_no, writer=ImageWriter())
filename = code128.save(f'barcode_code128_{batch_lot_no}')
```

### Code 39 (NIIN - Field 16)

**Standard:** ISO/IEC 16388
**Library:** python-barcode
**Pattern:** `660357879` (9 digits, extracted from NSN)
**Features:**
- Alphanumeric support
- Self-checking (no mandatory checksum)
- Wide adoption in military/government
- Larger quiet zones (10× narrow bar width)

**NIIN Extraction:**
```python
# NSN format: 9150-66-035-7879 (13 digits)
# NIIN: Last 9 digits → 660357879
niin = nsn.replace('-', '')[-9:]
```

### Code 128 (Use by Date - Field 20)

**Standard:** GS1-128
**Library:** python-barcode
**Pattern:** `YYMMDD` (e.g., `271115` for 15 Nov 2027)
**Features:**
- Date encoding in YYMMDD format
- GS1 Application Identifier (AI) compatible
- Expiry date calculation from manufacturing date + shelf life

**Date Calculation:**
```python
from datetime import datetime, timedelta

mfg_date = datetime.strptime('15/11/2025', '%d/%m/%Y')
shelf_life_months = 24
expiry_date = mfg_date + timedelta(days=shelf_life_months * 30)
date_code = expiry_date.strftime('%y%m%d')  # → '271115'
```

### GS1 Data Matrix ECC 200 (Field 21)

**Standard:** ISO/IEC 16022
**Library:** pylibdmtx
**Pattern:** `[FNC1]7001<NSN>[GS]10<BATCH>[GS]17<EXPIRY>[GS]21<SERIAL>`

**Critical Encoding:**
- **FNC1:** ASCII 29 (0x1D) - GS1 separator character
- **GS (Group Separator):** ASCII 29 (0x1D)
- **AI 7001:** NATO Stock Number (NSN) - 13 digits
- **AI 10:** Batch/Lot Number - alphanumeric
- **AI 17:** Expiry date (YYMMDD)
- **AI 21:** Serial number - alphanumeric

**Generation Example:**
```python
from pylibdmtx.pylibdmtx import encode

# Build GS1 Data Matrix string with separators
gs = chr(29)  # GS1 separator (FNC1/GS)
data = f"{gs}7001{nsn}{gs}10{batch}{gs}17{expiry_yymmdd}{gs}21{serial}"

encoded = encode(data.encode('utf-8'))
img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
```

**Print Quality Requirements:**
- **Minimum Grade:** 1.0 (ISO/IEC 15415)
- **Aperture:** 0.5 (5 mils)
- **Wavelength:** 660 nm (red laser)
- **Verification:** GS1 Australia testing mandatory

---

## Compliance Standards

### Military Specifications
- **MIL-STD-129:** Military Marking for Shipment and Storage
- **NATO STANAG:** Standardization Agreements
- **MIL-STD-130:** Identification Marking of U.S. Military Property

### Barcode Standards
- **ISO/IEC 15417:** Code 128
- **ISO/IEC 16388:** Code 39
- **ISO/IEC 16022:** Data Matrix
- **ISO/IEC 15416:** Linear barcode print quality (grade 1.0)
- **ISO/IEC 15415:** 2D barcode print quality (grade 1.0/0.5/660)

### GS1 Standards
- **GS1 General Specifications:** Application Identifiers (AI)
- **GS1 Data Matrix Guideline**
- **GS1 Australia:** Regional compliance body

### Australian Standards (v1.0 GHS)
- **WHS Regulations 2011 (Cth):** Workplace Health and Safety
- **GHS Revision 7:** Globally Harmonized System
- **ADG Code:** Australian Dangerous Goods Code

---

## File Structure

### Core Generators
- `dod_label_generator.py` - PDF generator (ReportLab, v2.0)
- `dod_label_generator_png.py` - PNG generator (PIL, v2.1)
- `dod_label_app.py` - Streamlit web dashboard (v2.2)
- `drum_label_generator.py` - GHS chemical labels (v1.0)

### Configuration
- `config.py` - v1.0 GHS label settings
- `requirements.txt` - Core dependencies
- `requirements_web.txt` - Streamlit dependencies

### Testing & Validation
- `verify_barcodes.py` - Barcode ISO compliance testing
- `test_installation.py` - Environment validation

---

## Development Workflow

### CLI Usage
```bash
# Generate DoD PDF labels (v2.0)
python dod_label_generator.py sample_data_dod.csv

# Generate DoD PNG labels (v2.1)
python dod_label_generator_png.py sample_data_dod.csv --size A5
python dod_label_generator_png.py sample_data_dod.csv --all-sizes

# Generate GHS chemical labels (v1.0)
python drum_label_generator.py sample_data.csv

# Verify barcode quality (v2.0+)
python verify_barcodes.py
```

### Web Dashboard Usage
```bash
# Start Streamlit dashboard
streamlit run dod_label_app.py

# Or use Windows launcher
Start_Label_Dashboard.vbs
```

**Dashboard URL:** http://localhost:8501

---

## Output Directories

```
output/
├── .gitkeep              # Preserve empty folder in git
├── *.pdf                 # PDF labels (git ignored)
└── png/                  # PNG labels (git ignored)
    ├── label_1_*.png
    ├── label_2_*.png
    └── ...
```

**File Naming Convention:**
- PDF: `dod_label_{product}_{batch}_{timestamp}.pdf`
- PNG: `dod_label_{product}_{batch}_{size}_{timestamp}.png`

---

## Performance Characteristics

### Rendering Speed (Approximate)

| Renderer | Single Label | 50 Labels | Notes |
|----------|--------------|-----------|-------|
| ReportLab PDF | ~0.5s | ~25s | Fast, vector output |
| PIL PNG (600 DPI) | ~1.5s | ~75s | Slower, raster output |
| Streamlit Web | +0.2s overhead | - | Browser rendering |

### Memory Usage

| Operation | Peak Memory | Notes |
|-----------|-------------|-------|
| Single PDF | ~50 MB | ReportLab canvas |
| Single PNG (A4, 600 DPI) | ~120 MB | 4961×7016 pixels = 35M pixels |
| Batch 50 labels | ~150 MB | Sequential processing |
| Streamlit app | ~200 MB | Flask server + caching |

---

## Dependency Rationale

### Why ReportLab?
- Industry standard for PDF generation
- Precise vector graphics
- Print-ready output
- Cross-platform fonts

### Why PIL/Pillow?
- **Mission-critical:** Barcode scannability requires pixel-perfect control
- No browser anti-aliasing (unlike HTML/Playwright approach)
- Direct DPI metadata embedding
- Lightweight (no 300MB Chromium dependency)
- Production-proven at 600 DPI

### Why NOT HTML/CSS + Playwright?
- **Barcode Risk:** Browser screenshot anti-aliasing could degrade ISO compliance
- **Overhead:** 300MB Chromium installation
- **Performance:** Slower than native PIL rendering
- **Complexity:** CSS debugging, browser version dependencies
- **Determinism:** Same input may produce slightly different outputs across browser versions

### Why Streamlit?
- Rapid web UI development
- Python-native (no JavaScript)
- Built-in file upload/download
- Editable data tables
- Real-time preview

---

## Future Considerations

### Potential Enhancements (NOT APPROVED)
- PostgreSQL backend for label history
- REST API for remote generation
- Multi-language support (NATO)
- QR code alternative to Data Matrix (ISO/IEC 18004)

### Explicitly Rejected
- ❌ HTML/CSS + Playwright rendering (barcode risk)
- ❌ Lower DPI output (<600) (print quality risk)
- ❌ Web fonts (determinism risk)

---

## Version History

| Version | Date | Rendering Stack | Notes |
|---------|------|----------------|-------|
| v1.0.0 | 2025-11-14 | ReportLab only | GHS chemical labels |
| v2.0.0 | 2025-11-15 | ReportLab + 4 barcodes | DoD/NATO PDF labels |
| v2.1.0 | 2025-11-21 | Added PIL PNG generator | Multi-size PNG output |
| v2.2.0 | 2025-11-21 | Added Streamlit web UI | Web dashboard |

---

**For PIL Rendering Maintenance, see:** `.claude_docs/MEMORY.md`
**For Visual Specifications, see:** `.claude_docs/PROJECT_BRIEF.md`
**For Architecture Decisions, see:** `.claude_docs/DECISIONS.md`
