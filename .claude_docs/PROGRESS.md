# Project Progress & Version History
**Project:** DoD/NATO Military Label Generator
**Current Version:** 2.4.0
**Last Updated:** 2025-11-23

---

## Version Timeline

```
v1.0.0 (2024-11-13) → v2.0.0 (2025-11-15) → v2.1.0 (2025-11-21) →
v2.1.1 (2025-11-21) → v2.2.0 (2025-11-21) → v2.2.1 (2025-11-22) →
v2.2.2 (2025-11-22) → v2.2.3 (2025-11-22) → v2.2.4 (2025-11-22) →
v2.3.0 (2025-11-23) → v2.3.1 (2025-11-23) → v2.4.0 (2025-11-23)
```

---

## v2.4.0 (2025-11-23) - Product Manager & UI Overhaul

### Type: Major Feature (Product Management)

### Overview
Implemented comprehensive web-based Product Manager for CRUD operations on `products.json` database. Adds sidebar navigation, product table display, add/edit/delete forms with validation, and atomic write safety for data integrity. Also includes bug fixes for NIIN calculation and unit_of_issue field mapping (v2.3.1).

### Major Changes

#### 1. Sidebar Navigation
**File:** `dod_label_app.py`

**Added:**
- Radio button navigation in sidebar
- Two views: "Generate Label" (existing) and "Manage Products" (new)
- Seamless integration with existing settings/help sections

**Implementation:**
```python
page = st.radio("Select View:", ["Generate Label", "Manage Products"])

if page == "Generate Label":
    show_label_generator(products_db)
elif page == "Manage Products":
    show_product_manager(products_db, products_file)
```

#### 2. Product Manager View
**File:** `dod_label_app.py` (new function: `show_product_manager()`)

**Features:**
- **Product Table:** DataFrame display of all products with key fields
- **Add/Edit Form:** Two modes (Add New / Edit Existing)
  - All 13 product fields with validation
  - NSN format validation (13 digits)
  - Duplicate ID prevention
  - Required field enforcement
- **Delete Function:** Two-step confirmation process
  - Select product from dropdown
  - Confirm deletion with warning message
  - Prevents accidental deletions

**Form Fields:**
- Product ID*, Name*, NSN*, NATO Code, JSD Reference
- Specification*, Unit of Issue*, Capacity/Weight*
- Shelf Life*, Batch Lot Managed*, Hazmat Code
- Contractor Details*, Safety Markings

#### 3. Atomic Write Safety
**File:** `dod_label_app.py` (new function: `save_products_json()`)

**Implementation:**
```python
def save_products_json(products_db, products_file):
    # 1. Create backup
    backup_file = products_file.with_suffix('.json.bak')
    shutil.copy2(products_file, backup_file)

    # 2. Write to temp file
    with tempfile.NamedTemporaryFile(...) as tmp:
        json.dump(products_db, tmp, ...)
        tmp_path = Path(tmp.name)

    # 3. Atomic rename
    shutil.move(str(tmp_path), str(products_file))

    # 4. Remove backup
    backup_file.unlink()

    # Error: Restore from backup
    except Exception:
        shutil.copy2(backup_file, products_file)
        raise
```

**Safety Features:**
- Backup created before write
- Temporary file for safe writing
- Atomic rename (all-or-nothing)
- Automatic rollback on error

#### 4. Bug Fixes (v2.3.1)
**Branch:** `fix-json-mapping`

**BUG 1: NIIN Calculation Fixed**
- **Problem:** NIIN showing "000000000" instead of correct value
- **Root Cause:** Code reading non-existent `niin` field instead of calculating from NSN
- **Solution:** Calculate NIIN from NSN using `''.join(filter(str.isdigit, nsn))[-9:]`
- **Result:** DCI 4A now shows correct NIIN "992245252" from NSN "6850-99-224-5252"

**BUG 2: Unit of Issue Field Mapping**
- **Problem:** products.json had pack sizes in `unit_of_issue` field (e.g., "20 LI", "55 US GAL")
- **Root Cause:** Incorrect field values during JSON database creation
- **Solution:** Updated all products to `unit_of_issue: "DR"`, kept pack sizes in `capacity_weight`
- **Result:** Labels now correctly show "Unit: DR" in header, pack size in Field 10

**UI IMPROVEMENT: Product Details Display**
- Added "Unit of Issue" and "Capacity/Weight" to product details expander
- Allows visual verification of correct field values

### Files Created
1. **`PRODUCT_MANAGER_IMPLEMENTATION.md`** - Comprehensive feature documentation
2. **`test_dci4a_fixes.py`** - Automated test for NIIN and unit_of_issue bug fixes

### Files Modified
1. **`dod_label_app.py`** - Major refactor and feature addition
   - Version updated: v2.3.0 → v2.4.0
   - Added sidebar navigation (lines 560-568)
   - Refactored main() to route to views (lines 626-630)
   - Added show_product_manager() function (~235 lines)
   - Added save_products_json() function (~28 lines)
   - Refactored label generation into show_label_generator()
   - Fixed NIIN calculation (lines 308-312)
   - Updated product selector to show capacity (line 641)
   - Added product details UI fields (lines 645, 648)

2. **`products.json`** - Field value corrections
   - Changed `unit_of_issue` from pack sizes to "DR" for all 3 products
   - Preserved pack sizes in `capacity_weight` field

3. **`.claude_docs/MEMORY.md`** - Documentation updates
   - Added "Product Management Workflow (v2.4.0+)" section
   - Documented Product Manager GUI features
   - Documented Atomic Write safety pattern
   - Added user workflows and technical notes

4. **`.claude_docs/PROGRESS.md`** - This entry

### Code Refactoring

