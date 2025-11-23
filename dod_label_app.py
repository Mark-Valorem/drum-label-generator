#!/usr/bin/env python3
"""
DoD/NATO Label Generator - Streamlit Web Dashboard
Generates military specification labels with web interface
Version 2.3.0 - JSON SKU Database
"""

import os
import io
import json
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

import barcode
from barcode.writer import ImageWriter
from pylibdmtx.pylibdmtx import encode as dmtx_encode

# Try to import ReportLab for PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# =============================================================================
# CONFIGURATION
# =============================================================================

# Label sizes in mm (width x height) - user-requested order
LABEL_SIZES = {
    '2" × 1"': (50.8, 25.4),
    '3" × 2"': (76.2, 50.8),
    '4" × 2"': (101.6, 50.8),
    '4" × 3"': (101.6, 76.2),
    '4" × 4"': (101.6, 101.6),
    '4" × 6"': (101.6, 152.4),
    'A6 (105 × 148 mm)': (105, 148),
    'A5 (148 × 210 mm)': (148, 210),
}

DEFAULT_LABEL_SIZE = '4" × 6"'
DPI = 600
BLEED_MM = 5  # Reduced bleed for smaller labels


def mm_to_px(mm_val, dpi=DPI):
    """Convert millimeters to pixels at given DPI"""
    return int(mm_val * dpi / 25.4)


# =============================================================================
# LABEL GENERATOR CLASS
# =============================================================================

