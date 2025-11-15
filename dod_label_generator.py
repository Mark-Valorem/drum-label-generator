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
FONT_SIZE_LARGE = 16
FONT_SIZE_HEADER = 12
FONT_SIZE_BODY = 10
FONT_SIZE_SMALL = 8

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
            return expiry_date.strftime("%d/%m/%Y"), expiry_date
        except:
            return "N/A", None

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
        """Generate GS1 Data Matrix (ECC 200) 2D barcode"""
        try:
            # Extract NIIN from NSN (last 9 digits, no separators)
            niin = ''.join(filter(str.isdigit, str(nsn)))[-9:]

            # Build GS1 data string with Application Identifiers
            # AI 7001: NSN (13 digits - add country code 6135 prefix for NIIN)
            nsn_full = f"6135{niin}"  # Country code + NIIN = 13 digits

            # AI 10: Batch/Lot (up to 20 characters)
            batch_str = str(batch_lot)[:20]

            # AI 17: Expiry date (YYMMDD)
            if expiry_date_obj:
                expiry_str = expiry_date_obj.strftime("%y%m%d")
            else:
                expiry_str = "990101"  # Default

            # Build GS1 string: FNC1 + (7001) + NSN + FNC1 + (10) + Batch + FNC1 + (17) + Date
            # FNC1 is handled internally by GS1 encoding
            gs1_data = f"7001{nsn_full}10{batch_str}17{expiry_str}"

            if serial_number and pd.notna(serial_number):
                serial_str = str(serial_number)[:20]
                gs1_data += f"21{serial_str}"

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

        # ===== HEADER SECTION =====

        # Field 4: Product Description (Large, centered)
        c.setFont(FONT_HEADER, FONT_SIZE_LARGE)
        product_desc = str(row.get('product_description', 'N/A'))
        text_width = c.stringWidth(product_desc, FONT_HEADER, FONT_SIZE_LARGE)
        c.drawString((width - text_width) / 2, y_pos, product_desc)
        y_pos -= 25

        # Field 11: NATO Stock No. (Centered, bold)
        c.setFont(FONT_HEADER, FONT_SIZE_HEADER)
        nato_stock = str(row.get('nato_stock_no', 'N/A'))
        text_width = c.stringWidth(nato_stock, FONT_HEADER, FONT_SIZE_HEADER)
        c.drawString((width - text_width) / 2, y_pos, nato_stock)
        y_pos -= 20

        # ===== TOP BARCODE/INFO SECTION =====

        # Field 16: NIIN Linear Barcode (Code 39) - Top Left
        niin = str(row.get('niin', '000000000'))
        niin_barcode = self.generate_code39(niin)

        # Field 17: Unit of Issue, Field 18: Hazardous Material Code, Field 21: GS1 Matrix
        unit_issue = str(row.get('unit_of_issue', 'DR'))
        hazmat = str(row.get('hazardous_material_code', 'N/A'))

        # Generate GS1 Data Matrix (Field 21)
        datamatrix = self.generate_gs1_datamatrix(
            nato_stock,
            row.get('batch_lot_no', ''),
            expiry_date_obj,
            row.get('serial_number', None)
        )

        # Layout top section
        barcode_y = y_pos - 30

        # NIIN Barcode (left)
        if niin_barcode:
            niin_img_buffer = BytesIO()
            niin_barcode.save(niin_img_buffer, format='PNG')
            niin_img_buffer.seek(0)
            niin_reader = ImageReader(niin_img_buffer)
            c.drawImage(niin_reader, x_left, barcode_y, width=60*mm, height=15*mm, preserveAspectRatio=True)

        # Unit of Issue (center-left)
        c.setFont(FONT_BODY, FONT_SIZE_BODY)
        c.drawString(x_left + 65*mm, barcode_y + 12*mm, f"Unit: {unit_issue}")

        # Hazmat Code (center-right)
        c.setFont(FONT_BODY, FONT_SIZE_SMALL)
        hazmat_lines = hazmat.split(',')
        hazmat_y = barcode_y + 12*mm
        for line in hazmat_lines:
            c.drawString(x_left + 95*mm, hazmat_y, line.strip())
            hazmat_y -= 10

        # GS1 Data Matrix (far right)
        if datamatrix:
            dm_img_buffer = BytesIO()
            datamatrix.save(dm_img_buffer, format='PNG')
            dm_img_buffer.seek(0)
            dm_reader = ImageReader(dm_img_buffer)
            c.drawImage(dm_reader, x_right - 25*mm, barcode_y, width=25*mm, height=25*mm, preserveAspectRatio=True)

        # Field 15: NIIN (text below barcode)
        c.setFont(FONT_BODY, FONT_SIZE_BODY)
        c.drawString(x_left + 10*mm, barcode_y - 5, f"NIIN: {niin}")

        y_pos = barcode_y - 15

        # ===== MIDDLE BARCODE SECTION =====

        # Field 7: Batch Lot No. Linear Barcode (Code 128) - Left
        batch_lot = str(row.get('batch_lot_no', ''))
        batch_barcode = self.generate_code128(batch_lot)

        # Field 20: Use by Date Linear Barcode (Code 128) - Right
        # Format: "DD MMM YY" (9 characters)
        if expiry_date_obj:
            use_by_formatted = expiry_date_obj.strftime("%d %b %y").upper()
        else:
            use_by_formatted = "01 JAN 99"
        use_by_barcode = self.generate_code128(use_by_formatted)

        batch_barcode_y = y_pos - 20

        # Batch Lot Barcode (left)
        if batch_barcode:
            batch_img_buffer = BytesIO()
            batch_barcode.save(batch_img_buffer, format='PNG')
            batch_img_buffer.seek(0)
            batch_reader = ImageReader(batch_img_buffer)
            c.drawImage(batch_reader, x_left, batch_barcode_y, width=80*mm, height=15*mm, preserveAspectRatio=True)

        # Use by Date Barcode (right)
        if use_by_barcode:
            use_by_img_buffer = BytesIO()
            use_by_barcode.save(use_by_img_buffer, format='PNG')
            use_by_img_buffer.seek(0)
            use_by_reader = ImageReader(use_by_img_buffer)
            c.drawImage(use_by_reader, x_left + 105*mm, batch_barcode_y, width=80*mm, height=15*mm, preserveAspectRatio=True)

        # Field 6: Batch Lot Managed (below batch barcode)
        c.setFont(FONT_BODY, FONT_SIZE_SMALL)
        batch_managed = str(row.get('batch_lot_managed', 'N'))
        c.drawString(x_left, batch_barcode_y - 10, f"Batch Lot Managed: {batch_managed}")

        # Field 19: Use by Date (below use by barcode)
        c.drawString(x_left + 105*mm, batch_barcode_y - 10, f"Use by Date: {use_by_date}")

        y_pos = batch_barcode_y - 25

        # ===== INFORMATION TABLE =====

        table_data = []

        # NATO Code & JSD Reference row
        nato_code = str(row.get('nato_code', ''))
        jsd_ref = str(row.get('jsd_reference', ''))
        if nato_code or jsd_ref:
            table_data.append(['NATO Code & JSD Reference:', nato_code, jsd_ref])

        # Specification
        spec = str(row.get('specification', ''))
        if spec and spec != 'nan':
            table_data.append(['Specification:', spec, ''])

        # Batch Lot No.
        table_data.append(['Batch Lot No.', batch_lot, ''])

        # Date of Manufacture
        dom = str(row.get('date_of_manufacture', ''))
        table_data.append(['Date of Manufacture', dom, ''])

        # Capacity or Net Weight
        capacity = str(row.get('capacity_net_weight', ''))
        table_data.append(['Capacity or Net Weight', capacity, ''])

        # Re-Test Date
        table_data.append(['Re-Test Date NATO/JSD products', use_by_date, ''])

        # Test Report No.
        test_report = str(row.get('test_report_no', '-/Blank'))
        table_data.append(['Test Report No.', test_report, ''])

        # Create table
        col_widths = [60*mm, 60*mm, 60*mm]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), FONT_HEADER, FONT_SIZE_SMALL),
            ('FONT', (1, 0), (-1, -1), FONT_BODY, FONT_SIZE_SMALL),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (1, 1), (2, 1)),  # Specification row spans 2 columns
        ]))

        table_width, table_height = table.wrapOn(c, content_width, height)
        table.drawOn(c, x_left, y_pos - table_height)
        y_pos -= (table_height + 5)

        # Safety and Movement Markings (Field 12) - Full width row
        safety_markings = str(row.get('safety_movement_markings', ''))
        if safety_markings and safety_markings != 'nan':
            safety_table = Table([[safety_markings]], colWidths=[content_width])
            safety_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), FONT_BODY, FONT_SIZE_SMALL),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            safety_width, safety_height = safety_table.wrapOn(c, content_width, height)
            safety_table.drawOn(c, x_left, y_pos - safety_height)
            y_pos -= (safety_height + 5)

        # Contractor's Details (Field 9) - Full width row
        contractor_details = str(row.get('contractor_details', ''))
        if contractor_details and contractor_details != 'nan':
            # Replace pipe delimiters with newlines
            contractor_text = contractor_details.replace('|', '\n')
            contractor_table = Table([[contractor_text]], colWidths=[content_width])
            contractor_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), FONT_BODY, FONT_SIZE_SMALL),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
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