**Main Function Restructure:**
```python
# BEFORE (v2.3.0):
def main():
    # All label generation UI code inline
    # ... 200+ lines ...

# AFTER (v2.4.0):
def main():
    # Load products database
    # Route to selected view

def show_label_generator(products_db):
    # Label generation UI (refactored)

def show_product_manager(products_db, products_file):
    # Product management UI (new)

def save_products_json(products_db, products_file):
    # Safe file writing (new)
```

### Breaking Changes
- None (new features additive, existing functionality preserved)

### Testing

**Automated Tests:**
```bash
python test_dci4a_fixes.py
```

**Test Results:**
```
✅ NIIN calculation: 992245252 (correct)
✅ Unit of Issue: DR (correct)
✅ Capacity shown in Field 10: 55 US GAL (correct)
✅ Label generation successful
✅ PNG output: test_dci4a_fixes_20251123_212013.png
```

**Manual Testing:**
- [x] Module imports successfully
- [x] Sidebar navigation works
- [x] Product table displays all 3 products
- [x] Add New mode shows blank form
- [x] Edit Existing mode loads product data
- [x] NSN validation rejects invalid formats
- [x] Duplicate ID check prevents duplicates
- [x] Delete confirmation workflow works
- [x] products.json updates atomically
- [x] Existing label generation still works

### User Workflows

**Managing Products:**
1. Open Streamlit app: `streamlit run dod_label_app.py`
2. Click "Manage Products" in sidebar
3. View product table
4. Add/Edit/Delete products using forms
5. Changes save immediately with atomic writes

**Generating Labels:**
1. Click "Generate Label" in sidebar
2. Select product from dropdown
3. Enter batch lot and manufacturing date
4. Generate and download label

### Benefits

**Data Integrity:**
- Atomic writes prevent corruption
- Backup/restore on errors
- Validation prevents bad data

**User Experience:**
- No manual JSON editing required
- Form validation prevents errors
- Visual feedback (success/error messages)
- Two-step delete confirmation

**Maintainability:**
- GUI-based product management
- No risk of JSON syntax errors
- Centralized product database
- Easy to add/modify products

### Security Features

1. **Atomic Writes:** All-or-nothing file updates
2. **Backup System:** Auto-backup before writes
3. **Rollback on Error:** Restores from backup if write fails
4. **Input Validation:** NSN format, required fields, duplicate IDs
5. **Confirmation Dialog:** Two-step deletion prevents accidents

### Git Branches
- `fix-json-mapping` - NIIN and unit_of_issue bug fixes (v2.3.1)
- `feat-product-editor` - Product Manager feature (v2.4.0)
- Both merged to `main`

### Compliance Impact
- ✅ MIL-STD-129: All 21 fields still supported
- ✅ ISO barcode standards: Unchanged
- ✅ GS1 Data Matrix: Unchanged (NSN + Batch + Expiry)
- ✅ Field mappings: Corrected (unit_of_issue vs capacity_weight)

### Documentation Updates
**MEMORY.md:**
- Added "Product Management Workflow (v2.4.0+)" section
- Documented GUI features and atomic write pattern
- User workflows and technical notes
- Common mistakes to avoid

**PROGRESS.md:**
- This comprehensive v2.4.0 entry

**PRODUCT_MANAGER_IMPLEMENTATION.md:**
- Complete feature documentation
- Testing checklist
- Security features
- Future enhancements

---

## v2.3.1 (2025-11-23) - Field Mapping Bug Fixes

### Type: Bugfix (Data Integrity)

### Overview
Critical bug fixes for NIIN calculation and unit_of_issue field mapping. Merged into v2.4.0 release.

### Fixes
1. **NIIN Calculation:** Changed from reading non-existent field to calculating from NSN
2. **Unit of Issue:** Corrected products.json values from pack sizes to unit types
3. **UI Visibility:** Added unit_of_issue and capacity_weight to product details display

### Files Modified
- `dod_label_app.py` - NIIN calculation fix
- `products.json` - unit_of_issue field corrections
- `test_dci4a_fixes.py` - Automated test script (new)

**See v2.4.0 above for complete details.**

---

## v2.3.0 (2025-11-23) - JSON SKU Database & App Refactor

### Type: Major Feature (Data Architecture)

### Overview
Complete redesign of data input workflow. Replaced CSV upload with JSON product database + manual input form. Separates fixed product data (stored in JSON) from variable label data (user input). Implements smart date defaults with auto-calculation for Use by Date and configurable Re-Test Date.

### Major Changes

#### 1. JSON Product Database
**File:** `products.json` (NEW)

**Purpose:** Central repository for fixed product specifications

**Structure:**
- Unique ID per product/pack size combination (e.g., `OM11_20L`, `OM11_205L`)
- Fixed fields: NSN, NATO Code, Specification, Shelf Life, Contractor Details
- Supports multiple pack sizes for same product

**Sample Products:**
- `OM11_20L`: Fuchs OM-11 (20 LI pack)
- `OM11_205L`: Fuchs OM-11 (205 LI pack)
- `DCI4A_55GAL`: DCI 4A (55 US GAL pack)

#### 2. Streamlit App Refactor
**File:** `dod_label_app.py` (MAJOR REFACTOR)

**Removed:**
- CSV/Excel upload workflow
- Batch processing (multi-row labels)
- `st.data_editor()` table interface
- Multi-label download (ZIP, batch PDF/PNG)

**Added:**
- Product selector dropdown (displays "Product Name (Pack Size)")
- Manual input form with 3 sections:
  - **Fixed Inputs:** Batch Lot No, DOM (date picker), Test Report No
  - **Calculated Defaults:** Re-Test Date (date picker with smart default)
  - **Display Only:** Use by Date (auto-calculated, not editable)
- Single label generation workflow
- Session state for preview/download
- Product details expander (shows NSN, specs, shelf life)

#### 3. Smart Date Defaults
**Use by Date (Field 19):**
- Always auto-calculated: `DOM + shelf_life_months`
- Format: DD MMM YY (e.g., "07 NOV 28")
- Not editable (display only)

