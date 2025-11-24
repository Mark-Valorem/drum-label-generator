# Project Memory & Context
**Version:** 2.2.0
**Last Updated:** 2025-11-22
**Project:** DoD/NATO Military Label Generator

---

## Project Evolution History

### v1.0 (2025-11-14) - GHS Chemical Labels
**Purpose:** Hazardous chemical labeling for Australian WHS compliance
**Technology:** ReportLab PDF generator
**Format:** A5 (148×210mm) labels
**Features:**
- GHS pictogram display (GHS01-GHS09)
- Hazard statements and precautionary statements
- QR code for product information
- UN dangerous goods classification
**Status:** Legacy, maintained for existing users

### v2.0 (2025-11-15) - DoD/NATO PDF Labels
**Purpose:** Military supply chain compliance
**Technology:** ReportLab Canvas API
**Format:** A4 (210×297mm) labels
**Major Changes:**
- Complete redesign from GHS to military specification
- 21-field data model (NATO/DoD requirements)
- 4 barcode symbologies:
  - Code 128 (Batch Lot - Field 7)
  - Code 39 (NIIN - Field 16)
  - Code 128/GS1-128 (Use by Date - Field 20)
  - GS1 Data Matrix ECC 200 (Comprehensive - Field 21)
- NSN/NIIN tracking
- MIL-STD-129 compliance
- GS1 Application Identifier encoding
**Files Created:**
- `dod_label_generator.py`
- `sample_data_dod.csv`
- `verify_barcodes.py`
- `.agent/system/dod-label-specification.md`

### v2.1 (2025-11-21) - PNG Multi-Size Generator
**Purpose:** Digital label generation with multiple sizes
**Technology:** PIL/Pillow ImageDraw (600 DPI)
**Format:** 8 label sizes (2"×1" through A4)
**Major Changes:**
- New PNG generator separate from PDF
- High-resolution raster rendering (600 DPI)
- Multiple label size support
- Bleed margins (5mm) with cut-lines
- Fixed Field 12 bug (always display with header box)
- Dynamic font scaling based on label size
**Files Created:**
- `dod_label_generator_png.py`
- `output/png/` directory
**Critical Decision:** Use PIL/Pillow for pixel-perfect barcode rendering (not HTML/Playwright)

### v2.2 (2025-11-21) - Streamlit Web Dashboard
**Purpose:** Browser-based label generation UI
**Technology:** Streamlit + PIL/Pillow
**Features:**
- Drag-and-drop CSV/Excel upload
- Editable data table (`st.data_editor`)
- Per-row label size selection (dropdown)
- Real-time PNG preview
- Download options: PNG ZIP, PDF ZIP, Combined ZIP
- Save to output/ folder (checkbox, default ON)
- Dark/light mode support
**Files Created:**
- `dod_label_app.py`
- `requirements_web.txt`
- `Start_Label_Dashboard.vbs` (Windows launcher)

### v2.2.1 (2025-11-22) - Gold Standard Architecture
**Purpose:** Refactor to Memory Bank + version control hygiene
**Changes:**
- Created `.claudeignore` (block output files from Claude indexing)
- Updated `.gitignore` (add `output/png/`, `.streamlit/`, `*.pyc`)
- Created `.claude_docs/` Memory Bank structure
- Documentation: TECH_STACK.md, PROJECT_BRIEF.md, MEMORY.md, PROGRESS.md, DECISIONS.md
- Updated CLAUDE.md with Memory Bank index
- Synced .agent/ documentation to v2.2.0
**Architecture Decision:** ADR-004 - Reject HTML/Playwright approach (barcode risk)

---

## Key Architectural Decisions

### ADR-001: PIL/Pillow for PNG Rendering (2025-11-15)
**Decision:** Use PIL ImageDraw for PNG label generation
**Rationale:**
- Pixel-perfect control at 600 DPI
- No browser anti-aliasing (critical for barcode scannability)
- Lightweight (no 300MB Chromium dependency)
- Deterministic output (same input = identical pixels)
- Production-proven for ISO barcode compliance
**Alternatives Considered:**
- HTML/CSS + Playwright: Rejected due to barcode anti-aliasing risk
- Cairo/Pycairo: Less mature Python bindings
- ImageMagick: Subprocess overhead
**Status:** Active, core rendering strategy

### ADR-002: Dual Rendering Strategy (2025-11-15)
**Decision:** Maintain both ReportLab (PDF) and PIL (PNG) generators
**Rationale:**
- PDF: Print-ready vector format (industry standard)
- PNG: Digital use, proofing, web display, precise barcode control
- Different use cases justify separate implementations
- Shared data model and barcode generation logic
**Status:** Active

### ADR-003: 600 DPI Standard (2025-11-15)
**Decision:** All PNG labels rendered at 600 DPI minimum
**Rationale:**
- ISO/IEC barcode print quality requires high resolution
- 600 DPI achieves grade 1.5-2.0 (exceeds min grade 1.0)
- Laser printer native resolution
- Ensures scannable barcodes in harsh field conditions
**Trade-offs:**
- Larger file sizes (~2-10 MB per PNG)
- Slower rendering (~1.5s vs 0.5s for PDF)
**Alternatives Considered:**
- 300 DPI: Risk of barcode compliance failure
- 1200 DPI: Diminishing returns, 4× file size
**Status:** Active, non-negotiable

### ADR-004: Reject HTML/Playwright Approach (2025-11-22)
**Decision:** Do NOT migrate to HTML/CSS + Playwright screenshot rendering
**Rationale:**
- **Mission-Critical Risk:** Browser anti-aliasing could degrade barcode scannability below ISO grade 1.0
- **Current Solution Works:** PIL/Pillow proven at 600 DPI with 100% scan rate
- **Complexity:** Adds 300MB Chromium, browser version dependencies, CSS debugging
- **Performance:** Slower than native PIL rendering
- **Determinism:** Browser rendering may vary across versions/platforms
**Context:**
- User initially requested HTML/CSS approach for "easier editing"
- Gap analysis revealed NO HTML/CSS in codebase (pure Python rendering)
- User decision: "Risk of barcode issues too high, keep PIL rendering"
**Alternative:** Document PIL rendering internals for safe future edits (this file)
**Status:** Active, explicitly rejected

### ADR-005: Field 12 Always Display (2025-11-21)
**Decision:** Field 12 (Safety & Movement Markings) must always display with header box
**Rationale:**
- User reported bug: Field 12 was missing in v2.1
- Military specification requires visible field even if empty
- Visual consistency across all labels
**Implementation:**
- Header box: RGB(240,240,240) light gray background
- Header text: "Field 12: Safety & Movement Markings"
- Content: Display value or "-" if empty
**Status:** Active, enforced in v2.1+

