# System Architecture

**version:** v1.0.0 (LEGACY)
**Created:** 2025-11-14
**Last Updated:** 2025-11-14

---

## ⚠️ DEPRECATION NOTICE

**This document describes the v1.0 GHS chemical label system, which is now LEGACY.**

**For current v2.x DoD/NATO label system architecture, see:**
- `.claude_docs/TECH_STACK.md` - Technical stack and rendering strategy
- `.claude_docs/PROJECT_BRIEF.md` - Visual design and specifications
- `.claude_docs/MEMORY.md` - PIL Rendering Maintenance Plan
- `.agent/system/dod-label-specification.md` - DoD/NATO 21-field spec

**Current System (v2.2.1):**
- **DoD/NATO Military Labels** (primary focus)
- 21-field data model with NSN/NIIN tracking
- 4 barcode symbologies (Code 128 ×2, Code 39, Data Matrix)
- Dual rendering: ReportLab (PDF) + PIL/Pillow (PNG)
- Streamlit web dashboard
- Multiple label sizes (2"×1" to A4)

---

## Overview (v1.0 GHS - LEGACY)

The Drum Label Generator is a Python-based PDF generation system that transforms CSV/Excel product data into GHS-compliant A5 drum labels. The architecture is designed for batch processing with minimal configuration.

**NOTE:** This system is maintained for existing users but v2.x DoD labels are the primary focus.

## System Components

### 1. Core Application

**File:** `drum_label_generator.py` (413 lines)

**Main Class:** `DrumLabelGenerator`

**Responsibilities:**
- Load and validate CSV/Excel data
- Generate individual label PDFs
- Coordinate barcode, QR code, and pictogram rendering
- Handle error cases (missing data, invalid formats)

**Key Methods:**
- `load_data()` - Read CSV/Excel using pandas
- `validate_data()` - Check required columns exist
- `create_label(row, output_path)` - Generate single label PDF
- `generate_all_labels()` - Batch process all records
- `generate_barcode(data)` - Create Code128 barcode image
- `generate_qr_code(data)` - Create QR code image
- `load_ghs_pictogram(code)` - Load GHS pictogram PNG

### 2. Configuration System

**File:** `config.py` (60 lines)

**Purpose:** Centralize all customizable settings

**Configuration Categories:**
- **Page dimensions:** A5 size (148mm × 210mm), margins
- **Fonts:** Helvetica variants, sizes (7-14pt)
- **Layout:** Column widths, row heights, spacing
- **Elements:** Pictogram size (20mm), barcode dimensions, QR size (25mm)
- **Company details:** Name, address, phone, email
- **Paths:** GHS pictogram folder, output folder

**Design Pattern:** Simple Python module with constants (no classes)

### 3. Data Processing

**Input Formats:**
- CSV (`.csv`) via `pandas.read_csv()`
- Excel (`.xlsx`, `.xls`) via `pandas.read_excel()`

**Required Columns:**
- `product_code` - String identifier
- `product_name` - String (max ~60 chars for layout)
- `batch_number` - String/alphanumeric

**Optional Columns:** (18 additional fields, see data schema)

**Data Validation:**
- Required columns presence check
- NaN/empty value handling
- Type coercion for display

### 4. External Dependencies

**PDF Generation:**
- `reportlab` - Canvas-based PDF rendering, table layout

**Data Processing:**
- `pandas` - CSV/Excel reading, DataFrame operations
- `openpyxl` - Excel file format support

**Barcode/QR:**
- `python-barcode` - Code128 barcode generation
- `qrcode` - QR code image creation

**Image Processing:**
- `Pillow (PIL)` - Image loading, format conversion, BytesIO buffering

## Data Flow

```
Input Data (CSV/Excel)
        ↓
    pandas.read_csv/read_excel
        ↓
    DataFrame validation
        ↓
For each row:
        ↓
    ├─→ Load GHS pictograms (PIL)
    ├─→ Generate barcode (python-barcode)
    ├─→ Generate QR code (qrcode)
    └─→ Create PDF (ReportLab)
        ↓
    Save to output/ folder
        ↓
PDF files ready for print
```

## File Structure