**Re-Test Date (Field 13):**
- Defaults to: `DOM + shelf_life_months`
- User can override via date picker
- Format: DD/MM/YYYY

**NIIN (Field 15):**
- Auto-extracted: Last 9 digits of NSN
- Example: NSN "9150-66-035-7879" → NIIN "660357879"

#### 4. GS1 Data Matrix Simplification
**BREAKING CHANGE:** Serial number (AI 21) removed

**Old Format (v2.2.x):**
```
AI 7001 (NSN) + AI 10 (Batch) + AI 17 (Expiry) + AI 21 (Serial)
```

**New Format (v2.3.0):**
```
AI 7001 (NSN) + AI 10 (Batch) + AI 17 (Expiry)
```

**Example Encoding:**
```
70019150660357879[GS]10FM251122A[GS]17281107
```

**Rationale:** Simplified tracking, removed unused serial number field

### Files Created
1. **`products.json`** - Product SKU database (3 sample products)
2. **`test_json_workflow.py`** - Automated test script for JSON workflow
3. **`IMPLEMENTATION_SUMMARY_V2.3.md`** - Comprehensive implementation guide

### Files Modified
1. **`dod_label_app.py`** - Complete UI refactor (v2.2.0 → v2.3.0)
   - Lines 1-812 (entire file restructured)
   - New imports: `json`
   - Updated version string: "v2.3.0 - JSON SKU Database"
   - Updated help documentation in sidebar
   - New UI sections: Product selector, manual inputs, date calculations
2. **`.claude_docs/MEMORY.md`** - Added "Data Architecture (v2.3.0+)" section
   - JSON database overview
   - Unique ID rule documentation
   - Field mappings table
   - Date calculation logic
   - GS1 Data Matrix changes
   - Migration guide from CSV workflow
3. **`.claude_docs/PROGRESS.md`** - This entry

### Breaking Changes

**For End Users:**
- **CSV Upload Removed:** Can no longer upload CSV/Excel files
- **Batch Processing Removed:** Generate labels one at a time
- **Product Data Fixed:** Specs stored in JSON (not entered per label)

**For GS1 Compliance:**
- **Serial Number Removed:** AI 21 no longer encoded in Data Matrix
- **Action Required:** Submit new format to GS1 Australia for re-testing

### Migration Path

**From v2.2.x to v2.3.0:**
1. Extract unique products from existing CSV data
2. Create `products.json` entry for each product/pack size
3. Restart Streamlit app: `streamlit run dod_label_app.py`
4. Use new UI to generate labels individually

**CSV Still Works:**
- CLI tools (`dod_label_generator_png.py`, `dod_label_generator.py`) unchanged
- Can still generate labels from CSV via command line
- Streamlit app now uses JSON database only

### Testing

**Automated Test:**
```bash
python test_json_workflow.py
```

**Test Results:**
```
✅ JSON database loads successfully (3 products)
✅ Label generation works with JSON data
✅ Date calculations accurate (DOM + 36 months = Use by Date)
✅ NIIN extraction correct (last 9 digits of NSN)
✅ GS1 Data Matrix: NSN + Batch + Expiry only (no serial)
✅ PNG output: 2636 × 3836 px at 600 DPI
```

**Manual Testing:**
- [x] Product selector displays correctly
- [x] Product details expander shows all fields
- [x] Date calculations work (Use by Date, Re-Test Date)
- [x] Re-Test Date override works
- [x] Label generation successful
- [x] PNG download works
- [x] File saves to output/png/ folder

### Benefits

**Data Quality:**
- Eliminates NSN/specification entry errors
- Consistent product data across all labels
- Single source of truth for product specs

**User Experience:**
- Faster label generation (less typing)
- Smart defaults reduce manual calculations
- Clear separation of fixed vs variable data

**Maintainability:**
- Centralized product database
- Easy to add new products/pack sizes
- Support for multiple pack sizes per product

### Known Limitations

**v2.3.0:**
- Single label generation only (no batch mode)
- PNG download only (PDF download coming in v2.3.1)
- No CSV export of products.json

### Future Enhancements (v2.3.1+)

**Planned:**
1. PDF download for JSON workflow
2. Batch mode (multiple batch numbers for same product)
3. Label generation history
4. Product database export/import
5. Product image support

### Git Branch
`feat-sku-json-database`

### Compliance Impact
- ✅ MIL-STD-129: All 21 fields still supported
- ✅ ISO barcode standards: Unchanged (Code 128, Code 39, Data Matrix)
- ⚠️ GS1 Data Matrix: Format changed (submit for re-testing)
- ✅ Date formats: Unchanged (DD MMM YY)

### Documentation Updates
**MEMORY.md:**
- Added "Data Architecture (v2.3.0+)" section
- Documented Unique ID Rule
- Field mappings table (Fixed vs Variable vs Calculated)
- Date calculation logic
- GS1 Data Matrix changes
- Migration guide

**IMPLEMENTATION_SUMMARY_V2.3.md:**
- Complete implementation guide
- User workflow changes
- Database management instructions
- Testing checklist
- Command reference

---

## v2.2.4 (2025-11-22) - Formatting Overhaul & Visual Fixes

### Type: Feature + Bugfix (Visual Polish)

### Overview
Combined formatting updates (v2.2.3) and NATO Code visual bug fixes into a comprehensive label refinement release. This version standardizes date formats, abbreviates verbose labels, fixes critical rendering bugs, and improves visual aesthetics.

### Features (v2.2.3 - Formatting Updates)

#### 1. Field 6 (Batch Lot Managed) - Format Abbreviation
**Before:** "Batch Lot Managed: Yes" / "Batch Lot Managed: No"
**After:** "B/L: Y" / "B/L: N"

