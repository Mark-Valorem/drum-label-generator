#!/usr/bin/env python3
"""
DoD/NATO Label Generator - Streamlit Web Dashboard
Generates military specification labels with web interface
Version 2.4.0 - Product Manager Feature
"""

import os
import io
import json
import zipfile
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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
            expiry_date = date_obj + relativedelta(months=months)
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
        # Calculate NIIN from NSN (last 9 digits, strip all dashes and spaces)
        nato_stock = self.safe_str(row.get('nato_stock_no', ''), '-')
        niin = ''.join(filter(str.isdigit, nato_stock))[-9:] if nato_stock != '-' else '000000000'
        unit_issue = self.safe_str(row.get('unit_of_issue', ''), 'DR')
        hazmat_code = self.safe_str(row.get('hazardous_material_code', ''), '-')  # Need this for header

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

        # Hazard Box (between Unit and GS1 Data Matrix)
        # Only draw if hazmat_code is not "-" or empty
        if hazmat_code and hazmat_code != '-':
            # Position hazard box to the right of Unit
            unit_text_width = draw.textbbox((0, 0), unit_issue, font=font_data)[2]
            hazard_x = unit_x + unit_label_width + unit_text_width + mm_to_px(3, self.dpi)

            # Draw "HAZARD" label above box
            hazard_label = "HAZARD"
            hazard_label_bbox = draw.textbbox((hazard_x, y_pos), hazard_label, font=font_small)
            draw.text((hazard_x, y_pos), hazard_label, fill='black', font=font_small)

            # Calculate box position below "HAZARD" text
            box_y = hazard_label_bbox[3] + mm_to_px(0.5, self.dpi)
            box_size = mm_to_px(5, self.dpi)  # Smaller square box for compact layout

            # Draw filled black square
            draw.rectangle(
                [hazard_x, box_y, hazard_x + box_size, box_y + box_size],
                fill='black',
                outline='black',
                width=1
            )

            # Draw class number in WHITE centered in box
            # Calculate text position to center it
            class_num_bbox = draw.textbbox((0, 0), hazmat_code, font=font_data)
            text_w = class_num_bbox[2] - class_num_bbox[0]
            text_h = class_num_bbox[3] - class_num_bbox[1]
            text_x = hazard_x + (box_size - text_w) // 2
            text_y = box_y + (box_size - text_h) // 2
            draw.text((text_x, text_y), hazmat_code, fill='white', font=font_data)

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
        # hazmat_code already defined earlier for header rendering (line 313)

        # Re-Test Date: Use manual override if provided, otherwise use calculated use_by_date
        manual_retest = row.get('retest_date')
        if manual_retest and manual_retest not in [None, '-', '']:
            # Manual override: format the provided date
            retest_display = self.format_date_display(str(manual_retest))
        else:
            # Auto-calculate: use the use_by_date (Field 19)
            retest_display = use_by_date

        table_data = [
            ('NATO Code / JSD:', f"{nato_code}|{jsd_ref}"),  # Req 7: Use internal separator for inline rendering
            ('Specification:', spec),
            ('Batch Lot No.:', batch_lot if batch_lot else '-'),
            ('Date of Manufacture:', dom_formatted),
            ('Capacity/Net Weight:', capacity),
            ('Re-Test Date:', retest_display),
            ('Test Report No.:', test_report),
            # Hazardous Material Code removed - now shown in header hazard box
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

def show_product_manager(products_db, products_file):
    """Display the product management view"""
    import pandas as pd

    st.title("🗂️ Product Manager")
    st.markdown("Manage your product SKU database")

    # Display current products in a table
    st.markdown("### 📋 Current Products")

    if products_db:
        # Convert to DataFrame for display
        df = pd.DataFrame(products_db)

        # Reorder columns for better display
        display_columns = ['id', 'product_name', 'nsn', 'unit_of_issue', 'capacity_weight',
                          'shelf_life_months', 'nato_code', 'jsd_reference']
        available_columns = [col for col in display_columns if col in df.columns]

        st.dataframe(
            df[available_columns],
            use_container_width=True,
            hide_index=True
        )

        st.info(f"📊 Total Products: {len(products_db)}")
    else:
        st.warning("No products in database")

    st.markdown("---")

    # Add/Edit Product Form
    st.markdown("### ➕ Add / Edit Product")

    # Select mode: Add new or Edit existing
    col1, col2 = st.columns([1, 3])
    with col1:
        mode = st.radio("Mode:", ["Add New", "Edit Existing"], horizontal=False)

    with col2:
        if mode == "Edit Existing" and products_db:
            product_ids = [p['id'] for p in products_db]
            selected_id = st.selectbox("Select Product to Edit:", product_ids)
            selected_product = next((p for p in products_db if p['id'] == selected_id), None)
        else:
            selected_product = None

    # Product form
    with st.form("product_form"):
        st.markdown("#### Product Information")

        col1, col2 = st.columns(2)

        with col1:
            product_id = st.text_input(
                "Product ID *",
                value=selected_product['id'] if selected_product else "",
                help="Unique identifier (e.g., OM11_20L)",
                disabled=(mode == "Edit Existing")
            )

            product_name = st.text_input(
                "Product Name *",
                value=selected_product['product_name'] if selected_product else "",
                help="Product name (e.g., Fuchs OM-11)"
            )

            nsn = st.text_input(
                "NSN *",
                value=selected_product['nsn'] if selected_product else "",
                help="NATO Stock Number (format: nnnn-nn-nnn-nnnn)"
            )

            nato_code = st.text_input(
                "NATO Code",
                value=selected_product.get('nato_code', '-') if selected_product else "-",
                help="NATO code or '-' if not applicable"
            )

            jsd_reference = st.text_input(
                "JSD Reference",
                value=selected_product.get('jsd_reference', '-') if selected_product else "-",
                help="Joint Service Designation reference"
            )

            specification = st.text_input(
                "Specification *",
                value=selected_product.get('specification', '') if selected_product else "",
                help="Product specification (e.g., DEF STAN 91-39 Issue 4)"
            )

        with col2:
            unit_of_issue = st.text_input(
                "Unit of Issue *",
                value=selected_product.get('unit_of_issue', 'DR') if selected_product else "DR",
                help="Unit type (e.g., DR for Drum, CN for Can)"
            )

            capacity_weight = st.text_input(
                "Capacity/Weight *",
                value=selected_product.get('capacity_weight', '') if selected_product else "",
                help="Pack size (e.g., 20 LI, 55 US GAL)"
            )

            shelf_life_months = st.number_input(
                "Shelf Life (months) *",
                min_value=1,
                max_value=120,
                value=selected_product.get('shelf_life_months', 24) if selected_product else 24,
                help="Shelf life in months"
            )

            batch_lot_managed = st.selectbox(
                "Batch Lot Managed *",
                options=["Y", "N"],
                index=0 if (selected_product and selected_product.get('batch_lot_managed') == 'Y') else 1,
                help="Is this product batch/lot managed?"
            )

            hazardous_material_code = st.text_input(
                "Hazardous Material Code",
                value=selected_product.get('hazardous_material_code', '-') if selected_product else "-",
                help="UN code or '-' if not hazardous (e.g., UN1307, 3, III)"
            )

        st.markdown("#### Contractor Details")
        contractor_details = st.text_area(
            "Contractor Details *",
            value=selected_product.get('contractor_details', '') if selected_product else
                  "Valorem Chemicals Pty Ltd|123 Industrial Drive|Sydney NSW 2000|Australia",
            help="Pipe-separated: Company|Address|City|Country"
        )

        st.markdown("#### Safety Information")
        safety_markings = st.text_area(
            "Safety/Movement Markings",
            value=selected_product.get('safety_markings', '-') if selected_product else "-",
            help="Safety markings or '-' if not applicable"
        )

        # Submit button
        submitted = st.form_submit_button(
            "💾 Save Product" if mode == "Add New" else "💾 Update Product",
            type="primary",
            use_container_width=True
        )

        if submitted:
            # Validate required fields
            if not all([product_id, product_name, nsn, specification, unit_of_issue,
                       capacity_weight, contractor_details]):
                st.error("❌ Please fill in all required fields (marked with *)")
            else:
                # Create product object
                new_product = {
                    "id": product_id.strip(),
                    "product_name": product_name.strip(),
                    "nsn": nsn.strip(),
                    "nato_code": nato_code.strip(),
                    "jsd_reference": jsd_reference.strip(),
                    "specification": specification.strip(),
                    "unit_of_issue": unit_of_issue.strip(),
                    "capacity_weight": capacity_weight.strip(),
                    "shelf_life_months": int(shelf_life_months),
                    "batch_lot_managed": batch_lot_managed,
                    "hazardous_material_code": hazardous_material_code.strip(),
                    "contractor_details": contractor_details.strip(),
                    "safety_markings": safety_markings.strip()
                }

                # Validate NSN format (basic check)
                if len(nsn.replace('-', '')) != 13 or not all(c.isdigit() or c == '-' for c in nsn):
                    st.error("❌ NSN must be 13 digits in format: nnnn-nn-nnn-nnnn")
                else:
                    # Save to database
                    try:
                        if mode == "Add New":
                            # Check for duplicate ID
                            if any(p['id'] == product_id for p in products_db):
                                st.error(f"❌ Product ID '{product_id}' already exists!")
                            else:
                                products_db.append(new_product)
                                save_products_json(products_db, products_file)
                                st.success(f"✅ Product '{product_name}' added successfully!")
                                st.rerun()
                        else:  # Edit mode
                            # Find and update existing product
                            for i, p in enumerate(products_db):
                                if p['id'] == product_id:
                                    products_db[i] = new_product
                                    break
                            save_products_json(products_db, products_file)
                            st.success(f"✅ Product '{product_name}' updated successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error saving product: {e}")

    # Delete Product Section
    if products_db:
        st.markdown("---")
        st.markdown("### 🗑️ Delete Product")

        col1, col2, col3 = st.columns([2, 1, 2])

        with col1:
            product_to_delete = st.selectbox(
                "Select product to delete:",
                options=[p['id'] for p in products_db],
                key="delete_selector"
            )

        with col2:
            st.write("")  # Spacer
            st.write("")  # Spacer
            if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                st.session_state['confirm_delete'] = product_to_delete

        with col3:
            if 'confirm_delete' in st.session_state and st.session_state['confirm_delete'] == product_to_delete:
                st.warning(f"⚠️ Confirm deletion of '{product_to_delete}'?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Yes, Delete", type="primary", use_container_width=True):
                        try:
                            products_db = [p for p in products_db if p['id'] != product_to_delete]
                            save_products_json(products_db, products_file)
                            st.success(f"✅ Product '{product_to_delete}' deleted!")
                            del st.session_state['confirm_delete']
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error deleting product: {e}")
                with col_no:
                    if st.button("❌ Cancel", use_container_width=True):
                        del st.session_state['confirm_delete']
                        st.rerun()


def save_products_json(products_db, products_file):
    """Safely save products database to JSON file with atomic write"""
    import tempfile
    import shutil

    # Create backup
    backup_file = products_file.with_suffix('.json.bak')
    if products_file.exists():
        shutil.copy2(products_file, backup_file)

    try:
        # Write to temporary file first
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
            json.dump(products_db, tmp_file, indent=2, ensure_ascii=False)
            tmp_path = Path(tmp_file.name)

        # Atomic rename (overwrites existing file)
        shutil.move(str(tmp_path), str(products_file))

        # Remove backup if successful
        if backup_file.exists():
            backup_file.unlink()

    except Exception as e:
        # Restore from backup if write failed
        if backup_file.exists():
            shutil.copy2(backup_file, products_file)
        raise e


def main():
    """Main Streamlit app"""

    # Page config
    st.set_page_config(
        page_title="DoD/NATO Label Generator",
        page_icon="🏷️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar navigation
    with st.sidebar:
        st.title("🧭 Navigation")
        page = st.radio(
            "Select View:",
            ["Generate Label", "Manage Products"],
            index=0,
            help="Switch between label generation and product management"
        )

        st.markdown("---")
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
        st.markdown("**v2.4.0** | Valorem Chemicals")

    # Apply dark mode CSS
    if dark_mode:
        st.markdown("""
        <style>
        .stApp { background-color: #1E1E1E; color: #FFFFFF; }
        </style>
        """, unsafe_allow_html=True)

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

    # Route to selected page
    if page == "Generate Label":
        show_label_generator(products_db)
    elif page == "Manage Products":
        show_product_manager(products_db, products_file)


def show_label_generator(products_db):
    """Display the label generation view"""
    st.title("🏷️ DoD/NATO Label Generator")
    st.markdown("Generate military specification labels with 4 barcode types per MIL-STD-129")

    # Create product selector options
    product_options = {}
    for product in products_db:
        display_name = f"{product['product_name']} ({product['capacity_weight']})"
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
            st.write(f"**Unit of Issue:** {selected_product['unit_of_issue']}")
        with col2:
            st.write(f"**Specification:** {selected_product['specification']}")
            st.write(f"**Capacity/Weight:** {selected_product['capacity_weight']}")
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
            default_retest_date = date_of_manufacture + relativedelta(months=selected_product['shelf_life_months'])
        else:
            default_retest_date = datetime.now() + relativedelta(months=selected_product['shelf_life_months'])

        # Override checkbox for Re-Test Date
        override_retest = st.checkbox(
            "Override Default Re-Test Date",
            value=False,
            help="Check this to manually specify a Re-Test Date instead of using the calculated default"
        )

        # Re-Test Date input (conditional based on override)
        retest_date = st.date_input(
            "Re-Test Date",
            value=default_retest_date,
            disabled=not override_retest,
            help=f"Default: DOM + {selected_product['shelf_life_months']} months. Enable override to manually specify. (Field 13)"
        )

        # Warning if override is active but test report is missing
        if override_retest and not test_report_no:
            st.warning("⚠️ Compliance Warning: You are overriding the Re-Test date without a Test Report Number.")

        # Calculate Use by Date (display only)
        if date_of_manufacture:
            use_by_date = date_of_manufacture + relativedelta(months=selected_product['shelf_life_months'])
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
            'retest_date': retest_date.strftime('%d/%m/%Y') if override_retest and retest_date else None,
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