---

## Critical Context & Knowledge

### NSN/NIIN Extraction Logic
**NATO Stock Number (NSN):** 13-digit format `nnnn-nn-nnn-nnnn`
**National Item Identification Number (NIIN):** Last 9 digits of NSN

**Example:**
- NSN: `9150-66-035-7879`
- NIIN: `660357879` (without hyphens)

**Code:**
```python
nsn = row.get('nato_stock_no', '')
niin = nsn.replace('-', '')[-9:]  # Extract last 9 digits
```

**Usage:**
- Field 11: Display NSN with hyphens
- Field 15: Display NIIN (9 digits)
- Field 16: Code 39 barcode of NIIN
- Field 21: Data Matrix uses NSN without hyphens

### GS1 Data Matrix Encoding
**Critical Separator:** FNC1 character = ASCII 29 (0x1D)

**Structure:**
```
[FNC1][AI][DATA][GS][AI][DATA][GS][AI][DATA]...
```

**Example:**
```python
gs = chr(29)  # Group Separator / FNC1
nsn_no_hyphens = '9150660357879'
batch = 'FM251115A'
expiry_yymmdd = '271115'  # 15 Nov 2027
serial = 'SN123456'

data = f"{gs}7001{nsn_no_hyphens}{gs}10{batch}{gs}17{expiry_yymmdd}{gs}21{serial}"
# Result: \x1D70019150660357879\x1D10FM251115A\x1D17271115\x1D21SN123456
```

**GS1 Application Identifiers:**
- `7001`: NSN (13 digits, n13)
- `10`: Batch/Lot Number (alphanumeric, an..20)
- `17`: Expiry Date (YYMMDD, n6)
- `21`: Serial Number (alphanumeric, an..20)

**Compliance:**
- Must submit samples to GS1 Australia for testing
- Verify per ISO/IEC 15415
- Minimum grade 1.0/0.5/660

### Date Calculations
**Shelf Life Calculation:**
```python
from datetime import datetime, timedelta

# Input
mfg_date_str = '15/11/2025'  # DD/MM/YYYY
shelf_life_months = 36

# Parse
mfg_date = datetime.strptime(mfg_date_str, '%d/%m/%Y')

# Calculate expiry (approximation: 30 days per month)
expiry_date = mfg_date + timedelta(days=shelf_life_months * 30)

# Format for display
display_format = expiry_date.strftime('%d %b %Y').upper()  # "15 NOV 2027"

# Format for barcodes
barcode_format = expiry_date.strftime('%y%m%d')  # "271115"
```

**Used In:**
- Field 13: Re-Test Date (display format)
- Field 19: Use by Date (display format)
- Field 20: Use by Date Barcode (YYMMDD)
- Field 21: Data Matrix AI 17 (YYMMDD)

### NaN/Null Handling
**Problem:** Pandas reads empty cells as `NaN`, which displays as "nan" string
**Solution:** Safe string conversion
```python
def safe_str(value, default='-'):
    """Convert value to string, handling NaN/None"""
    if pd.isna(value) or value is None or value == '':
        return default
    return str(value)

# Usage
safety_markings = safe_str(row.get('safety_movement_markings'), '-')
test_report = safe_str(row.get('test_report_no'), '-')
```

**Critical Fields:**
- Field 1: NATO Code (default: '-')
- Field 12: Safety Markings (default: '-')
- Field 14: Test Report No (default: '-')
- Field 18: Hazmat Code (default: '-')

---

## PIL/Pillow Rendering Maintenance Plan

### Overview
This section documents the internals of `dod_label_generator_png.py` and `dod_label_app.py` PIL rendering to enable safe future modifications without breaking barcode scannability.

---

### 1. How PIL Rendering Works

#### Image Canvas Creation
```python
from PIL import Image, ImageDraw, ImageFont

# Calculate dimensions
total_width_px = mm_to_px(total_width_mm, dpi=600)
total_height_px = mm_to_px(total_height_mm, dpi=600)

# Create white canvas
img = Image.new('RGB', (total_width_px, total_height_px), 'white')
draw = ImageDraw.Draw(img)
```

**Key Function:** `mm_to_px()` (line 17)
```python
def mm_to_px(mm_val, dpi=600):
    """Convert millimeters to pixels at given DPI"""
    return int(mm_val * dpi / 25.4)
```

**Example:**
- 10mm at 600 DPI = `10 * 600 / 25.4` = 236 pixels
- A4 width 210mm = `210 * 600 / 25.4` = 4961 pixels

#### Drawing Primitives
```python
# Rectangle
draw.rectangle([x1, y1, x2, y2], fill='white', outline='black', width=2)

# Text
draw.text((x, y), "Sample Text", fill='black', font=font_obj)

# Line
draw.line([(x1, y1), (x2, y2)], fill='black', width=1)
```

#### Barcode Integration
Barcodes are generated as separate PIL Image objects, then pasted onto the main canvas:
```python
# Generate barcode (returns PIL Image)
barcode_img = self.generate_code128(batch_lot_no)

# Resize if needed
new_width = mm_to_px(50, self.dpi)
aspect = barcode_img.width / barcode_img.height
new_height = int(new_width / aspect)
barcode_resized = barcode_img.resize((new_width, new_height), Image.LANCZOS)

# Paste onto main canvas
img.paste(barcode_resized, (x_left, y_pos))
```

**Critical:** Use `Image.LANCZOS` for linear barcodes (smooth edges), `Image.NEAREST` for Data Matrix (preserve sharp pixels)

#### Font Rendering
```python
# Load TrueType font
font_path = "C:/Windows/Fonts/arial.ttf"  # Or system equivalent
font = ImageFont.truetype(font_path, size_in_pixels)

# Fallback to default
try:
    font = ImageFont.truetype(font_path, size)
except:
    font = ImageFont.load_default()
```

**Font Scaling:** (lines 76-84)
```python
# Scale relative to label size (A5 reference: 148×210mm)
scale = min(label_width_mm / 148, label_height_mm / 210)
scale = max(0.4, min(scale, 1.5))  # Clamp to 0.4× - 1.5×

# Scale for DPI (72 DPI = standard)
base_scale = dpi / 72

# Final font sizes
FONT_SIZE_LARGE = int(20 * scale * base_scale)
FONT_SIZE_HEADER = int(14 * scale * base_scale)
FONT_SIZE_BODY = int(11 * scale * base_scale)
FONT_SIZE_SMALL = int(8 * scale * base_scale)
```

**Example for 4"×6" label at 600 DPI:**
- Label: 101.6×152.4mm
- Scale: `min(101.6/148, 152.4/210)` = `min(0.686, 0.726)` = 0.686
- Base scale: `600/72` = 8.33
- FONT_SIZE_LARGE: `20 * 0.686 * 8.33` ≈ 114 pixels

