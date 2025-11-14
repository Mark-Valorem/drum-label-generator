# Label Layout Specification

**version:** v1.0.0
**Created:** 2025-11-14
**Last Updated:** 2025-11-14

## Overview

This document describes the A5 drum label layout, including section positioning, dimensions, and rendering logic. All measurements are in millimeters unless otherwise specified.

## Page Specifications

**Format:** A5 (ISO 216)
**Dimensions:** 148mm (width) × 210mm (height)
**Orientation:** Portrait

**Margins:**
- Top: 8mm
- Bottom: 8mm
- Left: 8mm
- Right: 8mm

**Printable Area:** 132mm × 194mm

## Layout Sections (Top to Bottom)

### 1. Company Header

**Location:** Top of page, starting at y = (210 - 8) = 202mm

**Content:**
- Line 1: Company name (Helvetica-Bold, 14pt)
- Line 2: Address | Phone (Helvetica, 7pt)

**Spacing:**
- 15mm between company name and address line
- 20mm total height

**Configuration:**
```python
FONT_COMPANY = "Helvetica-Bold"
FONT_SIZE_COMPANY = 14
COMPANY_NAME = "Valorem Chemicals Pty Ltd"
COMPANY_ADDRESS = "Sydney, NSW, Australia"
COMPANY_PHONE = "+61 (0)2 XXXX XXXX"
```

