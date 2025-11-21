#!/usr/bin/env python3
"""
DoD/NATO Label Generator for Valorem Chemicals
Generates military specification labels with multiple barcode symbologies
Version 2.0.0
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from io import BytesIO

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
import barcode
from barcode.writer import ImageWriter
from pylibdmtx.pylibdmtx import encode as dmtx_encode
from PIL import Image

# Configuration
OUTPUT_FOLDER = "output"
FONT_HEADER = "Helvetica-Bold"
FONT_BODY = "Helvetica"
FONT_SIZE_LARGE = 20
FONT_SIZE_HEADER = 14
FONT_SIZE_BODY = 11
FONT_SIZE_SMALL = 8
FONT_SIZE_DATA = 12  # Larger font for field data values

# Page settings (A4)
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 10 * mm


class DoDLabelGenerator:
    """Generate DoD/NATO military specification labels"""

    def __init__(self, data_file):
        """Initialize generator with data file"""
        self.data_file = data_file
        self.data = None
        self.output_folder = Path(OUTPUT_FOLDER)
        self.output_folder.mkdir(exist_ok=True)

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
        """Calculate re-test date and use by date"""
        try:
            date_obj = datetime.strptime(manufacture_date, "%d/%m/%Y")
            months = int(shelf_life_months) if pd.notna(shelf_life_months) else 24
            expiry_date = date_obj + timedelta(days=months * 30)  # Approximate
            # Format as DD MMM YYYY (e.g., "15 NOV 2027")
            return expiry_date.strftime("%d %b %Y").upper(), expiry_date
        except:
            return "N/A", None

    def format_date_display(self, date_str):
        """Convert DD/MM/YYYY to DD MMM YYYY format"""
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            return date_obj.strftime("%d %b %Y").upper()
        except:
            return date_str if date_str and str(date_str) != 'nan' else ""

    def safe_str(self, value, default="-"):
        """Convert value to string, handling nan and None"""
        if pd.isna(value) or value is None or str(value).lower() == 'nan':
            return default
        str_val = str(value).strip()
        # Handle common "blank" indicators (case-insensitive)
        blank_values = ['not applicable or blank', '-/blank', 'n/a', '', '-', 'blank', 'na', 'none']
        if str_val.lower() in blank_values:
            return default
        return str_val

    def generate_code128(self, data):
        """Generate Code 128 barcode image"""
        try:
            data_str = str(data).strip()[:10]  # Max 10 characters per spec
            barcode_class = barcode.get_barcode_class('code128')
            barcode_obj = barcode_class(data_str, writer=ImageWriter())

            buffer = BytesIO()
            barcode_obj.write(buffer, options={
                'module_height': 10,
                'module_width': 0.3,
                'quiet_zone': 3,
                'font_size': 8,
                'text_distance': 2,
            })
            buffer.seek(0)
            return Image.open(buffer)
        except Exception as e:
            print(f"Error generating Code 128 barcode: {e}")
            return None

    def generate_code39(self, data):
        """Generate Code 39 barcode image for NIIN"""
        try:
            # Code 39 for NIIN - 9 digits exactly
            data_str = str(data).strip()
            if not data_str.isdigit() or len(data_str) != 9:
                print(f"Warning: NIIN must be exactly 9 digits: {data_str}")
                data_str = data_str.zfill(9)[:9]

            barcode_class = barcode.get_barcode_class('code39')
            barcode_obj = barcode_class(data_str, writer=ImageWriter(), add_checksum=False)

            buffer = BytesIO()
            barcode_obj.write(buffer, options={
                'module_height': 10,
                'module_width': 0.3,
                'quiet_zone': 3,
                'font_size': 8,
                'text_distance': 2,
            })
            buffer.seek(0)
            return Image.open(buffer)
        except Exception as e:
            print(f"Error generating Code 39 barcode: {e}")
            return None

    def generate_gs1_datamatrix(self, nsn, batch_lot, expiry_date_obj, serial_number=None):
        """
        Generate GS1 Data Matrix (ECC 200) 2D barcode per ISO/IEC 16022

        Data Content per GS1 spec:
        - AI 7001: NSN (n13 - full NSN without hyphens)
        - AI 10: Batch/Lot (an..20) - variable length, needs GS separator
        - AI 17: Expiry Date (n6 - YYMMDD) - fixed length
        - AI 21: Serial Number (an..20) - variable length, needs GS separator

        FNC1/GS (ASCII 29) separates variable-length AI elements
        """
        try:
            # GS character (ASCII 29) - Group Separator for variable-length AIs
            GS = chr(29)

            # AI 7001: NSN (13 digits - remove hyphens from full NSN)
            # Example: "6850-99-224-5252" -> "6850992245252"
            nsn_digits = ''.join(filter(str.isdigit, str(nsn)))
            if len(nsn_digits) != 13:
                print(f"Warning: NSN should be 13 digits, got {len(nsn_digits)}: {nsn_digits}")
                # Pad or truncate to 13 digits
                nsn_digits = nsn_digits.zfill(13)[-13:]

            # AI 10: Batch/Lot (up to 20 characters) - variable length
            batch_str = str(batch_lot)[:20] if batch_lot and pd.notna(batch_lot) else ""

            # AI 17: Expiry date (YYMMDD) - fixed length n6
            if expiry_date_obj:
                expiry_str = expiry_date_obj.strftime("%y%m%d")
            else:
                expiry_str = "990101"  # Default

            # Build GS1 string per spec:
            # AI 7001 is fixed length (n13), no GS needed after
            # AI 10 is variable length (an..20), needs GS after
            # AI 17 is fixed length (n6), no GS needed after (unless followed by variable AI)
            # AI 21 is variable length (an..20), needs GS after if not last

            # Format: 7001{NSN}[GS]10{Batch}[GS]17{YYMMDD}
            gs1_data = f"7001{nsn_digits}{GS}10{batch_str}{GS}17{expiry_str}"

            # Add serial number if provided
            if serial_number and pd.notna(serial_number):
                serial_str = str(serial_number)[:20]
                gs1_data += f"{GS}21{serial_str}"

            # Generate Data Matrix with GS1 encoding
            encoded = dmtx_encode(gs1_data.encode('utf-8'))
            img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)

            # Scale up for better visibility
            scale = 4
            img = img.resize((encoded.width * scale, encoded.height * scale), Image.NEAREST)

            return img
        except Exception as e:
            print(f"Error generating GS1 Data Matrix: {e}")
            return None

    def create_label(self, row, output_path):
        """Create single DoD/NATO label PDF"""
        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4

        # Starting positions
        y_pos = height - MARGIN
        x_left = MARGIN
        x_right = width - MARGIN
        content_width = x_right - x_left

        # Calculate dates
        use_by_date, expiry_date_obj = self.calculate_dates(
            row.get('date_of_manufacture', '01/01/2025'),
            row.get('shelf_life_months', 24)
        )

        # Get formatted date of manufacture
        dom_formatted = self.format_date_display(str(row.get('date_of_manufacture', '')))

        # ===== SECTION 1: HEADER (Fields 4, 11) - OUTSIDE BORDER =====
        # Field 4: Product Description (Large, centered) - above border
        c.setFont(FONT_HEADER, FONT_SIZE_LARGE)
        product_desc = self.safe_str(row.get('product_description', ''), 'N/A')
        text_width = c.stringWidth(product_desc, FONT_HEADER, FONT_SIZE_LARGE)
        c.drawString((width - text_width) / 2, y_pos - 5, product_desc)
        y_pos -= 30

        # Field 11: NATO Stock No. (Centered, bold) - above border
        c.setFont(FONT_HEADER, FONT_SIZE_HEADER)
        nato_stock = self.safe_str(row.get('nato_stock_no', ''), 'N/A')
        text_width = c.stringWidth(nato_stock, FONT_HEADER, FONT_SIZE_HEADER)
        c.drawString((width - text_width) / 2, y_pos, nato_stock)
        y_pos -= 20

        # Save border top position (after header)
        border_top = y_pos

        # Draw outer border for label content (below header)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(x_left, MARGIN, content_width, border_top - MARGIN)

        # Horizontal line at top of bordered area
        c.line(x_left, y_pos, x_right, y_pos)

        # ===== SECTION 2: NIIN BARCODE ROW (Fields 15, 16, 17, 18, 21) =====
        y_pos -= 5

        # Field 16: NIIN Linear Barcode (Code 39) - Left
        niin = self.safe_str(row.get('niin', ''), '000000000')
        niin_barcode = self.generate_code39(niin)

        # Field 17: Unit of Issue
        unit_issue = self.safe_str(row.get('unit_of_issue', ''), 'DR')

        # Field 18: Hazardous Material Code
        hazmat = self.safe_str(row.get('hazardous_material_code', ''), '')

        # Generate GS1 Data Matrix (Field 21)
        datamatrix = self.generate_gs1_datamatrix(
            nato_stock,
            row.get('batch_lot_no', ''),
            expiry_date_obj,
            row.get('serial_number', None)
        )

        barcode_y = y_pos - 20

        # NIIN Barcode (left side)
        if niin_barcode:
            niin_img_buffer = BytesIO()
            niin_barcode.save(niin_img_buffer, format='PNG')
            niin_img_buffer.seek(0)
            niin_reader = ImageReader(niin_img_buffer)
            c.drawImage(niin_reader, x_left + 5, barcode_y, width=55*mm, height=15*mm, preserveAspectRatio=True)

        # Unit of Issue (center-left) - label normal, value bold and larger
        c.setFont(FONT_BODY, FONT_SIZE_SMALL)
        c.drawString(x_left + 62*mm, barcode_y + 10, "Unit: ")
        c.setFont(FONT_HEADER, FONT_SIZE_DATA)  # Bold and larger for value
        c.drawString(x_left + 62*mm + c.stringWidth("Unit: ", FONT_BODY, FONT_SIZE_SMALL), barcode_y + 10, unit_issue)

        # Hazmat Code (center-right) - multiline
        c.setFont(FONT_BODY, FONT_SIZE_SMALL)
        if hazmat:
            hazmat_lines = hazmat.split(',')
            hazmat_y = barcode_y + 10
            for line in hazmat_lines[:4]:  # Max 4 lines
                c.drawString(x_left + 85*mm, hazmat_y, line.strip())
                hazmat_y -= 8

        # GS1 Data Matrix (far right)
        if datamatrix:
            dm_img_buffer = BytesIO()
            datamatrix.save(dm_img_buffer, format='PNG')
            dm_img_buffer.seek(0)
            dm_reader = ImageReader(dm_img_buffer)
            c.drawImage(dm_reader, x_right - 28*mm, barcode_y - 8, width=25*mm, height=25*mm, preserveAspectRatio=True)

        y_pos = barcode_y - 18

        # Field 15: NIIN text label below NIIN barcode
        c.setFont(FONT_BODY, FONT_SIZE_SMALL)
        c.drawString(x_left + 5, y_pos, "NIIN: ")
        c.setFont(FONT_HEADER, FONT_SIZE_DATA)  # Bold and larger for value
        c.drawString(x_left + 5 + c.stringWidth("NIIN: ", FONT_BODY, FONT_SIZE_SMALL), y_pos, niin)

        y_pos -= 20  # Increased gap to prevent overlap with Batch Lot barcode

        # Horizontal line after section 2
        c.line(x_left, y_pos, x_right, y_pos)

        # ===== SECTION 3: BATCH LOT & USE BY DATE BARCODES (Fields 6, 7, 19, 20) =====
        y_pos -= 5

        # Field 6: Batch Lot Managed
        batch_managed = self.safe_str(row.get('batch_lot_managed', ''), 'N')

        # Field 7: Batch Lot No. Linear Barcode (Code 128) - Left
        batch_lot = self.safe_str(row.get('batch_lot_no', ''), '')
        batch_barcode = self.generate_code128(batch_lot)

        # Field 20: Use by Date Linear Barcode (Code 128) - Right
        if expiry_date_obj:
            use_by_barcode_text = expiry_date_obj.strftime("%d%b%y").upper()  # Compact for barcode
        else:
            use_by_barcode_text = "01JAN99"
        use_by_barcode = self.generate_code128(use_by_barcode_text)

        batch_barcode_y = y_pos - 18

        # Batch Lot Barcode (left half)
        if batch_barcode:
            batch_img_buffer = BytesIO()
            batch_barcode.save(batch_img_buffer, format='PNG')
            batch_img_buffer.seek(0)
            batch_reader = ImageReader(batch_img_buffer)
            c.drawImage(batch_reader, x_left + 5, batch_barcode_y, width=70*mm, height=15*mm, preserveAspectRatio=True)

        # Use by Date Barcode (right half)
        if use_by_barcode:
            use_by_img_buffer = BytesIO()
            use_by_barcode.save(use_by_img_buffer, format='PNG')
            use_by_img_buffer.seek(0)
            use_by_reader = ImageReader(use_by_img_buffer)
            c.drawImage(use_by_reader, x_left + 100*mm, batch_barcode_y, width=70*mm, height=15*mm, preserveAspectRatio=True)

        y_pos = batch_barcode_y - 15

        # Field 6: Batch Lot Managed (below batch barcode) - label normal, value bold and larger
        c.setFont(FONT_BODY, FONT_SIZE_SMALL)
        c.drawString(x_left + 5, y_pos, "Batch Lot Managed: ")
        c.setFont(FONT_HEADER, FONT_SIZE_DATA)  # Bold and larger for value
        c.drawString(x_left + 5 + c.stringWidth("Batch Lot Managed: ", FONT_BODY, FONT_SIZE_SMALL), y_pos, batch_managed)

        # Field 19: Use by Date text (below use by barcode) - label normal, value bold and larger
        c.setFont(FONT_BODY, FONT_SIZE_SMALL)
        c.drawString(x_left + 100*mm, y_pos, "Use by Date: ")
        c.setFont(FONT_HEADER, FONT_SIZE_DATA)  # Bold and larger for value
        c.drawString(x_left + 100*mm + c.stringWidth("Use by Date: ", FONT_BODY, FONT_SIZE_SMALL), y_pos, use_by_date)

        y_pos -= 12

        # Horizontal line after section 3
        c.line(x_left, y_pos, x_right, y_pos)

        # ===== SECTION 4: INFORMATION TABLE =====
        y_pos -= 3

        # Get field values with proper nan handling
        nato_code = self.safe_str(row.get('nato_code', ''), '')
        jsd_ref = self.safe_str(row.get('jsd_reference', ''), '')
        spec = self.safe_str(row.get('specification', ''), '')
        capacity = self.safe_str(row.get('capacity_net_weight', ''), '')
        test_report = self.safe_str(row.get('test_report_no', ''), '-')

        # Build table data - match exact format from specification
        table_data = [
            # Row 0: NATO Code & JSD Reference (3 columns)
            ['NATO Code & JSD Reference:', nato_code, jsd_ref],
            # Row 1: Specification (spans columns 1-2)
            ['Specification:', spec, ''],
            # Row 2: Batch Lot No. (spans columns 1-2)
            ['Batch Lot No.', batch_lot, ''],
            # Row 3: Date of Manufacture (spans columns 1-2)
            ['Date of Manufacture', dom_formatted, ''],
            # Row 4: Capacity or Net Weight (spans columns 1-2)
            ['Capacity or Net Weight', capacity, ''],
            # Row 5: Re-Test Date NATO/JSD products (spans columns 1-2)
            ['Re-Test Date NATO/JSD products', use_by_date, ''],
            # Row 6: Test Report No. (spans columns 1-2)
            ['Test Report No.', test_report, ''],
        ]

        # Create table with proper column widths
        col_widths = [55*mm, 65*mm, 60*mm]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Font styles - Labels normal (small), Data bold (larger)
            ('FONT', (0, 0), (0, -1), FONT_BODY, FONT_SIZE_SMALL),   # Left column (labels) - normal, small
            ('FONT', (1, 0), (-1, -1), FONT_HEADER, FONT_SIZE_DATA), # Other columns (data) - bold, larger
            # Alignment
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # Span columns 1-2 for rows 1-6 (except row 0 which has 3 distinct values)
            ('SPAN', (1, 1), (2, 1)),  # Specification
            ('SPAN', (1, 2), (2, 2)),  # Batch Lot No.
            ('SPAN', (1, 3), (2, 3)),  # Date of Manufacture
            ('SPAN', (1, 4), (2, 4)),  # Capacity or Net Weight
            ('SPAN', (1, 5), (2, 5)),  # Re-Test Date
            ('SPAN', (1, 6), (2, 6)),  # Test Report No.
        ]))

        table_width, table_height = table.wrapOn(c, content_width, height)
        table.drawOn(c, x_left, y_pos - table_height)
        y_pos -= (table_height + 3)

        # ===== SECTION 5: SAFETY AND MOVEMENT MARKINGS (Field 12) =====
        safety_markings = self.safe_str(row.get('safety_movement_markings', ''), '')
        if safety_markings:
            safety_table = Table([[safety_markings]], colWidths=[content_width])
            safety_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), FONT_BODY, FONT_SIZE_SMALL),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            safety_width, safety_height = safety_table.wrapOn(c, content_width, height)
            safety_table.drawOn(c, x_left, y_pos - safety_height)
            y_pos -= (safety_height + 3)

        # ===== SECTION 6: CONTRACTOR'S DETAILS (Field 9) =====
        contractor_details = self.safe_str(row.get('contractor_details', ''), '')
        if contractor_details:
            # Replace pipe delimiters with newlines
            contractor_text = contractor_details.replace('|', '\n')
            contractor_table = Table([[contractor_text]], colWidths=[content_width])
            contractor_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), FONT_BODY, FONT_SIZE_SMALL),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            contractor_width, contractor_height = contractor_table.wrapOn(c, content_width, height)
            contractor_table.drawOn(c, x_left, y_pos - contractor_height)
            y_pos -= contractor_height

        # Finalize
        c.save()
        print(f"Generated: {output_path}")

    def generate_all_labels(self):
        """Generate labels for all records in data file"""
        if not self.load_data():
            return False

        if not self.validate_data():
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for idx, row in self.data.iterrows():
            product_desc = str(row.get('product_description', f'UNKNOWN_{idx}'))
            batch = str(row.get('batch_lot_no', 'NOBATCH'))

            # Clean filename
            product_clean = ''.join(c if c.isalnum() or c in '-_' else '_' for c in product_desc)

            filename = f"dod_label_{product_clean}_{batch}_{timestamp}.pdf"
            output_path = self.output_folder / filename

            try:
                self.create_label(row, output_path)
            except Exception as e:
                print(f"Error generating label for {product_desc}: {e}")
                import traceback
                traceback.print_exc()
                continue

        print(f"\nGeneration complete. Output saved to '{self.output_folder}/'")
        return True


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python dod_label_generator.py <data_file.csv|data_file.xlsx>")
        print("Example: python dod_label_generator.py sample_data_dod.csv")
        sys.exit(1)

    data_file = sys.argv[1]

    if not os.path.exists(data_file):
        print(f"Error: File '{data_file}' not found")
        sys.exit(1)

    generator = DoDLabelGenerator(data_file)
    success = generator.generate_all_labels()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