#### Saving with DPI Metadata
```python
# Save PNG with embedded DPI
img.save(output_path, 'PNG', dpi=(600, 600))
```

**Critical:** DPI metadata ensures correct scaling when printed

---

### 2. Critical Code Sections (DO NOT BREAK)

#### Section 1: DPI Conversion (Line 17)
**File:** `dod_label_generator_png.py`
**Function:** `mm_to_px()`
**Why Critical:** All layout calculations depend on this formula
**Safe to Modify:** NO - formula is mathematically exact
**Testing:** If modified, verify with: `mm_to_px(25.4, 600) == 600` (1 inch = 25.4mm = 600 pixels at 600 DPI)

#### Section 2: Font Scaling (Lines 76-84)
**File:** `dod_label_generator_png.py`
**Class:** `DoDLabelGenerator.__init__()`
**Why Critical:** Incorrect scaling breaks text readability on small labels
**Safe to Modify:** Carefully - test all 8 label sizes
**Testing Checklist:**
- [ ] 2"×1": Text not clipped
- [ ] 4"×6": Standard reference size
- [ ] A4: Text not oversized

#### Section 3: Barcode Positioning (Lines 320-410)
**File:** `dod_label_generator_png.py`
**Function:** `create_label_png()`
**Why Critical:** Incorrect positioning breaks barcode scannability
**Specific Lines:**
- Line 337: `img.paste(niin_barcode_resized, (x_left, y_pos))` - NIIN Code 39
- Line 356: `img.paste(dm_resized, (dm_x, y_pos))` - Data Matrix
- Line 393: `img.paste(batch_resized, (x_left, y_pos))` - Batch Code 128
- Line 406: `img.paste(use_by_resized, (use_by_x, y_pos))` - Date Code 128

**Safe to Modify:** Position coordinates only - DO NOT change resize algorithms
**Resize Algorithms:**
- Linear barcodes: `Image.LANCZOS` (smooth edges, anti-aliasing OK)
- Data Matrix: `Image.NEAREST` (preserve sharp pixel boundaries)

**Testing After Modification:**
1. Generate test label
2. Run `verify_barcodes.py`
3. Scan with physical barcode scanner
4. Verify ISO grade ≥ 1.0

#### Section 4: GS1 Data Matrix Encoding (Lines 212-249)
**File:** `dod_label_generator_png.py`
**Function:** `generate_datamatrix()`
**Why Critical:** FNC1 separator (ASCII 29) is mandatory for GS1 compliance
**Key Lines:**
```python
gs = chr(29)  # Line 217 - GS1 separator
data = f"{gs}7001{nsn_clean}{gs}10{batch}{gs}17{expiry_yymmdd}{gs}21{serial}"
```

**Safe to Modify:** Add/remove AI fields only - DO NOT change separator character
**GS1 Compliance:** Submit any changes to GS1 Australia for re-testing

#### Section 5: Field 12 Header Box (Lines 433-445)
**File:** `dod_label_generator_png.py` (approximate, varies by layout refactoring)
**Why Critical:** User requirement - must always display even if empty
**Implementation:**
```python
# Header box
safety_header_height = FONT_SIZE_SMALL + mm_to_px(2, dpi)
draw.rectangle([x_left - 3, y_pos, x_right + 3, y_pos + safety_header_height],
               fill=(240, 240, 240), outline='black', width=1)

# Header text
draw.text((x_left, y_pos + mm_to_px(0.5, dpi)),
          "Field 12: Safety & Movement Markings", fill='black', font=font_small)

# Content (below header)
safety_markings = safe_str(row.get('safety_movement_markings'), '-')
draw.text((x_left, y_pos + safety_header_height), safety_markings, ...)
```

**Safe to Modify:** Styling only - MUST keep header box visible
**Testing:** Generate label with empty Field 12, verify header displays

---

### 3. Safe Editing Guidelines

#### Before Making Changes
1. **Read this file first** - understand critical sections
2. **Create git branch** - `git checkout -b fix/label-layout-adjust`
3. **Backup current output** - save working labels for comparison
4. **Document intent** - what are you trying to change and why?

#### During Editing
1. **Use `mm_to_px()` everywhere** - never hardcode pixel values
   ```python
   # BAD
   x_offset = 500  # Hardcoded pixels

   # GOOD
   x_offset = mm_to_px(20, self.dpi)  # 20mm offset
   ```

2. **Preserve barcode dimensions**
   ```python
   # BAD
   barcode_width = 200  # Might break at different DPI

   # GOOD
   barcode_width_mm = 50  # Millimeters (spec requirement)
   barcode_width_px = mm_to_px(barcode_width_mm, self.dpi)
   ```

3. **Test incrementally** - generate label after each change
4. **Keep same coordinate system** - (0,0) = top-left, y increases downward

#### After Editing
1. **Run barcode verification:**
   ```bash
   python verify_barcodes.py
   ```

2. **Test all label sizes:**
   ```bash
   python dod_label_generator_png.py sample_data_dod.csv --all-sizes
   ```

3. **Visual inspection checklist:**
   - [ ] No text clipping/overflow
   - [ ] Barcodes have quiet zones
   - [ ] Field 12 header box displays
   - [ ] All 21 fields present
   - [ ] NSN/NIIN match (last 9 digits)
   - [ ] Dates formatted correctly (DD MMM YYYY)

4. **Physical barcode scanning:**
   - Print label at 600 DPI (laser printer)
   - Scan each barcode with handheld scanner
   - Verify 100% scan rate

5. **Performance check:**
   ```bash
   time python dod_label_generator_png.py sample_data_dod.csv
   ```
   - Should complete in <2s per label
   - If >5s, investigate rendering bottleneck

---

### 4. Layout Calculation Reference Map

#### File: `dod_label_generator_png.py`
**Coordinate System:** (0,0) = top-left, x increases right, y increases down

```
Bleed Area (5mm)
┌─────────────────────────────────────────────────────┐
│ [BLEED - not printed, safety margin]                │
│    Cut-Line ┌────────────────────────────┐          │
│             │                            │          │
│             │  LABEL PRINTABLE AREA      │          │
│             │                            │          │
│             │  border_top = bleed_px + mm_to_px(5)  │
│             │  border_left = bleed_px + mm_to_px(5) │
│             │                            │          │
│             │  [Fields rendered here]    │          │
│             │                            │          │
│             │  y_pos increments downward │          │
│             │  x_left, x_right for columns          │
│             │                            │          │
│             └────────────────────────────┘          │
│ [BLEED - not printed, safety margin]                │
└─────────────────────────────────────────────────────┘
```