**Code Reference:** [drum_label_generator.py:186-193](../../drum_label_generator.py#L186-L193)

---

### 2. Product Name Header

**Location:** Below company header (y -= 20mm)

**Content:**
- Product name from `product_name` column
- Truncated to 60 characters if longer

**Styling:**
- Font: Helvetica-Bold
- Size: 10pt

**Spacing:**
- 15mm below this line to next section

**Code Reference:** [drum_label_generator.py:195-199](../../drum_label_generator.py#L195-L199)

---

### 3. Information Table

**Location:** Below product header (y -= 15mm)

**Format:** 2-column table with borders

**Column Widths:**
- Left (labels): 45mm
- Right (values): 95mm
- Total: 140mm

**Rows (conditionally included):**

| Label | Data Column | Always Shown |
|-------|-------------|--------------|
| Product Code: | `product_code` | Yes |
| Batch Number: | `batch_number` | Yes |
| Supplier: | `supplier` | If not empty |
| Net Weight: | `net_weight` | If not empty |
| Gross Weight: | `gross_weight` | If not empty |
| UN Number: | `un_number` | If not empty |
| Proper Shipping Name: | `proper_shipping_name` | If UN present |
| Hazard Class: | `hazard_class` | If UN present |
| Packing Group: | `packing_group` | If UN present |
| Manufactured: | `manufacture_date` | If not empty |
| Expiry: | `expiry_date` | If not empty |

**Styling:**
- Left column: Helvetica-Bold, 9pt
- Right column: Helvetica, 9pt
- Cell padding: 2mm
- Border: 0.5pt grey
- Vertical alignment: Top

**Configuration:**
```python
LABEL_COL_WIDTH = 45  # mm
VALUE_COL_WIDTH = 95  # mm
TABLE_CELL_PADDING = 2
FONT_SIZE_BODY = 9
```

**Dynamic Height:** Table height calculated based on number of rows

**Spacing:** 10mm below table to next section

**Code Reference:** [drum_label_generator.py:201-243](../../drum_label_generator.py#L201-L243)

---

### 4. GHS Hazard Pictograms

**Location:** Below information table (y -= table_height + 10mm)

**Header:** "GHS Hazard Pictograms:" (Helvetica-Bold, 9pt)

**Pictogram Display:**
- Size: 20mm × 20mm (square)
- Spacing: 2mm between pictograms
- Layout: Horizontal row
- Maximum: 5 pictograms (space constraint)

**Data Source:**
- Column: `ghs_pictograms`
- Format: Comma-separated codes (e.g., "GHS02,GHS07,GHS09")
- Files: `ghs_pictograms/GHS01.png` through `GHS09.png`

**Rendering:**
- Loaded from PNG files via PIL
- Converted to ReportLab ImageReader
- Drawn with `preserveAspectRatio=True`
- Transparency supported via `mask='auto'`

**Configuration:**
```python
PICTOGRAM_SIZE = 20  # mm
PICTOGRAM_SPACING = 2  # mm
GHS_PICTOGRAM_FOLDER = "ghs_pictograms"
```

**Spacing:** 10mm below pictograms to next section

**Code Reference:** [drum_label_generator.py:245-272](../../drum_label_generator.py#L245-L272)

---

### 5. Hazard Statements

**Location:** Below GHS pictograms (y -= 10mm)

**Header:** "Hazard Statements:" (Helvetica-Bold, 9pt)

**Content:**
- Bulleted list of hazard codes and descriptions
- Font: Helvetica, 7pt
- Indent: 5mm from left margin

**Data Source:**
- Column: `hazard_statements`
- Format: Pipe-separated (e.g., "H315: Skin irritation|H319: Eye irritation")
- Rendered: Each statement on new line with bullet

**Example:**
```
Hazard Statements:
• H315: Causes skin irritation
• H319: Causes serious eye irritation
• H411: Toxic to aquatic life with long lasting effects
```

**Dynamic Height:** Based on number of statements

**Spacing:** 15mm below to next section

**Code Reference:** [drum_label_generator.py:274-285](../../drum_label_generator.py#L274-L285)

---

### 6. Precautionary Statements

**Location:** Below hazard statements (y -= dynamic)

**Header:** "Precautionary Statements:" (Helvetica-Bold, 9pt)

**Content:**
- Bulleted list of P-codes and instructions
- Font: Helvetica, 7pt
- Indent: 5mm from left margin

**Data Source:**
- Column: `precautionary_statements`
- Format: Pipe-separated (e.g., "P273: Avoid release|P280: Wear gloves")

**Example:**
```
Precautionary Statements:
• P273: Avoid release to environment
• P280: Wear protective gloves/eye protection
• P305+P351+P338: IF IN EYES rinse cautiously with water
```

**Dynamic Height:** Based on number of statements

**Spacing:** 15mm below to next section

**Code Reference:** [drum_label_generator.py:287-297](../../drum_label_generator.py#L287-L297)

---

### 7. Storage Instructions

**Location:** Below precautionary statements (y -= dynamic)

**Header:** "Storage:" (Helvetica-Bold, 9pt)

**Content:**
- Single line of storage guidance
- Font: Helvetica, 7pt
- Truncated to 80 characters
- Indent: 5mm from left margin

**Data Source:**
- Column: `storage_instructions`
- Example: "Store in cool dry place away from heat sources"

**Spacing:** 15mm below to next section

**Code Reference:** [drum_label_generator.py:299-308](../../drum_label_generator.py#L299-L308)

---

### 8. Emergency Contact

**Location:** Below storage instructions (y -= dynamic)

**Header:** "Emergency Contact:" (Helvetica-Bold, 9pt, RED #CC0000)

**Content:**
- Emergency phone number
- Font: Helvetica, 7pt, black
- Indent: 5mm from left margin

**Data Source:**
- Column: `emergency_contact`
- Example: "+61 1800 XXX XXX (24hr)"

**Styling:**
- Header in red to draw attention
- Content in black for readability

**Spacing:** 20mm below to barcode section

**Code Reference:** [drum_label_generator.py:310-321](../../drum_label_generator.py#L310-L321)

---

### 9. Barcode (Bottom Left)

**Location:** Variable y position (after all text content)

**Type:** Code128 (1D barcode)
**Content:** `product_code` + `batch_number` concatenated

**Dimensions:**
- Width: 70mm
- Height: 15mm

**Position:**
- Aligned to left margin (x = 8mm)
- Bottom section of label

**Configuration:**
```python
BARCODE_WIDTH = 70  # mm
BARCODE_HEIGHT = 15  # mm
```

**Barcode Options:**
```python
{
    'module_height': 10,
    'module_width': 0.2,
    'quiet_zone': 2,
    'font_size': 8,
    'text_distance': 2,
}
```

**Error Handling:**
- If barcode generation fails, section omitted
- Warning logged to console

**Code Reference:** [drum_label_generator.py:323-338](../../drum_label_generator.py#L323-L338)

---

### 10. QR Code (Bottom Right)

**Location:** Fixed bottom-right corner

**Type:** QR Code (2D)

**Content (default):**
- Format: `product_code|batch_number|manufacture_date`
- Or custom data from `qr_data` column

**Dimensions:**
- Size: 25mm × 25mm (square)

**Position:**
- X: Right margin - QR size = (148 - 8 - 25) = 115mm
- Y: Bottom margin = 8mm

**QR Settings:**
```python
{
    'version': 1,
    'error_correction': ERROR_CORRECT_L,
    'box_size': 10,
    'border': 2,
}
```

**Configuration:**
```python
QR_SIZE = 25  # mm
```

**Code Reference:** [drum_label_generator.py:340-359](../../drum_label_generator.py#L340-L359)

---

## Vertical Layout Logic

Labels are rendered **top-to-bottom** with dynamic spacing:

```
y_pos = 202mm (top of printable area)

y_pos -= 15   (company header)
y_pos -= 20   (spacing)
y_pos -= 15   (product name)
y_pos -= table_height + 10  (information table)
y_pos -= 15   (GHS header)
y_pos -= 20 + 10  (pictograms + spacing)
y_pos -= dynamic  (hazard statements)
y_pos -= dynamic  (precautionary statements)
y_pos -= dynamic  (storage instructions)
y_pos -= dynamic  (emergency contact)
y_pos -= 15   (barcode)

QR code at fixed position: y = 8mm
```

**Variable height:** y_pos tracks current vertical position as sections are added

## Color Scheme

**Primary:** Black text on white background
**Accent:** Red for emergency contact header (#CC0000)
**Borders:** Grey (0.5pt for table)
**Pictograms:** Full color (from PNG files)
**Barcodes/QR:** Black on white

## Font Usage

| Element | Font | Size |
|---------|------|------|
| Company name | Helvetica-Bold | 14pt |
| Company address | Helvetica | 7pt |
| Product header | Helvetica-Bold | 10pt |
| Table labels | Helvetica-Bold | 9pt |
| Table values | Helvetica | 9pt |
| Section headers | Helvetica-Bold | 9pt |
| Body text | Helvetica | 7pt |

## Data Truncation Rules

**To prevent overflow:**
- Product name: 60 characters max
- Storage instructions: 80 characters max
- Table values: Wrap within column width
- Long hazard/precautionary lists: Allowed to expand vertically

## Configuration Customization

### Increase Pictogram Size

Edit `config.py`:
```python
PICTOGRAM_SIZE = 25  # Was 20
```

### Adjust Table Column Widths

Edit `config.py`:
```python
LABEL_COL_WIDTH = 50  # Was 45
VALUE_COL_WIDTH = 90  # Was 95
```

### Change Fonts

Edit `config.py`:
```python
FONT_BODY = "Times-Roman"  # Was Helvetica
```

### Reduce Spacing

Edit `drum_label_generator.py` spacing constants:
```python
y_pos -= 10  # Was 15
```

## Print Considerations

**DPI:** Minimum 600 DPI for barcode readability
**Stock:** Durable weatherproof label material
**Color:** Full color required for GHS pictograms
**Cutting:** A5 size with 2mm bleed recommended
**Adhesive:** Permanent adhesive for drum application

## Responsive Behavior

**Long product names:** Truncated at 60 characters
**Missing data:** Sections omitted if data not present
**Many hazards:** List expands vertically (may push barcode down)
**Too many pictograms:** Limited to first 5 codes

**Overflow protection:** Not currently implemented (assumes reasonable data length)

## Related Files

- [config.py](../../config.py) - Layout configuration constants
- [drum_label_generator.py:168-363](../../drum_label_generator.py#L168-L363) - `create_label()` method
- [sample_data.csv](../../sample_data.csv) - Example data showing all sections