class DoDLabelGenerator:
    """Generate DoD/NATO military specification labels"""

    def __init__(self, label_size='4" × 6"', dpi=600):
        """Initialize generator with label size"""
        self.dpi = dpi
        self.label_size = label_size

        # Get label dimensions
        if label_size in LABEL_SIZES:
            self.label_width_mm, self.label_height_mm = LABEL_SIZES[label_size]
        else:
            self.label_width_mm, self.label_height_mm = LABEL_SIZES[DEFAULT_LABEL_SIZE]

        # Calculate total image size with bleed
        self.total_width_mm = self.label_width_mm + (2 * BLEED_MM)
        self.total_height_mm = self.label_height_mm + (2 * BLEED_MM)

        # Convert to pixels
        self.label_width_px = mm_to_px(self.label_width_mm, dpi)
        self.label_height_px = mm_to_px(self.label_height_mm, dpi)
        self.total_width_px = mm_to_px(self.total_width_mm, dpi)
        self.total_height_px = mm_to_px(self.total_height_mm, dpi)
        self.bleed_px = mm_to_px(BLEED_MM, dpi)

        # Font sizes scaled for DPI and label size
        # Scale relative to 4x6 (101.6 x 152.4mm)
        scale = min(self.label_width_mm / 101.6, self.label_height_mm / 152.4)
        scale = max(0.4, min(scale, 1.5))  # Clamp scale
        base_scale = dpi / 72

        self.FONT_SIZE_LARGE = max(8, int(18 * scale * base_scale))
        self.FONT_SIZE_HEADER = max(6, int(12 * scale * base_scale))
        self.FONT_SIZE_BODY = max(5, int(9 * scale * base_scale))
        self.FONT_SIZE_SMALL = max(4, int(7 * scale * base_scale))
        self.FONT_SIZE_DATA = max(5, int(10 * scale * base_scale))

        # Load fonts
        self._load_fonts()

    def _load_fonts(self):
        """Load system fonts or use defaults"""
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]

        self.font_regular = None
        self.font_bold = None

        for path in font_paths:
            if os.path.exists(path):
                if 'bold' in path.lower() or 'bd' in path.lower():
                    self.font_bold = path
                else:
                    self.font_regular = path

        if not self.font_regular:
            self.font_regular = "arial"
        if not self.font_bold:
            self.font_bold = self.font_regular

    def get_font(self, size, bold=False):
        """Get PIL font at specified size"""
        try:
            font_path = self.font_bold if bold else self.font_regular
            return ImageFont.truetype(font_path, size)
        except:
            return ImageFont.load_default()

    def calculate_dates(self, manufacture_date, shelf_life_months):
        """Calculate re-test date and use by date (Requirement 3: DD MMM YY format)"""
        try:
            date_obj = datetime.strptime(str(manufacture_date), "%d/%m/%Y")
            months = int(shelf_life_months) if pd.notna(shelf_life_months) else 24
            expiry_date = date_obj + timedelta(days=months * 30)
            return expiry_date.strftime("%d %b %y").upper(), expiry_date
        except:
            return "N/A", None

    def format_date_display(self, date_str):
        """Convert DD/MM/YYYY to MMM YYYY format (Requirement 2)"""
        try:
            date_obj = datetime.strptime(str(date_str), "%d/%m/%Y")
            return date_obj.strftime("%b %Y").upper()
        except:
            return str(date_str) if date_str and str(date_str) != 'nan' else "-"

    def safe_str(self, value, default="-"):
        """Convert value to string, handling nan and None"""
        if pd.isna(value) or value is None or str(value).lower() == 'nan':
            return default
        str_val = str(value).strip()
        blank_values = ['not applicable or blank', '-/blank', 'n/a', '', '-', 'blank', 'na', 'none']
        if str_val.lower() in blank_values:
            return default
        return str_val

    def generate_code128(self, data, height=10):
        """Generate Code 128 barcode image"""
        try:
            data_str = str(data).strip()[:20]
            if not data_str or data_str == '-':
                return None
            barcode_class = barcode.get_barcode_class('code128')
            barcode_obj = barcode_class(data_str, writer=ImageWriter())
            buffer = BytesIO()
            barcode_obj.write(buffer, options={
                'module_height': height,
                'module_width': 0.3,
                'quiet_zone': 3,
                'write_text': False,  # Disable HRI text (prevents overlap)
            })
            buffer.seek(0)
            img = Image.open(buffer)
            return img.copy()
        except Exception as e:
            return None

    def generate_code39(self, data, height=10):
        """Generate Code 39 barcode image for NIIN"""
        try:
            data_str = str(data).strip()
            if not data_str or data_str == '-':
                return None
            if not data_str.isdigit() or len(data_str) != 9:
                data_str = data_str.zfill(9)[:9]
            barcode_class = barcode.get_barcode_class('code39')
            barcode_obj = barcode_class(data_str, writer=ImageWriter(), add_checksum=False)
            buffer = BytesIO()
            barcode_obj.write(buffer, options={
                'module_height': height,
                'module_width': 0.3,
                'quiet_zone': 3,
                'write_text': False,  # Disable HRI text (prevents overlap)
            })
            buffer.seek(0)
            img = Image.open(buffer)
            return img.copy()
        except Exception as e:
            return None

    def generate_gs1_datamatrix(self, nsn, batch_lot, expiry_date_obj):
        """Generate GS1 Data Matrix (ECC 200) 2D barcode

        GS1 Format: AI 7001 (NSN) + AI 10 (Batch) + AI 17 (Expiry)
        Note: Serial number (AI 21) removed per v2.3.0 requirements
        """
        try:
            GS = chr(29)  # GS1 separator (ASCII 29)

            # NSN: Extract 13 digits
            nsn_digits = ''.join(filter(str.isdigit, str(nsn)))
            if len(nsn_digits) != 13:
                nsn_digits = nsn_digits.zfill(13)[-13:]

            # Batch Lot: Max 20 characters
            batch_str = str(batch_lot)[:20] if batch_lot and pd.notna(batch_lot) else ""

            # Expiry: YYMMDD format
            if expiry_date_obj:
                expiry_str = expiry_date_obj.strftime("%y%m%d")
            else:
                expiry_str = "990101"

            # Build GS1 string: Only NSN, Batch, Expiry (no serial number)
            gs1_data = f"7001{nsn_digits}{GS}10{batch_str}{GS}17{expiry_str}"

            encoded = dmtx_encode(gs1_data.encode('utf-8'))
            img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
            scale = 6
            img = img.resize((encoded.width * scale, encoded.height * scale), Image.NEAREST)
            return img
        except Exception as e:
            return None

    def create_label_png(self, row):
        """Create single DoD/NATO label as PNG using PIL"""
        # Create white image with bleed
        img = Image.new('RGB', (self.total_width_px, self.total_height_px), 'white')
        draw = ImageDraw.Draw(img)

        # Get fonts
        font_large = self.get_font(self.FONT_SIZE_LARGE, bold=True)
        font_header = self.get_font(self.FONT_SIZE_HEADER, bold=True)
        font_body = self.get_font(self.FONT_SIZE_BODY)
        font_small = self.get_font(self.FONT_SIZE_SMALL)
        font_data = self.get_font(self.FONT_SIZE_DATA, bold=True)

        # Draw cut-line (dashed gray border around label area)
        cut_color = (180, 180, 180)
        x0, y0 = self.bleed_px, self.bleed_px
        x1, y1 = self.bleed_px + self.label_width_px, self.bleed_px + self.label_height_px

        # Draw dashed rectangle for cut-line
        dash_len = mm_to_px(2, self.dpi)
        for x in range(x0, x1, dash_len * 2):
            draw.line([(x, y0), (min(x + dash_len, x1), y0)], fill=cut_color, width=2)
            draw.line([(x, y1), (min(x + dash_len, x1), y1)], fill=cut_color, width=2)
        for y in range(y0, y1, dash_len * 2):
            draw.line([(x0, y), (x0, min(y + dash_len, y1))], fill=cut_color, width=2)
            draw.line([(x1, y), (x1, min(y + dash_len, y1))], fill=cut_color, width=2)

        # Content margins
        margin_px = mm_to_px(3, self.dpi)
        x_left = self.bleed_px + margin_px
        x_right = self.bleed_px + self.label_width_px - margin_px
        content_width = x_right - x_left
        y_pos = self.bleed_px + margin_px

        # Calculate dates
        use_by_date, expiry_date_obj = self.calculate_dates(
            row.get('date_of_manufacture', '01/01/2025'),
            row.get('shelf_life_months', 24)
        )
        dom_formatted = self.format_date_display(str(row.get('date_of_manufacture', '')))

        # ===== SECTION 1: HEADER =====
        product_desc = self.safe_str(row.get('product_description', ''), 'N/A')
        bbox = draw.textbbox((0, 0), product_desc, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_x = self.bleed_px + (self.label_width_px - text_width) // 2
        draw.text((text_x, y_pos), product_desc, fill='black', font=font_large)
        y_pos += self.FONT_SIZE_LARGE + mm_to_px(2, self.dpi)

        nato_stock = self.safe_str(row.get('nato_stock_no', ''), 'N/A')
        bbox = draw.textbbox((0, 0), nato_stock, font=font_header)
        text_width = bbox[2] - bbox[0]
        text_x = self.bleed_px + (self.label_width_px - text_width) // 2
        draw.text((text_x, y_pos), nato_stock, fill='black', font=font_header)
        y_pos += self.FONT_SIZE_HEADER + mm_to_px(2, self.dpi)

        # Border top position
        border_top = y_pos

        # Draw main content border
        border_bottom = self.bleed_px + self.label_height_px - margin_px
        draw.rectangle([x_left - 3, border_top, x_right + 3, border_bottom], outline='black', width=2)
        draw.line([(x_left - 3, y_pos), (x_right + 3, y_pos)], fill='black', width=2)
        y_pos += mm_to_px(1, self.dpi)

        # ===== SECTION 2: NIIN BARCODE ROW =====
        niin = self.safe_str(row.get('niin', ''), '000000000')
        unit_issue = self.safe_str(row.get('unit_of_issue', ''), 'DR')

        # NIIN Barcode (Code 39)
        niin_barcode = self.generate_code39(niin)
        barcode_height_px = mm_to_px(10, self.dpi)

        if niin_barcode:
            barcode_width = mm_to_px(35, self.dpi)
            aspect = niin_barcode.width / niin_barcode.height
            new_height = barcode_height_px
            new_width = int(new_height * aspect)
            if new_width > barcode_width:
                new_width = barcode_width
                new_height = int(new_width / aspect)
            niin_barcode_resized = niin_barcode.resize((new_width, new_height), Image.LANCZOS)
            img.paste(niin_barcode_resized, (x_left, y_pos))

        # Unit of Issue (right of NIIN barcode)
        unit_x = x_left + mm_to_px(38, self.dpi)
        draw.text((unit_x, y_pos), "Unit: ", fill='black', font=font_small)
        unit_label_width = draw.textbbox((0, 0), "Unit: ", font=font_small)[2]
        draw.text((unit_x + unit_label_width, y_pos), unit_issue, fill='black', font=font_data)

        # GS1 Data Matrix (far right) - AI 7001 (NSN) + AI 10 (Batch) + AI 17 (Expiry)
        datamatrix = self.generate_gs1_datamatrix(
            nato_stock,
            row.get('batch_lot_no', ''),
            expiry_date_obj
        )
        if datamatrix:
            dm_size = mm_to_px(14, self.dpi)
            dm_resized = datamatrix.resize((dm_size, dm_size), Image.NEAREST)
            dm_x = x_right - dm_size - mm_to_px(1, self.dpi)
            img.paste(dm_resized, (dm_x, y_pos))

        y_pos += barcode_height_px + mm_to_px(2, self.dpi)

        # NIIN text label with extra spacing
        draw.text((x_left, y_pos), "NIIN: ", fill='black', font=font_small)
        niin_label_width = draw.textbbox((0, 0), "NIIN: ", font=font_small)[2]
        draw.text((x_left + niin_label_width, y_pos), niin, fill='black', font=font_data)

        y_pos += self.FONT_SIZE_DATA + mm_to_px(3, self.dpi)

        # Separator line
        draw.line([(x_left - 3, y_pos), (x_right + 3, y_pos)], fill='black', width=1)
        y_pos += mm_to_px(2, self.dpi)

        # ===== SECTION 3: BATCH LOT & USE BY DATE BARCODES =====
        batch_lot = self.safe_str(row.get('batch_lot_no', ''), '')
        batch_barcode = self.generate_code128(batch_lot)

        if expiry_date_obj:
            use_by_barcode_text = expiry_date_obj.strftime("%d%b%y").upper()
        else:
            use_by_barcode_text = "01JAN99"
        use_by_barcode = self.generate_code128(use_by_barcode_text)

        barcode_row_height = mm_to_px(10, self.dpi)

        # Batch Lot Barcode (left)
        if batch_barcode:
            barcode_width = mm_to_px(40, self.dpi)
            aspect = batch_barcode.width / batch_barcode.height
            new_height = barcode_row_height
            new_width = int(new_height * aspect)
            if new_width > barcode_width:
                new_width = barcode_width
                new_height = int(new_width / aspect)
            batch_resized = batch_barcode.resize((new_width, new_height), Image.LANCZOS)
            img.paste(batch_resized, (x_left, y_pos))

        # Use by Date Barcode (right)
        if use_by_barcode:
            barcode_width = mm_to_px(40, self.dpi)
            aspect = use_by_barcode.width / use_by_barcode.height
            new_height = barcode_row_height
            new_width = int(new_height * aspect)
            if new_width > barcode_width:
                new_width = barcode_width
                new_height = int(new_width / aspect)
            use_by_resized = use_by_barcode.resize((new_width, new_height), Image.LANCZOS)
            use_by_x = x_left + mm_to_px(50, self.dpi)
            img.paste(use_by_resized, (use_by_x, y_pos))

        y_pos += barcode_row_height + mm_to_px(1, self.dpi)

        # Batch Lot Managed text (Requirement 1: Format as "B/L: Y" or "B/L: N")
        batch_managed_raw = self.safe_str(row.get('batch_lot_managed', ''), 'N')
        batch_managed = 'Y' if batch_managed_raw.upper() in ['Y', 'YES'] else 'N'
        draw.text((x_left, y_pos), "B/L: ", fill='black', font=font_small)
        blm_width = draw.textbbox((0, 0), "B/L: ", font=font_small)[2]
        draw.text((x_left + blm_width, y_pos), batch_managed, fill='black', font=font_data)

        # Use by Date text
        use_by_x = x_left + mm_to_px(50, self.dpi)
        draw.text((use_by_x, y_pos), "Use by Date: ", fill='black', font=font_small)
        ubd_width = draw.textbbox((0, 0), "Use by Date: ", font=font_small)[2]
        draw.text((use_by_x + ubd_width, y_pos), use_by_date, fill='black', font=font_data)

        y_pos += self.FONT_SIZE_DATA + mm_to_px(2, self.dpi)

        # Separator line
        draw.line([(x_left - 3, y_pos), (x_right + 3, y_pos)], fill='black', width=1)
        y_pos += mm_to_px(1, self.dpi)

        # ===== SECTION 4: INFORMATION TABLE =====
        nato_code = self.safe_str(row.get('nato_code', ''), '-')
        jsd_ref = self.safe_str(row.get('jsd_reference', ''), '-')
        spec = self.safe_str(row.get('specification', ''), '-')
        capacity = self.safe_str(row.get('capacity_net_weight', ''), '-')
        test_report = self.safe_str(row.get('test_report_no', ''), '-')
        hazmat_code = self.safe_str(row.get('hazardous_material_code', ''), '-')

        table_data = [
            ('NATO Code / JSD:', f"{nato_code}|{jsd_ref}"),  # Req 7: Use internal separator for inline rendering
            ('Specification:', spec),
            ('Batch Lot No.:', batch_lot if batch_lot else '-'),
            ('Date of Manufacture:', dom_formatted),
            ('Capacity/Net Weight:', capacity),
            ('Re-Test Date:', use_by_date),
            ('Test Report No.:', test_report),
            ('Hazardous Material Code:', hazmat_code),  # Req 5: Always display (default "-")
        ]

        row_height = self.FONT_SIZE_DATA + mm_to_px(2, self.dpi)
        col1_width = mm_to_px(32, self.dpi)

        for label, value in table_data:
            # Draw row borders
            draw.rectangle([x_left - 3, y_pos, x_right + 3, y_pos + row_height], outline='black', width=1)
            draw.line([(x_left + col1_width, y_pos), (x_left + col1_width, y_pos + row_height)], fill='black', width=1)

            # Draw text
            text_y = y_pos + mm_to_px(0.5, self.dpi)
            draw.text((x_left, text_y), label, fill='black', font=font_small)

            # SPECIAL CASE: NATO Code / JSD row (Inline Rendering - Req 4 & 7)
            if label == 'NATO Code / JSD:':
                # Parse the combined value
                nato_code_val, jsd_ref_val = value.split('|')

                # Starting X position for value column
                value_x = x_left + col1_width + mm_to_px(1, self.dpi)
                current_x = value_x

                # BUG FIX 2: Skip rectangle if NATO code is just a placeholder dash
                if nato_code_val == '-':
                    # Draw dash only, no rectangle
                    draw.text((current_x, text_y), nato_code_val, fill='black', font=font_data)
                    dash_width = draw.textbbox((0, 0), nato_code_val, font=font_data)[2]
                    current_x += dash_width + mm_to_px(1, self.dpi)

                    # Draw separator and JSD
                    separator = " | "
                    draw.text((current_x, text_y), separator, fill='black', font=font_data)
                    sep_width = draw.textbbox((0, 0), separator, font=font_data)[2]
                    current_x += sep_width
                    draw.text((current_x, text_y), jsd_ref_val, fill='black', font=font_data)
                else:
                    # Step 1: Measure NATO Code text using actual text position
                    text_x = current_x + 12  # Start text with padding
                    nato_bbox = draw.textbbox((text_x, text_y), nato_code_val, font=font_data)

                    # Step 2: Calculate rectangle with padding around actual text bounds
                    padding = 10  # Padding around the bounding box
                    rect_x1 = nato_bbox[0] - padding
                    rect_y1 = nato_bbox[1] - padding
                    rect_x2 = nato_bbox[2] + padding
                    rect_y2 = nato_bbox[3] + padding

                    # Step 3: Draw rectangle border around NATO Code (thicker border)
                    draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], outline='black', width=3)

                    # Step 4: Draw NATO Code text inside rectangle (with padding offset)
                    draw.text((text_x, text_y), nato_code_val, fill='black', font=font_data)

                    # Step 5: Move cursor to right of rectangle
                    current_x = rect_x2 + mm_to_px(1, self.dpi)

                    # Step 6: Draw separator " | "
                    separator = " | "
                    draw.text((current_x, text_y), separator, fill='black', font=font_data)
                    sep_width = draw.textbbox((0, 0), separator, font=font_data)[2]
                    current_x += sep_width

                    # Step 7: Draw JSD Reference text
                    draw.text((current_x, text_y), jsd_ref_val, fill='black', font=font_data)
            else:
                # Standard table cell rendering (unchanged)
                draw.text((x_left + col1_width + mm_to_px(1, self.dpi), text_y), value, fill='black', font=font_data)

            y_pos += row_height

        y_pos += mm_to_px(1, self.dpi)

        # ===== SECTION 5: FIELD 12 - SAFETY AND MOVEMENT MARKINGS (CRITICAL) =====
        # Always display this field prominently, even if empty
        safety_markings = self.safe_str(row.get('safety_movement_markings', ''), '-')

        # Header for safety section (Requirement 6: Remove "Field 12:" prefix)
        safety_header_height = self.FONT_SIZE_SMALL + mm_to_px(2, self.dpi)
        draw.rectangle([x_left - 3, y_pos, x_right + 3, y_pos + safety_header_height],
                      fill=(240, 240, 240), outline='black', width=1)
        draw.text((x_left, y_pos + mm_to_px(0.5, self.dpi)),
                 "Safety & Movement Markings", fill='black', font=font_small)
        y_pos += safety_header_height

        # Safety content
        safety_content_height = self.FONT_SIZE_DATA + mm_to_px(3, self.dpi)
        draw.rectangle([x_left - 3, y_pos, x_right + 3, y_pos + safety_content_height],
                      outline='black', width=1)
        draw.text((x_left, y_pos + mm_to_px(0.5, self.dpi)), safety_markings, fill='black', font=font_data)
        y_pos += safety_content_height + mm_to_px(1, self.dpi)

        # ===== SECTION 6: CONTRACTOR DETAILS =====
        contractor_details = self.safe_str(row.get('contractor_details', ''), '')
        if contractor_details and contractor_details != '-':
            lines = contractor_details.split('|')
            line_height = self.FONT_SIZE_SMALL + mm_to_px(0.5, self.dpi)
            box_height = len(lines) * line_height + mm_to_px(2, self.dpi)

            # Only draw if there's space
            if y_pos + box_height < border_bottom - mm_to_px(2, self.dpi):
                draw.rectangle([x_left - 3, y_pos, x_right + 3, y_pos + box_height], outline='black', width=1)
                text_y = y_pos + mm_to_px(0.5, self.dpi)
                for line in lines:
                    draw.text((x_left, text_y), line.strip(), fill='black', font=font_small)
                    text_y += line_height

        return img