#### Vertical Layout (Approximate Y Positions)

| Section | Y Position Formula | Fields |
|---------|-------------------|--------|
| **Header** | `border_top + mm_to_px(5)` | Product Description (Field 4) |
| **NSN Row** | `y_pos += FONT_SIZE_LARGE + mm_to_px(8)` | NATO Stock No (Field 11) |
| **Barcode Row 1** | `y_pos += mm_to_px(10)` | NIIN Barcode (Field 16), Data Matrix (Field 21) |
| **NIIN Text** | `y_pos += barcode_height + mm_to_px(2)` | NIIN (Field 15), Unit (Field 17), Hazmat (Field 18) |
| **Barcode Row 2** | `y_pos += mm_to_px(12)` | Batch Barcode (Field 7), Date Barcode (Field 20) |
| **Text Row** | `y_pos += barcode_height + mm_to_px(2)` | Batch Managed (Field 6), Use by Date (Field 19) |
| **Table Section** | `y_pos += mm_to_px(15)` | Fields 1-3, 5, 8, 10, 13-14 |
| **Field 12 Box** | `y_pos += table_height` | Safety & Movement Markings (Field 12) |
| **Contractor Row** | `y_pos += field12_height` | Contractor Details (Field 9) |

**Key Variables:**
- `border_top` = `bleed_px + mm_to_px(5, dpi)`
- `border_left` = `bleed_px + mm_to_px(5, dpi)`
- `border_bottom` = `total_height_px - bleed_px - mm_to_px(5, dpi)`
- `border_right` = `total_width_px - bleed_px - mm_to_px(5, dpi)`
- `x_left` = `border_left`
- `x_right` = `border_right`

#### Barcode Dimensions (Millimeters)

| Barcode Type | Width (mm) | Height (mm) | Location | Resize Method |
|--------------|-----------|-------------|----------|---------------|
| Code 128 (Batch) | 50 | 15 | Left column | LANCZOS |
| Code 39 (NIIN) | 55 | 15 | Top left | LANCZOS |
| Code 128 (Date) | 50 | 15 | Right column | LANCZOS |
| Data Matrix | 20 × 20 | 20 | Top right | NEAREST |

**Convert to Pixels:**
```python
batch_width_px = mm_to_px(50, dpi)
batch_height_px = mm_to_px(15, dpi)
dm_size_px = mm_to_px(20, dpi)
```

---

### 5. Barcode Generation Details

#### Code 128 (python-barcode library)
**File:** `dod_label_generator_png.py`
**Function:** `generate_code128(data)`

```python
from barcode import Code128
from barcode.writer import ImageWriter

def generate_code128(self, data):
    """Generate Code 128 barcode as PIL Image"""
    try:
        # Create barcode with ImageWriter
        code128 = Code128(str(data), writer=ImageWriter())

        # Render to BytesIO
        buffer = BytesIO()
        code128.write(buffer, options={
            'module_height': 10,  # Height in mm
            'module_width': 0.2,  # Width in mm (bar width)
            'quiet_zone': 6.5,    # Quiet zone in mm (ISO requirement)
            'font_size': 8,       # HRI font size
            'text_distance': 2,   # Distance from barcode to HRI
        })

        # Load as PIL Image
        buffer.seek(0)
        img = Image.open(buffer)
        return img.convert('RGB')
    except Exception as e:
        print(f"Error generating Code 128: {e}")
        return None
```

**Safe to Modify:**
- `module_height`: Change bar height (recommend 10-15mm)
- **DO NOT MODIFY:**
  - `quiet_zone` (ISO requirement)
  - `module_width` (affects scannability)
  - **CRITICAL:** `write_text` MUST be `False` - HRI text causes overlaps and is redundant (label already has separate text fields)

#### Code 39 (python-barcode library)
**Function:** `generate_code39(data)`

```python
from barcode import Code39

def generate_code39(self, data):
    """Generate Code 39 barcode as PIL Image"""
    try:
        code39 = Code39(str(data), writer=ImageWriter(), add_checksum=False)
        buffer = BytesIO()
        code39.write(buffer, options={
            'module_height': 10,
            'module_width': 0.3,   # Wider than Code 128 (spec requirement)
            'quiet_zone': 10,      # Larger quiet zone (ISO requirement)
            'font_size': 8,
            'text_distance': 2,
        })
        buffer.seek(0)
        img = Image.open(buffer)
        return img.convert('RGB')
    except Exception as e:
        print(f"Error generating Code 39: {e}")
        return None
```

**Critical:** `add_checksum=False` - Code 39 doesn't require checksum for NIIN
**Safe to Modify:** `module_height` only
**DO NOT MODIFY:**
  - `quiet_zone` (ISO requirement)
  - `module_width` (affects scannability)
  - **CRITICAL:** `write_text` MUST be `False` - HRI text causes overlaps and is redundant

#### GS1 Data Matrix (pylibdmtx library)
**Function:** `generate_datamatrix(row)`

```python
from pylibdmtx.pylibdmtx import encode

def generate_datamatrix(self, row):
    """Generate GS1 Data Matrix with Application Identifiers"""
    try:
        # Extract data
        nsn = str(row.get('nato_stock_no', '')).replace('-', '')
        batch = str(row.get('batch_lot_no', ''))
        expiry_yymmdd = self.calculate_expiry_yymmdd(row)
        serial = str(row.get('serial_number', 'SN000001'))

        # Build GS1 string with FNC1 separators
        gs = chr(29)  # ASCII 29 - GS1 separator
        data = f"{gs}7001{nsn}{gs}10{batch}{gs}17{expiry_yymmdd}{gs}21{serial}"

        # Encode to Data Matrix
        encoded = encode(data.encode('utf-8'), size='ShapeAuto')

        # Convert to PIL Image
        img = Image.frombytes('RGB',
                              (encoded.width, encoded.height),
                              encoded.pixels)
        return img
    except Exception as e:
        print(f"Error generating Data Matrix: {e}")
        return None
```

**Critical Elements:**
1. **FNC1 Separator:** `chr(29)` - MUST be ASCII 29
2. **AI Order:** 7001, 10, 17, 21 (standard GS1 sequence)
3. **NSN Format:** Remove hyphens, 13 digits only
4. **Date Format:** YYMMDD (6 digits)
5. **Encoding:** UTF-8 byte encoding

**Safe to Modify:**
- Add/remove AI fields (10, 17, 21 optional)
- Change `size` parameter: `'ShapeAuto'`, `'10x10'`, `'12x12'`, etc.

**DO NOT MODIFY:**
- FNC1 character (ASCII 29)

---

## Visual Style Standards (v2.2.4+)