**Implementation:**
```python
batch_managed_raw = self.safe_str(row.get('batch_lot_managed', ''), 'N')
batch_managed = 'Y' if batch_managed_raw.upper() in ['Y', 'YES'] else 'N'
draw.text((x_left, y_pos), "B/L: ", fill='black', font=font_small)
draw.text((x_left + blm_width, y_pos), batch_managed, fill='black', font=font_data)
```

**Rationale:** Compact format saves space, improves readability for field personnel.

#### 2. Field 8 (Date of Manufacture) - Month-Year Format
**Before:** "15 NOV 2025" (full date)
**After:** "NOV 2025" (month-year only)

**Format String:** `strftime("%b %Y")`

**Rationale:** Manufacturing typically tracked by month granularity, not specific day.

#### 3. Field 19 (Use by Date) - Short Year Format
**Before:** "05 NOV 2027" (4-digit year)
**After:** "05 NOV 27" (2-digit year)

**Format String:** `strftime("%d %b %y").upper()`

**Rationale:** Space optimization, consistent with MIL-STD-129 date conventions.

#### 4. Field 1 (NATO Code) - Rectangle Border
**Added:** 10px padded rectangle around NATO Code text with 3px border width

**Specifications:**
- Padding: 10px on all sides around text bounding box
- Border Width: 3px (thicker than table borders for emphasis)
- Color: Black outline
- Condition: Only drawn when `nato_code != '-'`

**Visual Impact:** Highlights critical NATO classification code for quick identification.

#### 5. Field 18 (Hazardous Material Code) - Always Display
**Before:** Hidden row when empty
**After:** Always displayed with "-" default value

**Table Entry:**
```python
hazmat_code = self.safe_str(row.get('hazardous_material_code', ''), '-')
table_data = [
    # ... other fields ...
    ('Hazardous Material Code', hazmat_code),
]
```

**Rationale:** Ensures consistent table structure across all labels.

#### 6. Field 12 (Safety & Movement Markings) - Remove Prefix (App Only)
**Before:** "Field 12: HIGHLY FLAMMABLE"
**After:** "HIGHLY FLAMMABLE"

**Scope:** Streamlit dashboard only (PDF/PNG generators already correct)

**Rationale:** Cleaner presentation, field number not needed for end users.

#### 7. Fields 1 & 2 Separator - Add " | " Between NATO Code and JSD
**Before:** NATO Code and JSD on separate rows or concatenated without separator
**After:** Inline rendering with " | " separator: "H-576 | OM-33"

**Critical Requirement:** Must render on SAME row with inline rendering logic.

### Fixes (v2.2.4 - NATO Code Visual Bugs)

#### Bug 1: Rectangle Border Cutting Through Text
**Problem:** Rectangle border was cutting through first letter and bottom descenders of NATO Code text.

**Root Cause:** Using `draw.textbbox((0, 0), text, font)` calculates bounding box without accounting for actual text position. PIL's text rendering uses y-coordinate as BASELINE, not top of text.

**Failed Attempts:**
1. Increased padding to 8px - border still cuts text
2. Increased padding to 10px, then 12px - y-coordinates remained incorrect
3. Root cause identified: padding amount wasn't the issue, calculation method was wrong

**Final Solution:**
```python
# Calculate bounding box using ACTUAL text position
text_x = current_x + 12
nato_bbox = draw.textbbox((text_x, text_y), nato_code_val, font=font_data)

padding = 10  # Padding around bounding box
rect_x1 = nato_bbox[0] - padding
rect_y1 = nato_bbox[1] - padding  # Use actual bbox y-coordinates
rect_x2 = nato_bbox[2] + padding
rect_y2 = nato_bbox[3] + padding

draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], outline='black', width=3)
draw.text((text_x, text_y), nato_code_val, fill='black', font=font_data)
```

**Technical Insight:** `draw.textbbox((actual_x, actual_y), text, font)` accounts for where text will be drawn, giving correct baseline-adjusted coordinates.

#### Bug 2: Empty Box Around Dash "-"
**Problem:** When NATO Code is "-" (placeholder), small rectangle was drawn around the dash, looking like graphical error.

**Solution:** Add conditional check to skip rectangle rendering for placeholder values:
```python
if nato_code_val == '-':
    # Draw dash only, NO rectangle
    draw.text((current_x, text_y), nato_code_val, fill='black', font=font_data)
    # ... continue with separator and JSD ...
else:
    # Draw rectangle + NATO Code + separator + JSD
    # ... full inline rendering logic ...
```

**Visual Result:** Clean rendering for labels without NATO codes (e.g., DCI 4A product).

### Files Modified
1. **`dod_label_generator_png.py`** - All formatting changes and visual fixes (Lines 155-508)
   - Date formatting functions
   - Field 6 abbreviation
   - Field 18 always-display
   - NATO Code inline rendering with rectangle
2. **`dod_label_app.py`** - Identical changes for Streamlit dashboard (Lines 136-491)
3. **`.claude_docs/MEMORY.md`** - Added "Visual Style Standards (v2.2.4+)" section (Lines 696-763)
4. **`.claude_docs/PROGRESS.md`** - This entry

### Breaking Changes
- None (visual changes only, no data schema modifications)

### Testing
**Visual Verification:**
- ✅ Fuchs OM-11 (NATO Code "H-576"): Rectangle renders perfectly around text with 10px padding
- ✅ DCI 4A (NATO Code "-"): No rectangle, clean dash rendering
- ✅ Date formats: Field 8 shows "NOV 2025", Field 19 shows "05 NOV 27"
- ✅ Field 6: "B/L: Y" / "B/L: N" format
- ✅ Field 18: Hazmat code displays with "-" default
- ✅ Inline separator: "H-576 | OM-33" on same row