```
2511_DOD Labels/
├── drum_label_generator.py    # Main application
├── config.py                   # Configuration
├── requirements.txt            # Python dependencies
├── sample_data.csv             # Example data
├── test_installation.py        # Setup validation
├── setup.sh                    # Automated setup (Unix)
│
├── ghs_pictograms/            # GHS hazard pictogram PNGs
│   ├── GHS01.png              # Explosive
│   ├── GHS02.png              # Flammable
│   └── ... (GHS03-09)
│
├── output/                    # Generated label PDFs
│   └── drum_label_*.pdf
│
├── .agent/                    # AI agent documentation
│   ├── README.md              # Documentation index
│   ├── tasks/                 # Implementation plans
│   ├── system/                # Architecture docs (this file)
│   └── sops/                  # Standard procedures
│
├── .claude/                   # Claude Code integration
│   └── commands/              # Custom slash commands
│
├── archive/                   # Deprecated files
│
└── Documentation/
    ├── README.md
    ├── COMPLETE_SETUP_GUIDE.md
    ├── QUICK_REFERENCE.md
    └── CHANGELOG.md
```

## Label Generation Process

### Phase 1: Initialization

1. Create `DrumLabelGenerator` instance with data file path
2. Check GHS pictogram folder exists
3. Create output folder if missing

### Phase 2: Data Loading

1. Detect file type (CSV vs Excel)
2. Load data into pandas DataFrame
3. Validate required columns present
4. Report row count

### Phase 3: PDF Generation (per row)

1. Create ReportLab Canvas (A5 size)
2. Render sections top-to-bottom:
   - Company header (bold, large font)
   - Product name (header font)
   - Information table (2-column layout)
   - GHS pictograms (horizontal row, max 5)
   - Hazard statements (bulleted list)
   - Precautionary statements (bulleted list)
   - Storage instructions
   - Emergency contact (red text)
   - Barcode (bottom left)
   - QR code (bottom right)
3. Save PDF with timestamped filename

### Phase 4: Completion

1. Report generated file paths
2. Exit with success/failure status

## Error Handling

**Missing Data:**
- Optional fields display as empty (no error)
- Required fields raise validation error before generation

**Missing GHS Pictograms:**
- Warning logged to console
- Label generation continues without image

**Barcode Generation Failures:**
- Caught exception, logged
- Label generated without barcode section

**File I/O Errors:**
- Reported per-label (doesn't stop batch)
- Exit code 1 on any failure

## Extension Points

### Adding New Label Sections

Modify `create_label()` method in `drum_label_generator.py`:
1. Track y_pos for vertical placement
2. Use config.py constants for spacing
3. Add corresponding column to input data schema

### Custom Barcode Formats

Replace `generate_barcode()` call:
- Support for EAN-13, Code39, etc. via python-barcode
- Customize barcode data format (line 324)

### Layout Customization

Edit `config.py`:
- Adjust margins, fonts, element sizes
- No code changes required for most layout tweaks

### API Integration

Extend `DrumLabelGenerator` class:
- Add method to fetch data from REST API
- Transform API response to pandas DataFrame
- Use existing `create_label()` pipeline

## Performance Characteristics

**Throughput:**
- ~2-5 labels per second (depends on complexity)
- Bottleneck: ReportLab PDF rendering

**Memory:**
- Pandas loads full CSV into RAM
- For >1000 labels, consider chunked processing

**Disk I/O:**
- Each label = separate PDF file (~50-150KB)
- GHS pictograms cached by PIL automatically

## Security Considerations

**Input Validation:**
- No SQL injection risk (file-based input)
- Path traversal prevented (output folder hardcoded)
- No user-supplied Python code execution

**Data Privacy:**
- CSV files may contain sensitive product formulations
- Do not commit actual customer data to Git
- Use `sample_data.csv` for examples only

**Dependencies:**
- Pin versions in requirements.txt
- Regularly update for security patches

## Testing Strategy

**Manual Testing:**
- `test_installation.py` - Validates setup
- `sample_data.csv` - Known-good test cases

**Recommended Test Cases:**
- Missing optional columns
- Special characters in batch numbers
- Very long product names (truncation)
- Missing GHS pictograms
- Invalid CSV formatting

## Future Architecture Considerations

**Scalability:**
- Move to multiprocessing for >1000 labels
- Consider PDF merging (one file with all labels)

**Integration:**
- REST API endpoint for on-demand generation
- Web UI for non-technical users
- Database backend (replace CSV input)

**Monitoring:**
- Logging framework for production use
- Label generation audit trail
- Error reporting system