### Date Formatting
**CRITICAL:** Date formats were changed in v2.2.3 and MUST be maintained:

1. **Field 8 (Date of Manufacture):**
   - Format: `%b %Y` (e.g., "NOV 2025")
   - Function: `format_date_display()`
   - Input: DD/MM/YYYY string
   - Output: Uppercase month abbreviation + year

2. **Field 19 (Use by Date / Re-Test Date):**
   - Format: `%d %b %y` (e.g., "05 NOV 27")
   - Function: `calculate_dates()`
   - Input: Manufacture date + shelf life months
   - Output: Uppercase 2-digit year format

### Field 6 (Batch Lot Managed)
**Format:** `"B/L: Y"` or `"B/L: N"`
- Label text: "B/L: " (shortened from "Batch Lot Managed: ")
- Value: 'Y' if raw value is 'Y' or 'YES' (case-insensitive), else 'N'

### NATO Code Box Rendering (Field 1)
**CRITICAL:** Implemented in v2.2.4 with specific requirements:

**When to Draw Box:**
- ONLY when `nato_code_val != '-'`
- If NATO code is a dash/placeholder, render as plain text with NO rectangle

**Box Specifications:**
```python
# Correct implementation (v2.2.4):
text_x = current_x + 12  # Offset text start position
nato_bbox = draw.textbbox((text_x, text_y), nato_code_val, font=font_data)

padding = 10  # Padding around bounding box
rect_x1 = nato_bbox[0] - padding
rect_y1 = nato_bbox[1] - padding
rect_x2 = nato_bbox[2] + padding
rect_y2 = nato_bbox[3] + padding

draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], outline='black', width=3)
draw.text((text_x, text_y), nato_code_val, fill='black', font=font_data)
```

**Key Requirements:**
1. **Padding:** 10px on all sides around text bounding box
2. **Border Width:** 3px (thicker than table borders which are 1-2px)
3. **Bounding Box Method:** Use `draw.textbbox((text_x, text_y), text, font)` with ACTUAL text position, not (0,0)
4. **Conditional Rendering:** Check if value is "-" and skip box if true

**Common Mistakes to Avoid:**
- ❌ Using `draw.textbbox((0, 0), ...)` - causes incorrect y-coordinates
- ❌ Calculating padding from text baseline instead of bounding box
- ❌ Drawing box for dash "-" values (looks like graphical glitch)
- ❌ Using padding < 10px (causes border to cut through text descenders)

### Field 18 (Hazardous Material Code) - HAZARD BOX IN HEADER
**IMPORTANT CHANGE (v2.4.1):** Field 18 is NO LONGER in the data table. It now renders as a visual indicator in the label header.

**Visual Rendering:**
- **Location:** Top-right header area, positioned between "Unit of Issue" and the GS1 Data Matrix barcode
- **Style:** Black filled square with white text
- **Components:**
  1. "HAZARD" label text (tiny/small font, uppercase) positioned ABOVE the box
  2. Black filled square below the label
  3. Hazard class number rendered in WHITE, centered inside the black box
- **Conditional Display:** Only drawn when `hazardous_material_code` is not "-" or empty
- **Box Dimensions:**
  - PNG generator (`dod_label_generator_png.py`): 8mm square
  - App generator (`dod_label_app.py`): 5mm square (compact layout)

**Data Format Rule:**
- `hazardous_material_code` in `products.json` MUST contain ONLY the single-digit hazard class number
- ✅ CORRECT: `"hazardous_material_code": "3"` (Class 3 - Flammable Liquid)
- ❌ INCORRECT: `"hazardous_material_code": "UN1307, 3, III"` (full UN string)
- Full UN/safety information belongs in `safety_markings` field (Field 12)

**Code Location:**
- `dod_label_generator_png.py`: Lines 342-373 (header section)
- `dod_label_app.py`: Lines 335-366 (header section)
- Variable defined early in header: `hazmat_code = self.safe_str(row.get('hazardous_material_code', ''), '-')`

**Example Products:**
- DCI 4A: Class 3 (Flammable Liquid) - displays white "3" in black box
- Prist FSII: Class 3 (Flammable Liquid) - displays white "3" in black box
- Fuchs OM-11: No hazard class ("-") - box not drawn

### Field 12 (Safety & Movement Markings)
**Label Text (App only):**
- ❌ OLD: "Field 12: Safety & Movement Markings"
- ✅ NEW: "Safety & Movement Markings" (removed "Field 12:" prefix)
- AI 7001 (NSN is mandatory)
- String encoding (UTF-8)

**Testing:** Submit to GS1 Australia after any changes

---

### 6. Common Editing Scenarios

#### Scenario 1: Adjust Field Spacing
**Goal:** Increase spacing between barcode rows
**Safe Approach:**
```python
# Find the y_pos increment line
y_pos += barcode_height + mm_to_px(3, self.dpi)  # OLD: 3mm spacing

# Change to
y_pos += barcode_height + mm_to_px(5, self.dpi)  # NEW: 5mm spacing
```
**Testing:** Verify no overlap, fields still fit on label

#### Scenario 2: Change Font Size
**Goal:** Make product description larger
**Safe Approach:**
```python
# In __init__ method, adjust scale
self.FONT_SIZE_LARGE = int(24 * scale * base_scale)  # OLD: 20

# Or adjust in specific text draw call
font_large = self.get_font(int(FONT_SIZE_LARGE * 1.2), bold=True)  # 20% larger
```
**Testing:** Check text doesn't overflow at smallest label size (2"×1")

#### Scenario 3: Reposition Barcode
**Goal:** Move Data Matrix to left side instead of right
**Safe Approach:**
```python
# OLD: Right-aligned Data Matrix
dm_x = x_right - dm_size - mm_to_px(2, self.dpi)

# NEW: Left-aligned Data Matrix
dm_x = x_left + mm_to_px(2, self.dpi)

img.paste(dm_resized, (dm_x, y_pos))
```
**Testing:** Verify quiet zones not encroached, still scannable

#### Scenario 4: Add New Field
**Goal:** Add Field 22 (hypothetical)
**Safe Approach:**
1. Update data model (`sample_data_dod.csv` + validation)
2. Calculate y_pos after existing fields
3. Use `safe_str()` for null handling
4. Add text rendering
5. Test with missing data

```python
# Add after Field 21 rendering
y_pos += dm_size + mm_to_px(5, self.dpi)
new_field = safe_str(row.get('new_field_22'), '-')
draw.text((x_left, y_pos), f"Field 22: {new_field}", fill='black', font=font_body)
```