# =============================================================================
# STREAMLIT APP
# =============================================================================

def main():
    """Main Streamlit app"""

    # Page config
    st.set_page_config(
        page_title="DoD/NATO Label Generator",
        page_icon="🏷️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Dark/light mode toggle in sidebar
    with st.sidebar:
        st.title("⚙️ Settings")

        # Theme toggle (CSS-based)
        dark_mode = st.toggle("🌙 Dark Mode", value=False)

        st.markdown("---")
        st.markdown("### 📖 Help")
        st.markdown("""
        **Quick Start:**
        1. Select product SKU from dropdown
        2. Enter batch lot number and manufacturing date
        3. Adjust re-test date if needed (defaults to DOM + shelf life)
        4. Choose label size
        5. Generate and download label

        **Product Database:**
        - Products loaded from `products.json`
        - Each product has fixed NSN, specifications, shelf life
        - Support for multiple pack sizes per product

        **Date Calculations:**
        - **Use by Date:** Automatically calculated (DOM + shelf life)
        - **Re-Test Date:** Defaults to use by date, can be overridden
        - **GS1 Barcode:** Encodes NSN + Batch + Expiry only (no serial number)
        """)

        st.markdown("---")
        st.markdown("**v2.3.0** | Valorem Chemicals")

    # Apply dark mode CSS
    if dark_mode:
        st.markdown("""
        <style>
        .stApp { background-color: #1E1E1E; color: #FFFFFF; }
        </style>
        """, unsafe_allow_html=True)

    # Title
    st.title("🏷️ DoD/NATO Label Generator")
    st.markdown("Generate military specification labels with 4 barcode types per MIL-STD-129")

    # Load products database
    products_file = Path("products.json")
    if not products_file.exists():
        st.error("❌ `products.json` database file not found!")
        st.info("Please create a `products.json` file in the project root directory with product SKU data.")
        st.stop()

    try:
        with open(products_file, 'r') as f:
            products_db = json.load(f)
    except Exception as e:
        st.error(f"❌ Error loading products.json: {e}")
        st.stop()

    if not products_db or len(products_db) == 0:
        st.error("❌ products.json is empty!")
        st.stop()

    # Create product selector options
    product_options = {}
    for product in products_db:
        display_name = f"{product['product_name']} ({product['unit_of_issue']})"
        product_options[display_name] = product

    # Product Selection Section
    st.markdown("### 📦 Select Product")
    selected_product_name = st.selectbox(
        "Choose product SKU:",
        options=list(product_options.keys()),
        help="Select the product and pack size for label generation"
    )

    selected_product = product_options[selected_product_name]

    # Display product information
    with st.expander("ℹ️ Product Details", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Product ID:** {selected_product['id']}")
            st.write(f"**NSN:** {selected_product['nsn']}")
            st.write(f"**NATO Code:** {selected_product['nato_code']}")
            st.write(f"**JSD Reference:** {selected_product['jsd_reference']}")
        with col2:
            st.write(f"**Specification:** {selected_product['specification']}")
            st.write(f"**Shelf Life:** {selected_product['shelf_life_months']} months")
            st.write(f"**Batch Lot Managed:** {selected_product['batch_lot_managed']}")
            st.write(f"**Hazmat Code:** {selected_product['hazardous_material_code']}")

    st.markdown("---")

    # Manual Input Section
    st.markdown("### ✏️ Label Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Fixed Inputs")
        batch_lot_no = st.text_input(
            "Batch Lot Number *",
            value="",
            help="Enter the batch/lot number for this production run (Field 5)"
        )

        date_of_manufacture = st.date_input(
            "Date of Manufacture *",
            value=datetime.now(),
            help="Select the manufacturing date (Field 8)"
        )

        test_report_no = st.text_input(
            "Test Report Number",
            value="-",
            help="Enter test report number or leave as '-' if not applicable (Field 14)"
        )

    with col2:
        st.markdown("#### Calculated Defaults")

        # Calculate default Re-Test Date
        if date_of_manufacture:
            default_retest_date = date_of_manufacture + timedelta(days=selected_product['shelf_life_months'] * 30)
        else:
            default_retest_date = datetime.now() + timedelta(days=selected_product['shelf_life_months'] * 30)

        retest_date = st.date_input(
            "Re-Test Date",
            value=default_retest_date,
            help=f"Default: DOM + {selected_product['shelf_life_months']} months. You can override this date. (Field 13)"
        )

        # Calculate Use by Date (display only)
        if date_of_manufacture:
            use_by_date = date_of_manufacture + timedelta(days=selected_product['shelf_life_months'] * 30)
            st.info(f"**Use by Date (Auto):** {use_by_date.strftime('%d %b %y').upper()}\n\n*Calculated: DOM + {selected_product['shelf_life_months']} months (Field 19)*")
        else:
            st.info("**Use by Date:** _Enter manufacturing date first_")

    # Label Size Selection
    st.markdown("---")
    st.markdown("### 📏 Label Size")
    label_size = st.selectbox(
        "Select label size:",
        options=list(LABEL_SIZES.keys()),
        index=list(LABEL_SIZES.keys()).index(DEFAULT_LABEL_SIZE),
        help="Choose the physical label size for printing"
    )

    # Validation
    can_generate = bool(batch_lot_no and date_of_manufacture)

    if not can_generate:
        st.warning("⚠️ Please fill in all required fields (marked with *) to generate label")

    # Generate Label Button
    st.markdown("---")
    if st.button("🏷️ Generate Label", type="primary", disabled=not can_generate, use_container_width=True):
        # Combine product data with manual inputs
        row_data = {
            'product_description': selected_product['product_name'],
            'nato_stock_no': selected_product['nsn'],
            'nato_code': selected_product['nato_code'],
            'jsd_reference': selected_product['jsd_reference'],
            'specification': selected_product['specification'],
            'batch_lot_no': batch_lot_no,
            'batch_lot_managed': selected_product['batch_lot_managed'],
            'date_of_manufacture': date_of_manufacture.strftime('%d/%m/%Y'),
            'contractor_details': selected_product['contractor_details'],
            'capacity_net_weight': selected_product['capacity_weight'],
            'safety_movement_markings': selected_product['safety_markings'],
            'shelf_life_months': selected_product['shelf_life_months'],
            'test_report_no': test_report_no,
            'unit_of_issue': selected_product['unit_of_issue'],
            'hazardous_material_code': selected_product['hazardous_material_code'],
            'retest_date': retest_date.strftime('%d/%m/%Y') if retest_date else "-",
        }

        # Generate label
        with st.spinner("Generating label..."):
            generator = DoDLabelGenerator(label_size=label_size)
            label_img = generator.create_label_png(row_data)

            # Store in session state for download
            st.session_state['current_label'] = label_img
            st.session_state['current_label_data'] = row_data
            st.session_state['current_label_size'] = label_size

        st.success("✅ Label generated successfully!")

    # Preview Section
    if 'current_label' in st.session_state:
        st.markdown("---")
        st.markdown("### 👁️ Label Preview")
        st.image(st.session_state['current_label'], caption=f"Label Preview - {st.session_state['current_label_size']}", use_container_width=True)

        # Download Section
        st.markdown("---")
        st.markdown("### 📥 Download Label")

        # Option to save to output folder
        save_to_folder = st.checkbox("💾 Also save to output folder", value=True,
                                     help="Save file to the project's output/ folder in addition to browser download")

        # Create output directories if needed
        output_png_dir = Path("output/png")
        if save_to_folder:
            output_png_dir.mkdir(parents=True, exist_ok=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📷 Download PNG", type="secondary", use_container_width=True):
                img = st.session_state['current_label']
                row_data = st.session_state['current_label_data']

                # Save to buffer
                buffer = BytesIO()
                img.save(buffer, format='PNG', dpi=(DPI, DPI))
                buffer.seek(0)

                # Generate filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"dod_label_{row_data['product_description']}_{batch_lot_no}_{st.session_state['current_label_size'].replace(' ', '')}_{timestamp}.png"
                filename = "".join(c if c.isalnum() or c in '-_.' else '_' for c in filename)

                # Save to folder if enabled
                if save_to_folder:
                    filepath = output_png_dir / filename
                    img.save(filepath, format='PNG', dpi=(DPI, DPI))
                    st.success(f"💾 Saved to: {filepath}")

                # Provide download button
                st.download_button(
                    label="⬇️ Download PNG File",
                    data=buffer.getvalue(),
                    file_name=filename,
                    mime="image/png"
                )

        with col2:
            if HAS_REPORTLAB:
                if st.button("📄 Download PDF", type="secondary", use_container_width=True):
                    # Note: PDF generation would require refactoring the PDF generator
                    # For now, show info message
                    st.info("PDF generation with JSON workflow coming in v2.3.1")
            else:
                st.info("PDF generation unavailable (ReportLab not installed)")
    else:
        st.info("👆 Select a product and fill in the label information above to generate a label.")


if __name__ == "__main__":
    main()
