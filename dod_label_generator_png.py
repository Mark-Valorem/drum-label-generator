#!/usr/bin/env python3
"""
DoD/NATO Label Generator - High Resolution PNG Output
Generates military specification labels as PNG images at 600 DPI
Version 2.1.0

Uses direct PIL/Pillow rendering for cross-platform compatibility.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from io import BytesIO

import pandas as pd
import barcode
from barcode.writer import ImageWriter
from pylibdmtx.pylibdmtx import encode as dmtx_encode
from PIL import Image, ImageDraw, ImageFont

# Configuration
OUTPUT_FOLDER = "output/png"

# Label sizes in mm (width x height)
LABEL_SIZES = {
    'A5': (148, 210),
    'A6': (105, 148),
    '4x6': (101.6, 152.4),
    '4x4': (101.6, 101.6),
    '3x2': (76, 51),
    'A4': (210, 297),
}

# Resolution
DPI = 600
BLEED_MM = 10  # Bleed/margin in mm on each side


def mm_to_px(mm_val, dpi=DPI):
    """Convert millimeters to pixels at given DPI"""
    return int(mm_val * dpi / 25.4)


class DoDLabelGeneratorPNG:
    """Generate DoD/NATO military specification labels as PNG"""

    def __init__(self, data_file, label_size='A5', dpi=600):
        """Initialize generator with data file and label size"""
        self.data_file = data_file
        self.data = None
        self.label_size = label_size
        self.dpi = dpi
        self.output_folder = Path(OUTPUT_FOLDER)
        self.output_folder.mkdir(parents=True, exist_ok=True)

        # Get label dimensions
        if label_size in LABEL_SIZES:
            self.label_width_mm, self.label_height_mm = LABEL_SIZES[label_size]
        else:
            print(f"Unknown label size '{label_size}', using A5")
            self.label_width_mm, self.label_height_mm = LABEL_SIZES['A5']

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
        scale = min(self.label_width_mm / 148, self.label_height_mm / 210)
        base_scale = dpi / 72  # Scale from 72 DPI (standard) to target DPI

        self.FONT_SIZE_LARGE = int(20 * scale * base_scale)
        self.FONT_SIZE_HEADER = int(14 * scale * base_scale)
        self.FONT_SIZE_BODY = int(11 * scale * base_scale)
        self.FONT_SIZE_SMALL = int(8 * scale * base_scale)
        self.FONT_SIZE_DATA = int(12 * scale * base_scale)

        # Try to load fonts
        self._load_fonts()

    def _load_fonts(self):
        """Load system fonts or use defaults"""
        # Try common font paths
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
                try:
                    if 'bold' in path.lower() or 'bd' in path.lower():
                        self.font_bold = path
                    else:
                        self.font_regular = path
                except:
                    pass

        # Fallback to default
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

    def load_data(self):
        """Load data from CSV or Excel file"""
        file_extension = Path(self.data_file).suffix.lower()
        try:
            if file_extension == '.csv':
                self.data = pd.read_csv(self.data_file)
            elif file_extension in ['.xlsx', '.xls']:
                self.data = pd.read_excel(self.data_file)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            print(f"Loaded {len(self.data)} records from {self.data_file}")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def validate_data(self):
        """Validate required columns exist"""
        required_columns = [
            'product_description', 'nato_stock_no', 'niin',
            'batch_lot_no', 'date_of_manufacture'
        ]
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            print(f"Error: Missing required columns: {', '.join(missing_columns)}")
            return False
        return True

    def calculate_dates(self, manufacture_date, shelf_life_months):
        """Calculate re-test date and use by date (Requirement 3: DD MMM YY format)"""
        try:
            date_obj = datetime.strptime(manufacture_date, "%d/%m/%Y")
            months = int(shelf_life_months) if pd.notna(shelf_life_months) else 24
            expiry_date = date_obj + timedelta(days=months * 30)
            return expiry_date.strftime("%d %b %y").upper(), expiry_date
        except:
            return "N/A", None

    def format_date_display(self, date_str):
        """Convert DD/MM/YYYY to MMM YYYY format (Requirement 2)"""
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            return date_obj.strftime("%b %Y").upper()
        except:
            return date_str if date_str and str(date_str) != 'nan' else ""

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
            print(f"Error generating Code 128 barcode: {e}")
            return None

    def generate_code39(self, data, height=10):
        """Generate Code 39 barcode image for NIIN"""
        try:
            data_str = str(data).strip()
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
            print(f"Error generating Code 39 barcode: {e}")
            return None

    def generate_gs1_datamatrix(self, nsn, batch_lot, expiry_date_obj, serial_number=None):
        """Generate GS1 Data Matrix (ECC 200) 2D barcode"""
        try:
            GS = chr(29)
            nsn_digits = ''.join(filter(str.isdigit, str(nsn)))
            if len(nsn_digits) != 13:
                nsn_digits = nsn_digits.zfill(13)[-13:]
            batch_str = str(batch_lot)[:20] if batch_lot and pd.notna(batch_lot) else ""
            if expiry_date_obj:
                expiry_str = expiry_date_obj.strftime("%y%m%d")
            else:
                expiry_str = "990101"
            gs1_data = f"7001{nsn_digits}{GS}10{batch_str}{GS}17{expiry_str}"
            if serial_number and pd.notna(serial_number):
                gs1_data += f"{GS}21{str(serial_number)[:20]}"
            encoded = dmtx_encode(gs1_data.encode('utf-8'))
            img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
            scale = 6
            img = img.resize((encoded.width * scale, encoded.height * scale), Image.NEAREST)
            return img
        except Exception as e:
            print(f"Error generating GS1 Data Matrix: {e}")
            return None

    def create_label_png(self, row, output_path):
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
        margin_px = mm_to_px(5, self.dpi)
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
        y_pos += self.FONT_SIZE_LARGE + mm_to_px(3, self.dpi)

        nato_stock = self.safe_str(row.get('nato_stock_no', ''), 'N/A')
        bbox = draw.textbbox((0, 0), nato_stock, font=font_header)
        text_width = bbox[2] - bbox[0]
        text_x = self.bleed_px + (self.label_width_px - text_width) // 2
        draw.text((text_x, y_pos), nato_stock, fill='black', font=font_header)
        y_pos += self.FONT_SIZE_HEADER + mm_to_px(3, self.dpi)

        # Border top position
        border_top = y_pos

        # Draw main content border
        border_bottom = self.bleed_px + self.label_height_px - margin_px
        draw.rectangle([x_left - 5, border_top, x_right + 5, border_bottom], outline='black', width=3)

        # Horizontal line below header
        draw.line([(x_left - 5, y_pos), (x_right + 5, y_pos)], fill='black', width=3)
        y_pos += mm_to_px(2, self.dpi)

        # ===== SECTION 2: NIIN BARCODE ROW =====
        niin = self.safe_str(row.get('niin', ''), '000000000')
        unit_issue = self.safe_str(row.get('unit_of_issue', ''), 'DR')

        # NIIN Barcode (Code 39)
        niin_barcode = self.generate_code39(niin)
        barcode_height_px = mm_to_px(15, self.dpi)

        if niin_barcode:
            # Resize barcode to fit
            barcode_width = mm_to_px(50, self.dpi)
            aspect = niin_barcode.width / niin_barcode.height
            new_height = barcode_height_px
            new_width = int(new_height * aspect)
            if new_width > barcode_width:
                new_width = barcode_width
                new_height = int(new_width / aspect)
            niin_barcode_resized = niin_barcode.resize((new_width, new_height), Image.LANCZOS)
            img.paste(niin_barcode_resized, (x_left, y_pos))

        # Unit of Issue (right of NIIN barcode)
        unit_x = x_left + mm_to_px(55, self.dpi)
        draw.text((unit_x, y_pos), "Unit: ", fill='black', font=font_small)
        unit_label_width = draw.textbbox((0, 0), "Unit: ", font=font_small)[2]
        draw.text((unit_x + unit_label_width, y_pos), unit_issue, fill='black', font=font_data)

        # Hazard Box (between Unit and GS1 Data Matrix)
        # Only draw if hazmat_code is not "-" or empty
        if hazmat_code and hazmat_code != '-':
            # Position hazard box to the right of Unit
            unit_text_width = draw.textbbox((0, 0), unit_issue, font=font_data)[2]
            hazard_x = unit_x + unit_label_width + unit_text_width + mm_to_px(5, self.dpi)

            # Draw "HAZARD" label above box
            hazard_label = "HAZARD"
            hazard_label_bbox = draw.textbbox((hazard_x, y_pos), hazard_label, font=font_tiny)
            draw.text((hazard_x, y_pos), hazard_label, fill='black', font=font_tiny)

            # Calculate box position below "HAZARD" text
            box_y = hazard_label_bbox[3] + mm_to_px(1, self.dpi)
            box_size = mm_to_px(8, self.dpi)  # Square box

            # Draw filled black square
            draw.rectangle(
                [hazard_x, box_y, hazard_x + box_size, box_y + box_size],
                fill='black',
                outline='black',
                width=2
            )

            # Draw class number in WHITE centered in box
            # Calculate text position to center it
            class_num_bbox = draw.textbbox((0, 0), hazmat_code, font=font_data)
            text_w = class_num_bbox[2] - class_num_bbox[0]
            text_h = class_num_bbox[3] - class_num_bbox[1]
            text_x = hazard_x + (box_size - text_w) // 2
            text_y = box_y + (box_size - text_h) // 2
            draw.text((text_x, text_y), hazmat_code, fill='white', font=font_data)

        # GS1 Data Matrix (far right)
        datamatrix = self.generate_gs1_datamatrix(
            nato_stock,
            row.get('batch_lot_no', ''),
            expiry_date_obj,
            row.get('serial_number', None)
        )
        if datamatrix:
            dm_size = mm_to_px(20, self.dpi)
            dm_resized = datamatrix.resize((dm_size, dm_size), Image.NEAREST)
            dm_x = x_right - dm_size - mm_to_px(2, self.dpi)
            img.paste(dm_resized, (dm_x, y_pos))

        y_pos += barcode_height_px + mm_to_px(3, self.dpi)

        # NIIN text label with extra spacing
        draw.text((x_left, y_pos), "NIIN: ", fill='black', font=font_small)
        niin_label_width = draw.textbbox((0, 0), "NIIN: ", font=font_small)[2]
        draw.text((x_left + niin_label_width, y_pos), niin, fill='black', font=font_data)

        y_pos += self.FONT_SIZE_DATA + mm_to_px(5, self.dpi)  # Extra spacing before separator

        # Separator line
        draw.line([(x_left - 5, y_pos), (x_right + 5, y_pos)], fill='black', width=2)
        y_pos += mm_to_px(3, self.dpi)

        # ===== SECTION 3: BATCH LOT & USE BY DATE BARCODES =====
        batch_lot = self.safe_str(row.get('batch_lot_no', ''), '')
        batch_barcode = self.generate_code128(batch_lot)

        if expiry_date_obj:
            use_by_barcode_text = expiry_date_obj.strftime("%d%b%y").upper()
        else:
            use_by_barcode_text = "01JAN99"
        use_by_barcode = self.generate_code128(use_by_barcode_text)

        barcode_row_height = mm_to_px(15, self.dpi)

        # Batch Lot Barcode (left)
        if batch_barcode:
            barcode_width = mm_to_px(55, self.dpi)
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
            barcode_width = mm_to_px(55, self.dpi)
            aspect = use_by_barcode.width / use_by_barcode.height
            new_height = barcode_row_height
            new_width = int(new_height * aspect)
            if new_width > barcode_width:
                new_width = barcode_width
                new_height = int(new_width / aspect)
            use_by_resized = use_by_barcode.resize((new_width, new_height), Image.LANCZOS)
            use_by_x = x_left + mm_to_px(70, self.dpi)
            img.paste(use_by_resized, (use_by_x, y_pos))

        y_pos += barcode_row_height + mm_to_px(2, self.dpi)

        # Batch Lot Managed text (Requirement 1: Format as "B/L: Y" or "B/L: N")
        batch_managed_raw = self.safe_str(row.get('batch_lot_managed', ''), 'N')
        batch_managed = 'Y' if batch_managed_raw.upper() in ['Y', 'YES'] else 'N'
        draw.text((x_left, y_pos), "B/L: ", fill='black', font=font_small)
        blm_width = draw.textbbox((0, 0), "B/L: ", font=font_small)[2]
        draw.text((x_left + blm_width, y_pos), batch_managed, fill='black', font=font_data)

        # Use by Date text
        use_by_x = x_left + mm_to_px(70, self.dpi)
        draw.text((use_by_x, y_pos), "Use by Date: ", fill='black', font=font_small)
        ubd_width = draw.textbbox((0, 0), "Use by Date: ", font=font_small)[2]
        draw.text((use_by_x + ubd_width, y_pos), use_by_date, fill='black', font=font_data)

        y_pos += self.FONT_SIZE_DATA + mm_to_px(4, self.dpi)

        # Separator line
        draw.line([(x_left - 5, y_pos), (x_right + 5, y_pos)], fill='black', width=2)
        y_pos += mm_to_px(3, self.dpi)

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
            ('Batch Lot No.', batch_lot),
            ('Date of Manufacture', dom_formatted),
            ('Capacity or Net Weight', capacity),
            ('Re-Test Date NATO/JSD', use_by_date),
            ('Test Report No.', test_report),
            # Hazardous Material Code removed - now shown in header hazard box
        ]

        row_height = self.FONT_SIZE_DATA + mm_to_px(4, self.dpi)
        col1_width = mm_to_px(45, self.dpi)

        for label, value in table_data:
            # Draw row borders
            draw.rectangle([x_left - 5, y_pos, x_right + 5, y_pos + row_height], outline='black', width=1)
            draw.line([(x_left + col1_width, y_pos), (x_left + col1_width, y_pos + row_height)], fill='black', width=1)

            # Draw text
            text_y = y_pos + mm_to_px(1, self.dpi)
            draw.text((x_left, text_y), label, fill='black', font=font_small)

            # SPECIAL CASE: NATO Code / JSD row (Inline Rendering - Req 4 & 7)
            if label == 'NATO Code / JSD:':
                # Parse the combined value
                nato_code_val, jsd_ref_val = value.split('|')

                # Starting X position for value column
                value_x = x_left + col1_width + mm_to_px(2, self.dpi)
                current_x = value_x

                # BUG FIX 2: Skip rectangle if NATO code is just a placeholder dash
                if nato_code_val == '-':
                    # Draw dash only, no rectangle
                    draw.text((current_x, text_y), nato_code_val, fill='black', font=font_data)
                    dash_width = draw.textbbox((0, 0), nato_code_val, font=font_data)[2]
                    current_x += dash_width + mm_to_px(2, self.dpi)

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
                    current_x = rect_x2 + mm_to_px(2, self.dpi)

                    # Step 6: Draw separator " | "
                    separator = " | "
                    draw.text((current_x, text_y), separator, fill='black', font=font_data)
                    sep_width = draw.textbbox((0, 0), separator, font=font_data)[2]
                    current_x += sep_width

                    # Step 7: Draw JSD Reference text
                    draw.text((current_x, text_y), jsd_ref_val, fill='black', font=font_data)
            else:
                # Standard table cell rendering (unchanged)
                draw.text((x_left + col1_width + mm_to_px(2, self.dpi), text_y), value, fill='black', font=font_data)

            y_pos += row_height

        y_pos += mm_to_px(2, self.dpi)

        # ===== SECTION 5: SAFETY MARKINGS =====
        safety_markings = self.safe_str(row.get('safety_movement_markings', ''), '')
        if safety_markings:
            safety_height = self.FONT_SIZE_SMALL + mm_to_px(4, self.dpi)
            draw.rectangle([x_left - 5, y_pos, x_right + 5, y_pos + safety_height], outline='black', width=1)
            draw.text((x_left, y_pos + mm_to_px(1, self.dpi)), safety_markings, fill='black', font=font_small)
            y_pos += safety_height + mm_to_px(2, self.dpi)

        # ===== SECTION 6: CONTRACTOR DETAILS =====
        contractor_details = self.safe_str(row.get('contractor_details', ''), '')
        if contractor_details:
            lines = contractor_details.split('|')
            box_height = len(lines) * (self.FONT_SIZE_SMALL + mm_to_px(1, self.dpi)) + mm_to_px(3, self.dpi)
            draw.rectangle([x_left - 5, y_pos, x_right + 5, y_pos + box_height], outline='black', width=1)

            text_y = y_pos + mm_to_px(1, self.dpi)
            for line in lines:
                draw.text((x_left, text_y), line.strip(), fill='black', font=font_small)
                text_y += self.FONT_SIZE_SMALL + mm_to_px(1, self.dpi)

        # Save PNG
        img.save(output_path, 'PNG', dpi=(self.dpi, self.dpi))

    def generate_all_labels(self):
        """Generate PNG labels for all records"""
        if not self.load_data():
            return False
        if not self.validate_data():
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"\nGenerating {self.label_size} labels at {self.dpi} DPI...")
        print(f"Label size: {self.label_width_mm}x{self.label_height_mm}mm")
        print(f"Image size with bleed: {self.total_width_mm}x{self.total_height_mm}mm")
        print(f"Image dimensions: {self.total_width_px}x{self.total_height_px}px\n")

        for idx, row in self.data.iterrows():
            product_desc = str(row.get('product_description', f'UNKNOWN_{idx}'))
            batch = str(row.get('batch_lot_no', 'NOBATCH'))
            product_clean = ''.join(c if c.isalnum() or c in '-_' else '_' for c in product_desc)

            png_filename = f"dod_label_{product_clean}_{batch}_{self.label_size}_{timestamp}.png"
            png_path = self.output_folder / png_filename

            try:
                self.create_label_png(row, png_path)
                print(f"Generated PNG: {png_path}")
            except Exception as e:
                print(f"Error generating label for {product_desc}: {e}")
                import traceback
                traceback.print_exc()
                continue

        print(f"\nGeneration complete. Output saved to '{self.output_folder}/'")
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate DoD/NATO military labels as high-resolution PNG images'
    )
    parser.add_argument('data_file', help='CSV or Excel file with label data')
    parser.add_argument('--size', '-s', default='A5',
                       choices=list(LABEL_SIZES.keys()),
                       help='Label size (default: A5)')
    parser.add_argument('--all-sizes', '-a', action='store_true',
                       help='Generate labels in all available sizes')
    parser.add_argument('--dpi', type=int, default=600,
                       help='Output resolution in DPI (default: 600)')

    args = parser.parse_args()

    if not os.path.exists(args.data_file):
        print(f"Error: File '{args.data_file}' not found")
        sys.exit(1)

    if args.all_sizes:
        for size in LABEL_SIZES.keys():
            print(f"\n{'='*60}")
            print(f"Generating {size} labels...")
            print('='*60)
            generator = DoDLabelGeneratorPNG(args.data_file, label_size=size, dpi=args.dpi)
            generator.generate_all_labels()
    else:
        generator = DoDLabelGeneratorPNG(args.data_file, label_size=args.size, dpi=args.dpi)
        success = generator.generate_all_labels()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