#### Scenario 5: Change Barcode Size
**Goal:** Make NIIN barcode taller
**Safe Approach:**
```python
# In barcode generation options
code39.write(buffer, options={
    'module_height': 12,  # OLD: 10mm, NEW: 12mm
    # ... other options unchanged
})

# Adjust paste height accordingly
new_height_mm = 17  # Was 15mm
new_height_px = mm_to_px(new_height_mm, self.dpi)
```
**Testing:** Verify barcode still scannable, ISO grade ≥ 1.0

---

### 7. Testing Protocol After Edits

#### Level 1: Quick Smoke Test (30 seconds)
```bash
python dod_label_generator_png.py sample_data_dod.csv --size "4\" × 6\""
```
- Visual check: Label renders without errors
- Check: All fields visible, no overlap

#### Level 2: Multi-Size Test (2 minutes)
```bash
python dod_label_generator_png.py sample_data_dod.csv --all-sizes
```
- Check all 8 sizes: 2"×1", 3"×2", 4"×2", 4"×3", 4"×4", 4"×6", A6, A5
- Verify: Text scaling correct, no clipping

#### Level 3: Barcode Verification (5 minutes)
```bash
python verify_barcodes.py
```
- Automated scan of all 4 barcode types
- Pass criteria: All barcodes decode correctly
- Optional: Check ISO grade with barcode verifier hardware

#### Level 4: Physical Print Test (10 minutes)
1. Print label on laser printer (600 DPI setting)
2. Scan each barcode with handheld scanner
3. Verify 100% scan rate
4. Check readability under harsh lighting

#### Level 5: Compliance Test (Submit to GS1)
- Required after Data Matrix changes
- Submit samples to GS1 Australia
- Await ISO/IEC 15415 verification report

---

### 8. Emergency Rollback Procedure

**If Edit Breaks Barcode Scannability:**

```bash
# 1. Revert changes
git checkout main -- dod_label_generator_png.py

# 2. Verify working state
python verify_barcodes.py

# 3. Document issue
echo "Edit caused barcode failure: [describe change]" >> .claude_docs/MEMORY.md

# 4. Re-approach with safer method
# Review this file, consult barcode specs, test incrementally
```

---

### 9. Performance Optimization Notes

**Current Performance:** ~1.5s per PNG label at 600 DPI

**Bottlenecks:**
1. Barcode generation: ~0.4s (4 barcodes × ~0.1s each)
2. Image operations: ~0.3s (resize, paste)
3. Font rendering: ~0.2s (TrueType text)
4. File I/O: ~0.1s (save PNG)

**Safe Optimizations:**
- **Batch Processing:** Reuse barcode images for duplicate batch numbers
- **Font Caching:** Load fonts once, reuse `ImageFont` objects
- **Parallel Generation:** Use `multiprocessing` for 50+ labels

**Unsafe Optimizations (DO NOT DO):**
- ❌ Lower DPI (breaks ISO compliance)
- ❌ Reduce barcode quality settings (breaks scannability)
- ❌ Skip barcode generation (defeats purpose)

---

### 10. Contact for Critical Issues

**If You're Unsure About an Edit:**
1. Create git branch
2. Document proposed change in this file
3. Test thoroughly with protocol above
4. Request review before merging to main

**Barcode Compliance Questions:**
- Consult ISO/IEC standards documents
- Contact GS1 Australia: https://www.gs1au.org
- Review MIL-STD-129 specification

**PIL/Pillow Technical Issues:**
- Pillow Documentation: https://pillow.readthedocs.io
- ImageDraw reference: https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html

---

## Version Control Workflow

**Current Branch:** `main`
**Branch Strategy:** Feature branches per task

**Workflow:**
1. `git checkout -b feature/description`
2. Make changes, test thoroughly
3. `git commit -m "feat(scope): description"`
4. `git push origin feature/description`
5. Merge to `main` after verification

**Commit Conventions:** Conventional Commits
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Testing
- `chore:` Maintenance

**Example:**
```bash
git commit -m "feat(barcode): increase Code 39 quiet zone to 12mm for better scannability"
```

---

## Monitoring & Maintenance

**Regular Tasks:**
- **Weekly:** Review generated labels, spot-check barcodes
- **Monthly:** Re-test barcode scannability with physical scanner
- **Quarterly:** Submit Data Matrix samples to GS1 Australia
- **Annually:** Review ISO/IEC standards for updates

**Update Triggers:**
- New military specifications (MIL-STD revisions)
- GS1 Application Identifier changes
- ISO barcode standard updates
- Client feedback (Valorem Chemicals)

---

## Conclusion

This PIL rendering system is **production-ready** and **mission-critical**. Any changes must preserve:

1. **600 DPI resolution** (barcode quality)
2. **Pixel-perfect positioning** (ISO compliance)
3. **GS1 Data Matrix encoding** (FNC1 separators)
4. **Field 12 always visible** (user requirement)
5. **Safe string handling** (NaN/null defense)

**When in doubt, don't edit. Consult this document first.**

---

## Data Architecture (v2.3.0+)

### JSON SKU Database Overview

**Version:** Introduced in v2.3.0
**Purpose:** Separate Fixed Product Data from Variable Label Data
**File:** `products.json`

### Data Separation Strategy

**Fixed Data (products.json):**
- Product specifications that don't change per label
- Stored centrally, managed by admin
- Examples: NSN, NATO Code, Specification, Shelf Life

**Variable Data (User Input):**
- Information that changes for each label
- Entered by user via Streamlit UI
- Examples: Batch Lot Number, Date of Manufacture, Test Report Number

### products.json Structure

```json
[
  {
    "id": "PRODUCT_SIZE",
    "product_name": "Product Name",
    "nsn": "nnnn-nn-nnn-nnnn",
    "nato_code": "X-XXX or -",
    "jsd_reference": "XX-XX",
    "specification": "Spec Number",
    "unit_of_issue": "SIZE",
    "capacity_weight": "SIZE",
    "shelf_life_months": 24,
    "batch_lot_managed": "Y",
    "hazardous_material_code": "UN#### or -",
    "contractor_details": "Company|Address|City|Country",
    "safety_markings": "Markings or -"
  }
]
```

### Unique ID Rule (CRITICAL)

**Rule:** Each product/pack size combination MUST have a unique `id` field.

**Rationale:** Products can have the same name but different pack sizes, so `product_name` alone is not unique.

**Examples:**
- `OM11_20L` - Fuchs OM-11 in 20 litre pack
- `OM11_205L` - Fuchs OM-11 in 205 litre drum
- `OM11_1000L` - Fuchs OM-11 in 1000 litre IBC
- `DCI4A_55GAL` - DCI 4A in 55 US gallon drum

**Naming Convention:**
- Format: `PRODUCTCODE_SIZE`
- Use uppercase letters and numbers only
- Use underscores for separators
- Keep IDs short but descriptive

