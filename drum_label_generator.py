#!/usr/bin/env python3
"""
Drum Label Generator for Valorem Chemicals
Generates A5 GHS-compliant drum labels from CSV/Excel data
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from io import BytesIO

import pandas as pd
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
import barcode
from barcode.writer import ImageWriter
import qrcode
from PIL import Image

import config


class DrumLabelGenerator:
    """Generate GHS-compliant drum labels from data"""
    
    def __init__(self, data_file):
        """
        Initialize generator with data file
        
        Args:
            data_file: Path to CSV or Excel file
        """
        self.data_file = data_file
        self.data = None
        self.output_folder = Path(config.OUTPUT_FOLDER)
        self.ghs_folder = Path(config.GHS_PICTOGRAM_FOLDER)
        
        # Create output folder if it doesn't exist
        self.output_folder.mkdir(exist_ok=True)
        
        # Validate GHS pictogram folder exists
        if not self.ghs_folder.exists():
            print(f"Warning: GHS pictogram folder '{self.ghs_folder}' not found.")
            print("Please add GHS pictogram PNG files to this folder.")
    
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
        required_columns = ['product_code', 'product_name', 'batch_number']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        
        if missing_columns:
            print(f"Error: Missing required columns: {', '.join(missing_columns)}")
            return False
        
        return True
    
    def generate_barcode(self, data, barcode_type='code128'):
        """
        Generate barcode image
        
        Args:
            data: Data to encode
            barcode_type: Barcode type (code128, ean13, etc)
        
        Returns:
            PIL Image object
        """
        try:
            # Create barcode
            barcode_class = barcode.get_barcode_class(barcode_type)
            barcode_obj = barcode_class(str(data), writer=ImageWriter())
            
            # Generate to BytesIO
            buffer = BytesIO()
            barcode_obj.write(buffer, options={
                'module_height': 10,
                'module_width': 0.2,
                'quiet_zone': 2,
                'font_size': 8,
                'text_distance': 2,
            })
            buffer.seek(0)
            
            return Image.open(buffer)
            
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None
    
    def generate_qr_code(self, data):
        """
        Generate QR code image
        
        Args:
            data: Data to encode
        
        Returns:
            PIL Image object
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=2,
            )
            qr.add_data(str(data))
            qr.make(fit=True)
            
            return qr.make_image(fill_color="black", back_color="white")
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None
    
    def load_ghs_pictogram(self, pictogram_code):
        """
        Load GHS pictogram image
        
        Args:
            pictogram_code: GHS code (e.g., 'GHS02', 'GHS07')
        
        Returns:
            PIL Image object or None
        """
        # Try different possible filenames
        possible_names = [
            f"{pictogram_code}.png",
            f"{pictogram_code.upper()}.png",
            f"{pictogram_code.lower()}.png",
        ]
        
        for name in possible_names:
            path = self.ghs_folder / name
            if path.exists():
                try:
                    return Image.open(path)
                except Exception as e:
                    print(f"Error loading pictogram {path}: {e}")
        
        print(f"Warning: GHS pictogram '{pictogram_code}' not found")
        return None
    
    def create_label(self, row, output_path):
        """
        Create single drum label PDF
        
        Args:
            row: DataFrame row with label data
            output_path: Output PDF path
        """
        # Create canvas
        c = canvas.Canvas(str(output_path), pagesize=A5)
        width, height = A5
        
        # Starting Y position (from top)
        y_pos = height - config.MARGIN_TOP * mm
        x_left = config.MARGIN_LEFT * mm
        x_right = width - config.MARGIN_RIGHT * mm
        content_width = x_right - x_left
        
        # 1. Company header
        c.setFont(config.FONT_COMPANY, config.FONT_SIZE_COMPANY)
        c.drawString(x_left, y_pos, config.COMPANY_NAME)
        y_pos -= 15
        
        c.setFont(config.FONT_SMALL, config.FONT_SIZE_SMALL)
        c.drawString(x_left, y_pos, f"{config.COMPANY_ADDRESS} | {config.COMPANY_PHONE}")
        y_pos -= 20
        
        # 2. Product header section
        c.setFont(config.FONT_HEADER, config.FONT_SIZE_HEADER)
        product_name = str(row.get('product_name', 'N/A'))
        c.drawString(x_left, y_pos, product_name[:60])  # Truncate if too long
        y_pos -= 15
        
        # 3. Main information table
        table_data = []
        
        # Helper to add row
        def add_row(label, value):
            if pd.notna(value) and str(value).strip():
                table_data.append([label, str(value)])
        
        add_row("Product Code:", row.get('product_code', 'N/A'))
        add_row("Batch Number:", row.get('batch_number', 'N/A'))
        add_row("Supplier:", row.get('supplier', ''))
        add_row("Net Weight:", row.get('net_weight', ''))
        add_row("Gross Weight:", row.get('gross_weight', ''))
        
        # UN information if present
        if pd.notna(row.get('un_number')):
            add_row("UN Number:", row.get('un_number', ''))
            add_row("Proper Shipping Name:", row.get('proper_shipping_name', ''))
            add_row("Hazard Class:", row.get('hazard_class', ''))
            add_row("Packing Group:", row.get('packing_group', ''))
        
        add_row("Manufactured:", row.get('manufacture_date', ''))
        add_row("Expiry:", row.get('expiry_date', ''))
        
        # Create table
        if table_data:
            col_widths = [config.LABEL_COL_WIDTH * mm, config.VALUE_COL_WIDTH * mm]
            
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), config.FONT_BODY, config.FONT_SIZE_BODY),
                ('FONT', (0, 0), (0, -1), config.FONT_HEADER, config.FONT_SIZE_BODY),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), config.TABLE_CELL_PADDING),
                ('RIGHTPADDING', (0, 0), (-1, -1), config.TABLE_CELL_PADDING),
                ('TOPPADDING', (0, 0), (-1, -1), config.TABLE_CELL_PADDING),
                ('BOTTOMPADDING', (0, 0), (-1, -1), config.TABLE_CELL_PADDING),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            table_width, table_height = table.wrapOn(c, content_width, height)
            table.drawOn(c, x_left, y_pos - table_height)
            y_pos -= (table_height + 10)
        
        # 4. GHS Pictograms
        ghs_codes = str(row.get('ghs_pictograms', '')).split(',')
        ghs_codes = [code.strip() for code in ghs_codes if code.strip()]
        
        if ghs_codes:
            c.setFont(config.FONT_HEADER, config.FONT_SIZE_BODY)
            c.drawString(x_left, y_pos, "GHS Hazard Pictograms:")
            y_pos -= 15
            
            x_pictogram = x_left
            pictogram_size = config.PICTOGRAM_SIZE * mm
            
            for ghs_code in ghs_codes[:5]:  # Max 5 pictograms
                pictogram_img = self.load_ghs_pictogram(ghs_code)
                if pictogram_img:
                    # Convert PIL to ImageReader
                    img_buffer = BytesIO()
                    pictogram_img.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    img_reader = ImageReader(img_buffer)
                    
                    c.drawImage(img_reader, x_pictogram, y_pos - pictogram_size, 
                              width=pictogram_size, height=pictogram_size, 
                              preserveAspectRatio=True, mask='auto')
                    
                    x_pictogram += pictogram_size + (config.PICTOGRAM_SPACING * mm)
            
            y_pos -= (pictogram_size + 10)
        
        # 5. Hazard and Precautionary Statements
        hazard_statements = str(row.get('hazard_statements', '')).replace('|', '\n• ')
        if hazard_statements and hazard_statements != 'nan':
            c.setFont(config.FONT_HEADER, config.FONT_SIZE_BODY)
            c.drawString(x_left, y_pos, "Hazard Statements:")
            y_pos -= 12
            
            c.setFont(config.FONT_BODY, config.FONT_SIZE_SMALL)
            text_obj = c.beginText(x_left + 5, y_pos)
            text_obj.textLines("• " + hazard_statements)
            c.drawText(text_obj)
            y_pos -= (text_obj.getY() - y_pos) + 15
        
        precautionary = str(row.get('precautionary_statements', '')).replace('|', '\n• ')
        if precautionary and precautionary != 'nan':
            c.setFont(config.FONT_HEADER, config.FONT_SIZE_BODY)
            c.drawString(x_left, y_pos, "Precautionary Statements:")
            y_pos -= 12
            
            c.setFont(config.FONT_BODY, config.FONT_SIZE_SMALL)
            text_obj = c.beginText(x_left + 5, y_pos)
            text_obj.textLines("• " + precautionary)
            c.drawText(text_obj)
            y_pos -= (text_obj.getY() - y_pos) + 15
        
        # 6. Storage instructions
        storage = str(row.get('storage_instructions', ''))
        if storage and storage != 'nan':
            c.setFont(config.FONT_HEADER, config.FONT_SIZE_BODY)
            c.drawString(x_left, y_pos, "Storage:")
            y_pos -= 12
            
            c.setFont(config.FONT_BODY, config.FONT_SIZE_SMALL)
            c.drawString(x_left + 5, y_pos, storage[:80])
            y_pos -= 15
        
        # 7. Emergency contact
        emergency = str(row.get('emergency_contact', ''))
        if emergency and emergency != 'nan':
            c.setFont(config.FONT_HEADER, config.FONT_SIZE_BODY)
            c.setFillColor(colors.HexColor('#CC0000'))
            c.drawString(x_left, y_pos, "Emergency Contact:")
            y_pos -= 12
            
            c.setFont(config.FONT_BODY, config.FONT_SIZE_SMALL)
            c.setFillColor(colors.black)
            c.drawString(x_left + 5, y_pos, emergency)
            y_pos -= 20
        
        # 8. Barcode (bottom section)
        barcode_data = str(row.get('product_code', '')) + str(row.get('batch_number', ''))
        if barcode_data:
            barcode_img = self.generate_barcode(barcode_data)
            if barcode_img:
                img_buffer = BytesIO()
                barcode_img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                img_reader = ImageReader(img_buffer)
                
                barcode_width = config.BARCODE_WIDTH * mm
                barcode_height = config.BARCODE_HEIGHT * mm
                
                c.drawImage(img_reader, x_left, y_pos - barcode_height,
                          width=barcode_width, height=barcode_height,
                          preserveAspectRatio=True)
        
        # 9. QR Code (bottom right)
        qr_data = str(row.get('qr_data', ''))
        if not qr_data or qr_data == 'nan':
            qr_data = f"{row.get('product_code', '')}|{row.get('batch_number', '')}|{row.get('manufacture_date', '')}"
        
        if qr_data:
            qr_img = self.generate_qr_code(qr_data)
            if qr_img:
                img_buffer = BytesIO()
                qr_img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                img_reader = ImageReader(img_buffer)
                
                qr_size = config.QR_SIZE * mm
                qr_x = x_right - qr_size
                qr_y = config.MARGIN_BOTTOM * mm
                
                c.drawImage(img_reader, qr_x, qr_y,
                          width=qr_size, height=qr_size,
                          preserveAspectRatio=True)
        
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
            product_code = str(row.get('product_code', f'UNKNOWN_{idx}'))
            batch = str(row.get('batch_number', 'NOBATCH'))
            
            filename = f"drum_label_{product_code}_{batch}_{timestamp}.pdf"
            output_path = self.output_folder / filename
            
            try:
                self.create_label(row, output_path)
            except Exception as e:
                print(f"Error generating label for {product_code}: {e}")
                continue
        
        print(f"\nGeneration complete. Output saved to '{self.output_folder}/'")
        return True


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python drum_label_generator.py <data_file.csv|data_file.xlsx>")
        print("Example: python drum_label_generator.py sample_data.csv")
        sys.exit(1)
    
    data_file = sys.argv[1]
    
    if not os.path.exists(data_file):
        print(f"Error: File '{data_file}' not found")
        sys.exit(1)
    
    generator = DrumLabelGenerator(data_file)
    success = generator.generate_all_labels()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