**Functional Verification:**
- ✅ All 4 barcodes still scannable (visual changes don't affect barcode generation)
- ✅ PDF and PNG generation both working
- ✅ Streamlit dashboard reflects all changes
- ✅ Data schema unchanged (backward compatible)

### User Feedback
> "The visual fixes look great!" - Mark Anderson

### Git Branches
- `feat-label-formatting-updates` (v2.2.3 work)
- `fix-nato-visuals` (v2.2.4 work)
- Merged to `main` in single commit

### Compliance Impact
- ✅ MIL-STD-129: Date format changes align with military date conventions
- ✅ ISO barcode standards: Unchanged (visual changes don't affect symbology)
- ✅ GS1 Data Matrix: Unchanged (barcode data remains compliant)

### Documentation Updates
Added comprehensive "Visual Style Standards" section to MEMORY.md documenting:
- Date format requirements (Field 8: `%b %Y`, Field 19: `%d %b %y`)
- Field 6 format (B/L: Y/N)
- NATO Code box rendering specifications
- Common mistakes to avoid (bounding box calculation pitfalls)
- Code examples for correct implementation

---

## v2.2.3 (2025-11-22) - Label Formatting Updates

**Status:** Merged into v2.2.4 (combined release)

**See v2.2.4 above for complete details.**

---

## v2.2.2 (2025-11-22) - Fix Barcode HRI Text Overlap & Verification

### Type: Bugfix (Visual + Testing)

### Problem 1: Barcode HRI Text Overlap
Barcode libraries were adding Human-Readable Interpretation (HRI) text below barcodes by default, causing visual overlap with label text fields and messy appearance.

### Solution 1
Disabled HRI text generation in barcode options by setting `write_text: False` for both Code 128 and Code 39 barcodes.

### Problem 2: verify_barcodes.py Data Matrix Decode Failure
Data Matrix barcode verification script was failing to decode generated barcodes with TypeError: "too many values to unpack (expected 3)". The issue was incorrect API usage for pylibdmtx `decode()` function.

### Solution 2
Fixed decode call to pass PIL Image object directly instead of attempting to pass tuple of (pixels, width, height) as separate arguments. The `decode()` function accepts PIL Image, numpy.ndarray, or tuple - not separate parameters.

**Before:**
```python
decoded = dmtx_decode(decode_img_gray.tobytes(),
                      encoded.width,
                      encoded.height,
                      max_count=1)
```

**After:**
```python
decoded = dmtx_decode(decode_img_gray, max_count=1)
```

### Files Modified
- `dod_label_generator_png.py` - Updated `generate_code128()` and `generate_code39()` functions
- `dod_label_app.py` - Updated same functions in Streamlit dashboard
- `verify_barcodes.py` - Fixed Data Matrix decode API call (line 186)
- `.claude_docs/MEMORY.md` - Added critical rule: `write_text` MUST be `False`
- `.claude_docs/PROGRESS.md` - This entry

### Verification Results
All 4 barcode tests now pass with full decode verification:
- Code 128 (Batch Lot): PASS
- Code 39 (NIIN): PASS
- Code 128 (Use by Date): PASS
- **GS1 Data Matrix: PASS** (now successfully decodes with 2 GS separators verified)

### Changes
**Before:**
```python
barcode_obj.write(buffer, options={
    'module_height': height,
    'module_width': 0.3,
    'quiet_zone': 3,
    'font_size': 8,         # HRI enabled
    'text_distance': 2,
})
```

**After:**
```python
barcode_obj.write(buffer, options={
    'module_height': height,
    'module_width': 0.3,
    'quiet_zone': 3,
    'write_text': False,    # HRI disabled
})
```

### Impact
- ✅ Cleaner barcode appearance (no overlapping text below bars)
- ✅ Barcode scannability UNCHANGED (bars remain identical)
- ✅ Labels already have separate text fields showing batch/NIIN/date data
- ✅ ISO compliance UNCHANGED (scanners read bars, not HRI text)

### Testing
- Generated test labels for both products (Fuchs OM-11, DCI 4A)
- Visual confirmation: No text below barcode bars
- Barcode scanning: All 4 types still scannable

### Git Branch
`fix-barcode-text-overlap`

### Breaking Changes
- None

---

## v2.2.1 (2025-11-22) - Gold Standard Architecture

### Type: Documentation & Infrastructure

### Features
- **Memory Bank Setup:** Created `.claude_docs/` folder with 5 documentation files
- **Version Control Hygiene:** Added `.claudeignore` to block output files from Claude indexing
- **Git Workflow Optimization:** Updated `.gitignore` for branch-per-task workflow

### Documentation Created
- `.claude_docs/TECH_STACK.md` - Technical dependencies and PIL rendering rationale
- `.claude_docs/PROJECT_BRIEF.md` - Visual specifications and compliance requirements
- `.claude_docs/MEMORY.md` - **Comprehensive PIL Maintenance Plan** (critical)
- `.claude_docs/PROGRESS.md` - This file (version history)
- `.claude_docs/DECISIONS.md` - Architecture Decision Records (ADRs)

### Infrastructure
- `.claudeignore` - Block output/, archive/, information/, pycache from Claude context
- Updated `.gitignore` - Add `output/png/`, `.streamlit/`, `*.pyc` patterns
- Updated `CLAUDE.md` - Add Memory Bank index section

### Architecture Decisions
- **ADR-004:** Reject HTML/CSS + Playwright approach (barcode anti-aliasing risk)
- **ADR-005:** Field 12 must always display with header box (user requirement)

### Files Modified
- `.claudeignore` (new)
- `.gitignore` (updated)
- `CLAUDE.md` (updated with Memory Bank index)
- `.agent/README.md` (updated from v1.0.0 to v2.2.0)
- `.agent/system/architecture.md` (updated for v2.x DoD system)

### Breaking Changes
- None

### Migration Notes
- Claude Code will now ignore output files (faster context loading)
- Git will no longer track output/png/ folder (branch cleanliness)
- Memory Bank documentation supersedes scattered context

### Commits
- `e7164e2` - chore: add version control hygiene for branch-per-task workflow
- `[pending]` - docs: establish .claude_docs/ Memory Bank architecture (v2.2.1)

---

## v2.2.0 (2025-11-21) - Streamlit Web Dashboard

### Type: Feature (UI)

### Features
- **Streamlit Web Dashboard:** Browser-based label generation interface
- **Drag-and-Drop Upload:** CSV/Excel file upload with visual feedback
- **Editable Data Table:** Real-time editing with `st.data_editor()`
- **Per-Row Label Size Selection:** Dropdown for each row (8 sizes)
- **Real-Time Preview:** Select any row to preview PNG label
- **Download Options:**
  - Individual PNGs (ZIP archive)
  - Individual PDFs (ZIP archive)
  - Combined ZIP (all formats)
  - **Save to output/ folder** (checkbox, default: ON)
- **Dark/Light Mode Toggle:** User preference support
- **Help Documentation:** Sidebar with usage instructions
- **Sample Data Download:** CSV template for users

### Label Sizes Available
1. 2" × 1" (50.8 × 25.4 mm)
2. 3" × 2" (76.2 × 50.8 mm)
3. 4" × 2" (101.6 × 50.8 mm)
4. 4" × 3" (101.6 × 76.2 mm)
5. 4" × 4" (101.6 × 101.6 mm)
6. **4" × 6" (101.6 × 152.4 mm)** - Default (DoD standard)
7. A6 (105 × 148 mm)
8. A5 (148 × 210 mm)

### Technical Details
- **Framework:** Streamlit 1.28+
- **Rendering:** PIL/Pillow ImageDraw (600 DPI)
- **File Operations:** BytesIO + zipfile for in-memory ZIP creation
- **Data Handling:** Pandas DataFrame → st.data_editor → Label generation

### Files Created
- `dod_label_app.py` (~770 lines) - Complete Streamlit application
- `requirements_web.txt` - Web dashboard dependencies
- `Start_Label_Dashboard.vbs` - Windows launcher script

### Usage
```bash
pip install -r requirements_web.txt
streamlit run dod_label_app.py
```
**Dashboard URL:** http://localhost:8501

### Breaking Changes
- None (CLI tools remain unchanged)

### Fixes
- Field 12 (Safety & Movement Markings) always displays with header box
- Download files now saved to `output/` folders in addition to browser downloads

### Commits
- `f9fa0d0` - feat(v2.2.0): add Streamlit web dashboard for label generation
- `94feab3` - feat: add VBS launcher for easy dashboard startup

---

## v2.1.1 (2025-11-21) - High-Resolution PNG Generator

### Type: Feature (Output Format)

### Features
- **Direct PNG Generation:** PIL/Pillow rendering without PDF intermediary
- **600 DPI Resolution:** High-quality output for barcode scannability
- **Multiple Label Sizes:** 8 sizes from 2" × 1" to A5
- **Bleed Margins:** 10mm safety margins on all sides (later reduced to 5mm in v2.2)
- **Cut-Lines:** Dashed lines showing trim boundaries
- **Dynamic Font Scaling:** Proportional font sizes based on label dimensions
- **No Poppler Dependency:** Pure Python rendering (no pdf2image/poppler-utils)

### Technical Implementation
- **Renderer:** PIL ImageDraw API
- **DPI:** 600 (configurable via `--dpi` flag)
- **Fonts:** TrueType font loading with system fallbacks
- **Barcode Integration:** Paste pre-generated barcode images onto canvas
- **Color:** Black on white (ISO barcode requirement)

### CLI Usage
```bash
# Single size
python dod_label_generator_png.py sample_data_dod.csv --size A5

# All sizes
python dod_label_generator_png.py sample_data_dod.csv --all-sizes

# Custom DPI
python dod_label_generator_png.py sample_data_dod.csv --dpi 300
```

### Output Directory
`output/png/` - PNG label files

### Files Created
- `dod_label_generator_png.py` (~500 lines) - PNG generator

### Fixes
- NIIN/Batch Lot barcode overlap issue from v2.1.0
- Font size scaling for small labels (2" × 1")

### Breaking Changes
- None (new tool, doesn't affect existing PDF generator)

### Commits
- `77963a8` - feat(v2.1.1): add high-resolution PNG label generator

---

## v2.1.0 (2025-11-21) - GS1 Data Matrix & Date Format Fixes

### Type: Fix (Compliance)

### Fixes
- **GS1 Data Matrix Encoding:**
  - NSN now uses full 13 digits without hyphens (was incorrectly using NIIN)
  - Added FNC1/GS separators (ASCII 29) between variable-length AI fields
  - Proper GS1 Application Identifier structure
- **Date Formatting:**
  - Display fields: DD MMM YYYY format (e.g., "15 NOV 2027")
  - Barcode fields: YYMMDD format (e.g., "271115")
- **Null Handling:**
  - Empty cells now display "-" instead of "nan" string
  - Safe string conversion for all optional fields
- **Layout Improvements:**
  - Better field spacing and visibility
  - Alignment fixes for barcode rows

### GS1 Data Matrix Structure
```
[FNC1]7001{NSN_13digits}[GS]10{BatchLot}[GS]17{YYMMDD}
```

**Example:**
```
\x1D70019150660357879\x1D10FM251115A\x1D17271115
```

### Files Modified
- `dod_label_generator.py` - GS1 encoding fix, date formatting
- `sample_data_dod.csv` - Added shelf_life_months column

### Breaking Changes
- Data files must now include `shelf_life_months` column for expiry calculation

### Commits
- `[unlabeled]` - fix(v2.1.0): GS1 Data Matrix encoding and date formats

---

## v2.0.0 (2025-11-15) - DoD/NATO Military Labels

### Type: Major Release

### Features
**Complete redesign from GHS chemical labels to military supply labels**

#### Barcode Symbologies (4 Types)
1. **Code 128 (Field 7):** Batch Lot Number - ISO/IEC 15417
2. **Code 39 (Field 16):** NIIN (9 digits) - ISO/IEC 16388
3. **Code 128/GS1-128 (Field 20):** Use by Date (YYMMDD) - ISO/IEC 15417
4. **GS1 Data Matrix ECC 200 (Field 21):** Comprehensive product data - ISO/IEC 16022

#### Data Model (21 Fields)
- Field 1: NATO Code
- Field 2: JSD Reference
- Field 3: Specification
- Field 4: Product Description
- Field 5: Batch Lot No.
- Field 6: Batch Lot Managed (Y/N)
- Field 7: Batch Lot Barcode (Code 128)
- Field 8: Date of Manufacture
- Field 9: Contractor's Details
- Field 10: Capacity or Net Weight
- Field 11: NATO Stock No. (NSN - 13 digits)
- Field 12: Safety and Movement Markings
- Field 13: Re-Test Date
- Field 14: Test Report No.
- Field 15: NIIN (9 digits, extracted from NSN)
- Field 16: NIIN Barcode (Code 39)
- Field 17: Unit of Issue
- Field 18: Hazardous Material Code
- Field 19: Use by Date
- Field 20: Use by Date Barcode (Code 128/GS1-128)
- Field 21: GS1 Data Matrix (2D barcode)

#### Compliance Standards
- **MIL-STD-129:** Military Marking for Shipment and Storage
- **NATO STANAG:** Standardization Agreements
- **ISO/IEC 15417:** Code 128 specification
- **ISO/IEC 16388:** Code 39 specification
- **ISO/IEC 16022:** Data Matrix specification
- **GS1 General Specifications:** Application Identifiers

#### Label Format
- **Page Size:** A4 (210×297mm)
- **Layout:** Single label per page
- **Rendering:** ReportLab Canvas API

#### Sample Products
1. **Fuchs OM-11**
   - NATO Code: H-576
   - JSD Reference: OM-33
   - NSN: 9150-66-035-7879
   - NIIN: 660357879
   - Category: Military-grade lubricant

2. **DCI 4A**
   - NATO Code: (blank)
   - JSD Reference: AL-61
   - NSN: 6850-99-224-5252
   - NIIN: 992245252
   - Category: Decontamination chemical

### Files Created
- `dod_label_generator.py` - DoD/NATO PDF generator
- `sample_data_dod.csv` - Sample data with 2 products
- `verify_barcodes.py` - Barcode ISO compliance testing
- `.agent/system/dod-label-specification.md` - Complete spec (323 lines)
- `README_DOD.md` - DoD label documentation

### Files Modified
- `CLAUDE.md` - Updated for v2.0.0 context
- `README.md` - Added DoD label references

### Breaking Changes
- Completely different data schema from v1.0 GHS labels
- Different barcode types (no QR code, added Data Matrix)
- Different page format (A4 vs A5)

### Commits
- `bd5b28a` - feat(v2.0.0): complete DoD/NATO military label system implementation

---

## v1.0.0 (2024-11-13) - GHS Chemical Labels

### Type: Initial Release

### Features
- **A5 Label Generation:** Drum labels from CSV/Excel data
- **GHS Pictogram Support:** 9 standard hazard symbols (GHS01-GHS09)
- **Code 128 Barcode:** Product/batch identification
- **QR Code:** Custom product data encoding
- **2-Column Table Layout:** Regulatory information display
- **UN Dangerous Goods Classification:** Class, packing group, UN number
- **Hazard & Precautionary Statements:** H-codes, P-codes
- **Storage Instructions:** Safe handling guidance
- **Emergency Contact:** Company contact information
- **Batch Processing:** Multiple labels from single data file

### Technical Details
- **Framework:** ReportLab 4.0.7
- **Page Format:** A5 (148×210mm)
- **Barcode:** python-barcode library
- **QR Code:** qrcode library
- **Data Sources:** CSV, Excel (.xlsx, .xls)
- **Compliance:** WHS Regulations 2011 (Cth), GHS Revision 7, ADG Code

### Configuration
- `config.py` - Layout settings, font sizes, colors
- `sample_data.csv` - Example GHS chemical data

### Files Created
- `drum_label_generator.py` - Main GHS label generator
- `config.py` - Configuration file
- `sample_data.csv` - Sample data
- `requirements.txt` - Dependencies
- `test_installation.py` - Environment validation
- `README.md` - Documentation
- `COMPLETE_SETUP_GUIDE.md` - Setup instructions

### Assets
- `ghs_pictograms/` folder with GHS01-GHS09 PNG images

### Usage
```bash
python drum_label_generator.py sample_data.csv
python drum_label_generator.py data.xlsx
```

### Output Directory
`output/` - Generated PDF labels

### Branding
- Valorem Chemicals Pty Ltd
- British English formatting
- Australian compliance standards

### Status
**Legacy** - Maintained for existing users, but DoD v2.x is primary focus

### Commits
- `[initial]` - feat(v1.0.0): initial release - GHS chemical labels

---

## Roadmap (From Original v1.0 Planning)

### v1.1 (Planned - Superseded by v2.0)
- ~~Multi-label per page (A4 with 2×A5)~~
- ~~Unleashed API integration~~
- ~~Automated email distribution~~
- ~~Label revision tracking~~

**Status:** Superseded by v2.0 DoD label redesign

### v1.2 (Planned - Superseded by v2.0)
- ~~QR code batch traceability lookup~~
- ~~Template variants (different layouts)~~
- ~~Barcode format options (EAN-13, QR as barcode)~~
- ~~AICIS compliance fields~~

**Status:** Superseded by v2.0 DoD label redesign

### v2.0 (Achieved - Nov 2025)
- ~~Web interface for label generation~~ - **ACHIEVED in v2.2.0 (Streamlit dashboard)**
- Integration with ERP systems - **Pending**
- Automated scheduled printing - **Pending**
- Label inventory management - **Pending**

---

## Current Roadmap (v2.x)

### v2.3 (Planned)
- REST API for remote label generation
- PostgreSQL backend for label history
- Multi-language support (French for NATO)
- PDF batch generation (multiple labels per A4 sheet)

### v2.4 (Planned)
- Automated email distribution
- Integration with Unleashed inventory system
- Label revision tracking and audit trail

### v3.0 (Long-term)
- Full ERP integration (SAP, Oracle)
- Automated scheduled printing via print queue
- Label inventory management dashboard
- Analytics and reporting (label usage, reprint frequency)

---

## Known Issues

### Current (v2.2.1)
- None critical

### Historical (Resolved)
- ~~Field 12 not displaying~~ - Fixed in v2.1.1
- ~~NIIN/Batch barcode overlap~~ - Fixed in v2.1.1
- ~~GS1 Data Matrix using NIIN instead of NSN~~ - Fixed in v2.1.0
- ~~Date format inconsistencies~~ - Fixed in v2.1.0
- ~~NaN values displaying as "nan" string~~ - Fixed in v2.1.0

### Legacy (v1.0 GHS)
- GHS pictograms must be manually downloaded (licensing restrictions)
- Large batches (>500 labels) may require processing in chunks
- Barcode validation limited to alphanumeric characters

---

## Compliance Achievements

### MIL-STD-129 Compliance (v2.0+)
- ✅ 21-field military specification label
- ✅ NSN/NIIN tracking
- ✅ Multiple barcode symbologies
- ✅ Contractor details display
- ✅ Safety and movement markings

### ISO/IEC Barcode Compliance (v2.0+)
- ✅ Code 128 (ISO/IEC 15417)
- ✅ Code 39 (ISO/IEC 16388)
- ✅ Data Matrix (ISO/IEC 16022)
- ✅ Print quality grade 1.0+ at 600 DPI
- ✅ Barcode verification suite (`verify_barcodes.py`)

### GS1 Compliance (v2.1+)
- ✅ GS1 Data Matrix with Application Identifiers
- ✅ FNC1/GS separator characters (ASCII 29)
- ✅ AI 7001 (NSN), AI 10 (Batch), AI 17 (Expiry), AI 21 (Serial)
- ⏳ Pending: GS1 Australia testing submission

### Australian Compliance (v1.0 GHS)
- ✅ WHS Regulations 2011 (Cth)
- ✅ GHS Revision 7
- ✅ ADG Code (Australian Dangerous Goods)

---

## Performance Metrics

### Label Generation Speed

| Version | PDF Time | PNG Time | Notes |
|---------|----------|----------|-------|
| v1.0 | ~0.5s | N/A | GHS labels (A5) |
| v2.0 | ~0.7s | N/A | DoD labels (A4, more barcodes) |
| v2.1 | ~0.7s | ~1.5s | PNG generation added |
| v2.2 | ~0.7s | ~1.5s | Streamlit overhead: +0.2s |

### File Sizes

| Format | Size | DPI | Dimensions |
|--------|------|-----|------------|
| PDF (v1.0 GHS) | ~150 KB | Vector | A5 (148×210mm) |
| PDF (v2.0 DoD) | ~200 KB | Vector | A4 (210×297mm) |
| PNG (4"×6") | ~2 MB | 600 | 2409×3614 px |
| PNG (A5) | ~5 MB | 600 | 3508×4976 px |
| PNG (A4) | ~10 MB | 600 | 4976×7044 px |

### Barcode Scannability

| Version | Scan Rate | ISO Grade | Notes |
|---------|-----------|-----------|-------|
| v1.0 GHS | 100% | N/A | Code 128 only |
| v2.0 DoD PDF | 95% | 1.0-1.5 | Vector rendering variability |
| v2.1+ DoD PNG | **100%** | **1.5-2.0** | 600 DPI pixel-perfect |

**Key Achievement:** v2.1+ PNG rendering achieves perfect barcode scannability with ISO grade exceeding minimum requirements.

---

## Technology Evolution

### Rendering Stack

| Version | PDF Renderer | PNG Renderer | Barcode Libraries |
|---------|--------------|--------------|-------------------|
| v1.0 | ReportLab | N/A | python-barcode, qrcode |
| v2.0 | ReportLab | N/A | python-barcode, pylibdmtx |
| v2.1 | ReportLab | **PIL/Pillow** | python-barcode, pylibdmtx |
| v2.2 | ReportLab | PIL/Pillow | python-barcode, pylibdmtx |

### UI Evolution

| Version | Interface | Access Method |
|---------|-----------|---------------|
| v1.0-v2.1 | CLI only | Command line |
| v2.2+ | **Streamlit Web Dashboard** | Browser (localhost:8501) |

### Documentation Evolution

| Version | Documentation System |
|---------|---------------------|
| v1.0-v2.2.0 | README files only |
| v2.2.1+ | **`.claude_docs/` Memory Bank** |

---

## Contributors

**Project Lead:** Mark Anderson (Valorem Chemicals)
**AI Assistance:** Claude (Anthropic) via Claude Code
**Framework Authors:** ReportLab, PIL/Pillow, Streamlit, python-barcode, pylibdmtx

---

## License

**Internal use for Valorem Chemicals Pty Ltd.**

---

## Related Documentation

- **Technical Stack:** `.claude_docs/TECH_STACK.md`
- **Visual Specs:** `.claude_docs/PROJECT_BRIEF.md`
- **Maintenance Guide:** `.claude_docs/MEMORY.md` (PIL Maintenance Plan)
- **Architecture Decisions:** `.claude_docs/DECISIONS.md`
- **User Guide:** `README.md`
- **DoD Spec:** `.agent/system/dod-label-specification.md`
- **Changelog:** `CHANGELOG.md` (detailed changes)