### Field Mappings

| JSON Field | Label Field | Type | Example |
|------------|-------------|------|---------|
| `id` | (Internal) | Fixed | "OM11_20L" |
| `product_name` | Field 4 | Fixed | "Fuchs OM-11" |
| `nsn` | Field 11 | Fixed | "9150-66-035-7879" |
| `nato_code` | Field 1 | Fixed | "H-576" |
| `jsd_reference` | Field 2 | Fixed | "OM-33" |
| `specification` | Field 3 | Fixed | "DEF STAN 91-39 Issue 4" |
| `unit_of_issue` | Field 17 | Fixed | "20 LI" |
| `capacity_weight` | Field 10 | Fixed | "20 LI" |
| `shelf_life_months` | (Calculation) | Fixed | 36 |
| `batch_lot_managed` | Field 6 | Fixed | "Y" |
| `hazardous_material_code` | Field 18 | Fixed | "-" |
| `contractor_details` | Field 9 | Fixed | "Valorem..." |
| `safety_markings` | Field 12 | Fixed | "-" |
| (User Input) | Field 5 | Variable | "FM251122A" |
| (User Input) | Field 8 | Variable | "23/11/2025" |
| (User Input) | Field 14 | Variable | "-" |
| (Calculated) | Field 13 | Calculated | DOM + shelf_life |
| (Calculated) | Field 19 | Calculated | DOM + shelf_life |
| (Calculated) | Field 15 | Calculated | Last 9 digits of NSN |

### Date Calculation Logic (v2.4.2+)

**IMPORTANT CHANGE (v2.4.2):** Switched from `timedelta(days=months * 30)` to `relativedelta(months=months)` for accurate month arithmetic.

**Use by Date (Field 19):**
```python
from dateutil.relativedelta import relativedelta

use_by_date = date_of_manufacture + relativedelta(months=shelf_life_months)
# Format: DD MMM YY (e.g., "12 MAY 26")
# Always calculated, not editable
# Example: Nov 12 + 18 months = May 12 (exact day preserved)
```

**Re-Test Date (Field 13) - Manual Override Logic (v2.5.0+):**

**IMPORTANT CHANGE (v2.5.0):** Re-Test Date now supports manual override with linked Test Report Number field.

```python
from dateutil.relativedelta import relativedelta

# Default calculation
default_retest_date = date_of_manufacture + relativedelta(months=shelf_life_months)

# Override logic in generator
manual_retest = row.get('retest_date')
if manual_retest and manual_retest not in [None, '-', '']:
    retest_display = format_date_display(manual_retest)  # Manual override
else:
    retest_display = use_by_date  # Auto-calculate (Field 19)
```

**UI Logic (v2.5.0):**
- **Override Checkbox:** "Override Default Re-Test Date" (default: unchecked)
- **Re-Test Date Picker:**
  - Unchecked: `disabled=True` (shows calculated value, not editable)
  - Checked: `disabled=False` (allows manual date selection)
- **Test Report Number:**
  - Unchecked: `disabled=True` (grayed out)
  - Checked: `disabled=False` (active for input)
- **Visual Grouping:** Both fields in col2 (right column) for logical coupling

**Safety Rule - Stale Data Prevention:**
```python
# Data passing logic
'test_report_no': test_report_no if override_retest else "-",
'retest_date': retest_date.strftime('%d/%m/%Y') if override_retest and retest_date else None
```
- **IF Override is False:** Test Report field forced to `"-"` (ignores any hidden user input)
- **IF Override is True:** Uses actual user-provided values
- **Purpose:** Prevents stale data from disabled fields printing on labels

**Compliance Warning:**
- Shows when: `override_retest == True` AND `test_report_no in ["-", "", None]`
- Message: "⚠️ Compliance Warning: You are overriding the Re-Test date without a Test Report Number."
- Purpose: Reminds users to document manual date changes

**Why relativedelta?**
- **OLD (v2.3.0):** `timedelta(days=months * 30)` - assumes all months are 30 days
  - ❌ Nov 12 + 18 months = May 06 (incorrect, off by 6 days)
- **NEW (v2.4.2):** `relativedelta(months=months)` - accurate calendar month addition
  - ✅ Nov 12 + 18 months = May 12 (correct, preserves day of month)
- Handles month-end boundaries intelligently (e.g., Jan 31 + 1 month = Feb 28)

**NIIN Extraction (Field 15):**
```python
nsn = "9150-66-035-7879"
niin = nsn.replace('-', '')[-9:]  # "660357879"
```

### GS1 Data Matrix Changes (v2.3.0)

**CRITICAL CHANGE:** Serial number (AI 21) removed from GS1 encoding.

**Old Format (v2.2.x):**
```
AI 7001 (NSN) + AI 10 (Batch) + AI 17 (Expiry) + AI 21 (Serial)
```

**New Format (v2.3.0):**
```
AI 7001 (NSN) + AI 10 (Batch) + AI 17 (Expiry)
```

**Encoding:**
```python
gs = chr(29)  # GS1 separator (ASCII 29)
nsn_digits = '9150660357879'  # 13 digits, no hyphens
batch = 'FM251122A'
expiry_yymmdd = '281107'  # YYMMDD format

gs1_data = f"7001{nsn_digits}{GS}10{batch}{GS}17{expiry_yymmdd}"
# Result: 70019150660357879[GS]10FM251122A[GS]17281107
```

**Compliance Note:** Submit new format to GS1 Australia for re-testing before production use.

### User Workflow (v2.3.0)

1. **Select Product:** Dropdown shows `product_name (unit_of_issue)`
2. **Enter Variable Data:**
   - Batch Lot Number (required)
   - Date of Manufacture (required, date picker)
   - Test Report Number (optional, defaults to "-")
3. **Review Calculated Defaults:**
   - Re-Test Date (date picker, defaults to DOM + shelf life, user can override)
   - Use by Date (display only, auto-calculated)
4. **Choose Label Size:** Select from 8 available sizes
5. **Generate Label:** Click button to combine product + user data
6. **Download:** PNG download (PDF coming in v2.3.1)

### Adding New Products

**Step 1:** Determine unique ID
- Check existing products.json for conflicts
- Follow naming convention: `PRODUCTCODE_SIZE`

**Step 2:** Create JSON entry
```json
{
  "id": "NEW_PRODUCT_SIZE",
  "product_name": "Product Name",
  "nsn": "nnnn-nn-nnn-nnnn",
  "nato_code": "X-XXX",
  "jsd_reference": "XX-XX",
  "specification": "Spec Number",
  "unit_of_issue": "SIZE",
  "capacity_weight": "SIZE",
  "shelf_life_months": 24,
  "batch_lot_managed": "Y",
  "hazardous_material_code": "-",
  "contractor_details": "Company|Address|City|Country",
  "safety_markings": "-"
}
```

