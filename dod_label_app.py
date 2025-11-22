#!/usr/bin/env python3
"""
DoD/NATO Label Generator - Streamlit Web Dashboard
Generates military specification labels with web interface
Version 2.2.0
"""

import os
import io
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
        """Calculate re-test date and use by date"""
        try:
            date_obj = datetime.strptime(str(manufacture_date), "%d/%m/%Y")
            months = int(shelf_life_months) if pd.notna(shelf_life_months) else 24
            expiry_date = date_obj + timedelta(days=months * 30)
            return expiry_date.strftime("%d %b %Y").upper(), expiry_date
        except:
            return "N/A", None

    def format_date_display(self, date_str):
        """Convert DD/MM/YYYY to DD MMM YYYY format"""
        try:
            date_obj = datetime.strptime(str(date_str), "%d/%m/%Y")
            return date_obj.strftime("%d %b %Y").upper()
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
                'font_size': 8,
                'text_distance': 2,
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
                'font_size': 8,
                'text_distance': 2,
            })
            buffer.seek(0)
            img = Image.open(buffer)
            return img.copy()
        except Exception as e:
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
            if serial_number and pd.notna(serial_number) and str(serial_number).strip():
                gs1_data += f"{GS}21{str(serial_number)[:20]}"
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
        batch_managed = self.safe_str(row.get('batch_lot_managed', ''), 'N')

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

        # GS1 Data Matrix (far right)
        datamatrix = self.generate_gs1_datamatrix(
            nato_stock,
            row.get('batch_lot_no', ''),
            expiry_date_obj,
            row.get('serial_number', None)
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

        # Batch Lot Managed text
        draw.text((x_left, y_pos), "Batch Lot Managed: ", fill='black', font=font_small)
        blm_width = draw.textbbox((0, 0), "Batch Lot Managed: ", font=font_small)[2]
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

        table_data = [
            ('NATO Code & JSD:', f"{nato_code}  {jsd_ref}"),
            ('Specification:', spec),
            ('Batch Lot No.:', batch_lot if batch_lot else '-'),
            ('Date of Manufacture:', dom_formatted),
            ('Capacity/Net Weight:', capacity),
            ('Re-Test Date:', use_by_date),
            ('Test Report No.:', test_report),
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
            draw.text((x_left + col1_width + mm_to_px(1, self.dpi), text_y), value, fill='black', font=font_data)

            y_pos += row_height

        y_pos += mm_to_px(1, self.dpi)

        # ===== SECTION 5: FIELD 12 - SAFETY AND MOVEMENT MARKINGS (CRITICAL) =====
        # Always display this field prominently, even if empty
        safety_markings = self.safe_str(row.get('safety_movement_markings', ''), '-')

        # Header for safety section
        safety_header_height = self.FONT_SIZE_SMALL + mm_to_px(2, self.dpi)
        draw.rectangle([x_left - 3, y_pos, x_right + 3, y_pos + safety_header_height],
                      fill=(240, 240, 240), outline='black', width=1)
        draw.text((x_left, y_pos + mm_to_px(0.5, self.dpi)),
                 "Field 12: Safety & Movement Markings", fill='black', font=font_small)
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
        1. Upload a CSV or Excel file
        2. Select label size per row
        3. Preview labels
        4. Download as PNG, PDF, or ZIP

        **Required Columns:**
        - `product_description`
        - `nato_stock_no`
        - `niin`
        - `batch_lot_no`
        - `date_of_manufacture`

        **Field 12 (Safety Markings):**
        - Column: `safety_movement_markings`
        - Always displayed on label
        """)

        st.markdown("---")
        st.markdown("**v2.2.0** | Valorem Chemicals")

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

    # File upload
    st.markdown("### 📁 Upload Data File")
    uploaded_file = st.file_uploader(
        "Drag and drop CSV or Excel file here",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a file containing product data. Each row will generate one label."
    )

    if uploaded_file is not None:
        # Load data
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.success(f"✅ Loaded {len(df)} rows from {uploaded_file.name}")

            # Add Label Size column if not present
            if 'Label Size' not in df.columns:
                df['Label Size'] = DEFAULT_LABEL_SIZE

            # Display editable data table
            st.markdown("### 📊 Edit Data & Select Label Sizes")
            st.markdown("*Edit values directly in the table. Select label size for each row.*")

            # Configure column for label size dropdown
            column_config = {
                'Label Size': st.column_config.SelectboxColumn(
                    'Label Size',
                    options=list(LABEL_SIZES.keys()),
                    default=DEFAULT_LABEL_SIZE,
                    required=True,
                )
            }

            # Editable dataframe
            edited_df = st.data_editor(
                df,
                column_config=column_config,
                num_rows="dynamic",
                use_container_width=True,
                height=400
            )

            st.markdown("---")

            # Preview section
            st.markdown("### 👁️ Label Preview")

            col1, col2 = st.columns([1, 2])

            with col1:
                preview_row = st.selectbox(
                    "Select row to preview:",
                    options=range(len(edited_df)),
                    format_func=lambda x: f"Row {x+1}: {edited_df.iloc[x].get('product_description', 'Unknown')}"
                )

            with col2:
                if st.button("🔄 Refresh Preview", type="primary"):
                    st.rerun()

            # Generate preview
            if preview_row is not None:
                row_data = edited_df.iloc[preview_row].to_dict()
                label_size = row_data.get('Label Size', DEFAULT_LABEL_SIZE)

                generator = DoDLabelGenerator(label_size=label_size)
                preview_img = generator.create_label_png(row_data)

                # Display preview
                st.image(preview_img, caption=f"Label Preview - {label_size}", use_container_width=True)

            st.markdown("---")

            # Download section
            st.markdown("### 📥 Download Labels")

            # Option to save to output folder
            save_to_folder = st.checkbox("💾 Also save to output folder", value=True,
                                         help="Save files to the project's output/ folder in addition to browser download")

            # Create output directories if needed
            output_png_dir = Path("output/png")
            output_pdf_dir = Path("output/pdf")
            if save_to_folder:
                output_png_dir.mkdir(parents=True, exist_ok=True)
                output_pdf_dir.mkdir(parents=True, exist_ok=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📷 Download All PNGs", type="secondary", use_container_width=True):
                    with st.spinner("Generating PNG labels..."):
                        png_files = []
                        saved_paths = []
                        for idx, row in edited_df.iterrows():
                            row_data = row.to_dict()
                            label_size = row_data.get('Label Size', DEFAULT_LABEL_SIZE)
                            generator = DoDLabelGenerator(label_size=label_size)
                            img = generator.create_label_png(row_data)

                            # Save to buffer
                            buffer = BytesIO()
                            img.save(buffer, format='PNG', dpi=(DPI, DPI))
                            buffer.seek(0)

                            filename = f"label_{idx+1}_{row_data.get('product_description', 'unknown')}.png"
                            filename = "".join(c if c.isalnum() or c in '-_.' else '_' for c in filename)
                            png_files.append((filename, buffer.getvalue()))

                            # Also save to output folder if enabled
                            if save_to_folder:
                                filepath = output_png_dir / filename
                                img.save(filepath, format='PNG', dpi=(DPI, DPI))
                                saved_paths.append(str(filepath))

                        # Create ZIP
                        zip_buffer = BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                            for filename, data in png_files:
                                zf.writestr(filename, data)
                        zip_buffer.seek(0)

                        st.download_button(
                            label="💾 Save PNG Files (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name="dod_labels_png.zip",
                            mime="application/zip"
                        )

                        if save_to_folder and saved_paths:
                            st.success(f"✅ {len(saved_paths)} PNG files saved to: output/png/")

            with col2:
                if HAS_REPORTLAB:
                    if st.button("📄 Download All PDFs", type="secondary", use_container_width=True):
                        with st.spinner("Generating PDF labels..."):
                            pdf_files = []
                            saved_paths = []
                            for idx, row in edited_df.iterrows():
                                row_data = row.to_dict()
                                label_size = row_data.get('Label Size', DEFAULT_LABEL_SIZE)
                                generator = DoDLabelGenerator(label_size=label_size)
                                img = generator.create_label_png(row_data)

                                # Convert PNG to PDF
                                pdf_buffer = BytesIO()
                                img_width_pt = generator.total_width_mm * 72 / 25.4
                                img_height_pt = generator.total_height_mm * 72 / 25.4

                                pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=(img_width_pt, img_height_pt))
                                img_buffer = BytesIO()
                                img.save(img_buffer, format='PNG')
                                img_buffer.seek(0)
                                pdf_canvas.drawImage(ImageReader(img_buffer), 0, 0, width=img_width_pt, height=img_height_pt)
                                pdf_canvas.save()
                                pdf_buffer.seek(0)

                                filename = f"label_{idx+1}_{row_data.get('product_description', 'unknown')}.pdf"
                                filename = "".join(ch if ch.isalnum() or ch in '-_.' else '_' for ch in filename)
                                pdf_files.append((filename, pdf_buffer.getvalue()))

                                # Also save to output folder if enabled
                                if save_to_folder:
                                    filepath = output_pdf_dir / filename
                                    with open(filepath, 'wb') as f:
                                        f.write(pdf_buffer.getvalue())
                                    saved_paths.append(str(filepath))

                            # Create ZIP
                            zip_buffer = BytesIO()
                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                                for filename, data in pdf_files:
                                    zf.writestr(filename, data)
                            zip_buffer.seek(0)

                            st.download_button(
                                label="💾 Save PDF Files (ZIP)",
                                data=zip_buffer.getvalue(),
                                file_name="dod_labels_pdf.zip",
                                mime="application/zip"
                            )

                            if save_to_folder and saved_paths:
                                st.success(f"✅ {len(saved_paths)} PDF files saved to: output/pdf/")
                else:
                    st.warning("PDF export requires ReportLab library")

            with col3:
                if st.button("📦 Download ZIP (All PNGs)", type="primary", use_container_width=True):
                    with st.spinner("Creating ZIP archive..."):
                        zip_buffer = BytesIO()
                        saved_paths = []
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                            for idx, row in edited_df.iterrows():
                                row_data = row.to_dict()
                                label_size = row_data.get('Label Size', DEFAULT_LABEL_SIZE)
                                generator = DoDLabelGenerator(label_size=label_size)
                                img = generator.create_label_png(row_data)

                                # Save to buffer
                                img_buffer = BytesIO()
                                img.save(img_buffer, format='PNG', dpi=(DPI, DPI))
                                img_buffer.seek(0)

                                filename = f"label_{idx+1}_{row_data.get('product_description', 'unknown')}.png"
                                filename = "".join(ch if ch.isalnum() or ch in '-_.' else '_' for ch in filename)
                                zf.writestr(filename, img_buffer.getvalue())

                                # Also save to output folder if enabled
                                if save_to_folder:
                                    filepath = output_png_dir / filename
                                    img.save(filepath, format='PNG', dpi=(DPI, DPI))
                                    saved_paths.append(str(filepath))

                        zip_buffer.seek(0)

                        st.download_button(
                            label="💾 Save ZIP Archive",
                            data=zip_buffer.getvalue(),
                            file_name="dod_labels.zip",
                            mime="application/zip"
                        )

                        if save_to_folder and saved_paths:
                            st.success(f"✅ {len(saved_paths)} PNG files saved to: output/png/")

        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
            st.exception(e)

    else:
        # Show sample data format
        st.markdown("### 📋 Sample Data Format")
        sample_df = pd.DataFrame({
            'product_description': ['Fuchs OM-11', 'DCI 4A'],
            'nato_stock_no': ['9150-66-035-7879', '6850-99-224-5252'],
            'niin': ['660357879', '992245252'],
            'batch_lot_no': ['FM251115A', 'DC251115B'],
            'date_of_manufacture': ['15/11/2025', '15/11/2025'],
            'shelf_life_months': [36, 24],
            'safety_movement_markings': ['-', 'UN1307, Flammable Liquid, Class 3, PG III'],
            'Label Size': [DEFAULT_LABEL_SIZE, DEFAULT_LABEL_SIZE],
        })
        st.dataframe(sample_df, use_container_width=True)

        # Download sample CSV
        csv_buffer = BytesIO()
        sample_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        st.download_button(
            label="📥 Download Sample CSV",
            data=csv_buffer.getvalue(),
            file_name="sample_data_dod.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()