**Step 3:** Validate JSON
```bash
python -c "import json; json.load(open('products.json'))"
```

**Step 4:** Restart Streamlit app
```bash
streamlit run dod_label_app.py
```

### Migration from CSV Workflow

**Old Workflow (v2.2.x):**
- Upload CSV with all fields (fixed + variable)
- Edit in table
- Generate multiple labels

**New Workflow (v2.3.0):**
- Product data in JSON (one-time setup)
- User enters variable data per label
- Generate single label at a time

**Migration Steps:**
1. Extract unique products from CSV data
2. Create JSON entry for each product/size
3. Use new UI to generate labels individually

**Benefits:**
- Eliminates data entry errors (NSN, specs pre-populated)
- Faster label generation (less typing)
- Centralized product database (easier to maintain)
- Support for multiple pack sizes per product

---

## Product Management Workflow (v2.4.0+)

### Product Manager GUI Overview

**Version:** Introduced in v2.4.0
**Access:** Streamlit App → Sidebar → "Manage Products"
**Purpose:** Web-based GUI for CRUD operations on `products.json` database

### Features

#### 1. Product Table Display
- Shows all products in DataFrame format
- Columns: ID, Product Name, NSN, Unit of Issue, Capacity, Shelf Life, NATO Code, JSD Reference
- Real-time view of database contents
- Product count indicator

#### 2. Add/Edit Product Form
**Two Modes:**
- **Add New:** Create new product entry with unique ID
- **Edit Existing:** Modify existing product (ID field disabled)

**Form Fields (All Validated):**
- Product ID* (unique identifier, format: `PRODUCTCODE_SIZE`)
- Product Name* (e.g., "Fuchs OM-11")
- NSN* (13 digits, format: `nnnn-nn-nnn-nnnn`)
- NATO Code (or "-")
- JSD Reference (or "-")
- Specification* (e.g., "DEF STAN 91-39 Issue 4")
- Unit of Issue* (e.g., "DR" for Drum, "CN" for Can)
- Capacity/Weight* (e.g., "20 LI", "55 US GAL")
- Shelf Life (months)* (1-120 range)
- Batch Lot Managed* (Y/N dropdown)
- Hazardous Material Code (UN code or "-")
- Contractor Details* (pipe-separated format)
- Safety/Movement Markings (or "-")

**Validation Rules:**
- Required fields must be filled
- NSN must be exactly 13 digits (dashes optional)
- Product ID must be unique for new products
- All text fields trimmed of whitespace

#### 3. Delete Product
- Select product from dropdown
- Two-step confirmation process:
  1. Click "Delete" button
  2. Confirm with "Yes, Delete" or "Cancel"
- Warning message displays product ID
- Prevents accidental deletions

### Atomic Write Safety Feature

**CRITICAL:** All `products.json` updates use atomic write pattern to prevent data corruption.

**Safe Write Process:**
```python
def save_products_json(products_db, products_file):
    """Safely save with backup/restore capability"""

    # Step 1: Create backup
    backup_file = products_file.with_suffix('.json.bak')
    shutil.copy2(products_file, backup_file)

    # Step 2: Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        json.dump(products_db, tmp, indent=2, ensure_ascii=False)
        tmp_path = Path(tmp.name)

    # Step 3: Atomic rename (overwrites original)
    shutil.move(str(tmp_path), str(products_file))

    # Step 4: Remove backup if successful
    backup_file.unlink()

    # Error handling: Restore from backup if write fails
    except Exception:
        if backup_file.exists():
            shutil.copy2(backup_file, products_file)
        raise
```

**Why Atomic Writes Matter:**
1. **No Partial Writes:** Either entire file writes or nothing changes
2. **Backup Safety:** Original file preserved until new file verified
3. **Crash Recovery:** Interrupted writes don't corrupt database
4. **Rollback on Error:** Automatic restore from backup if write fails

**Temporary Files:**
- `products.json.bak` - Backup file (exists briefly during write)
- `temp_XXXXX.json` - Temporary write target (deleted after atomic rename)

### User Workflow

**To Add Product:**
1. Navigate to "Manage Products" in sidebar
2. Select "Add New" mode
3. Fill in product form (all required fields)
4. Click "💾 Save Product"
5. Page refreshes, new product appears in table

**To Edit Product:**
1. Navigate to "Manage Products"
2. Select "Edit Existing" mode
3. Choose product from dropdown
4. Modify desired fields (Product ID disabled)
5. Click "💾 Update Product"
6. Page refreshes with updated data

**To Delete Product:**
1. Navigate to "Manage Products"
2. Scroll to "Delete Product" section
3. Select product from dropdown
4. Click "🗑️ Delete"
5. Confirm deletion with "✅ Yes, Delete"
6. Product removed from database

### Technical Notes

**Session State:**
- `st.session_state['confirm_delete']` tracks deletion confirmation
- Page auto-refreshes (`st.rerun()`) after save/delete operations

**Data Validation:**
- NSN format: Checks 13 digits with optional dashes
- Duplicate ID: Prevents adding product with existing ID
- Required fields: Validates all mandatory fields filled

**Error Handling:**
- User-friendly error messages via `st.error()`
- Success confirmations via `st.success()`
- Backup restoration on write failures

**File Safety:**
- Backup created before every write
- Atomic rename prevents corruption
- JSON validation before write
- UTF-8 encoding preserved

### Common Mistakes to Avoid

1. **Don't Edit products.json Directly While App Running:** Use GUI to ensure atomic writes
2. **Don't Duplicate Product IDs:** Each ID must be unique (validation prevents this)
3. **Don't Skip Required Fields:** Form validation enforces all required fields
4. **Don't Use Invalid NSN Format:** Must be 13 digits (e.g., "6850-99-224-5252")

### Migration from Manual JSON Editing

**Old Way (Manual):**
```bash
nano products.json  # Edit by hand
# Risk: Syntax errors, missing fields, corruption
```

**New Way (GUI):**
```bash
streamlit run dod_label_app.py
# Navigate to "Manage Products"
# Use form with validation
```

**Benefits:**
- Form validation prevents errors
- Atomic writes prevent corruption
- No JSON syntax mistakes
- Immediate visual feedback

---

**For Technical Stack Details, see:** `.claude_docs/TECH_STACK.md`
**For Visual Specifications, see:** `.claude_docs/PROJECT_BRIEF.md`
**For Architecture Decisions, see:** `.claude_docs/DECISIONS.md`
**For Version History, see:** `.claude_docs/PROGRESS.md`
