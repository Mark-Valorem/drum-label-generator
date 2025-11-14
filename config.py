"""
Configuration file for drum label generator
All measurements in millimeters unless specified
"""

# Page settings
PAGE_WIDTH = 148  # A5 width in mm
PAGE_HEIGHT = 210  # A5 height in mm

# Margins
MARGIN_TOP = 8
MARGIN_BOTTOM = 8
MARGIN_LEFT = 8
MARGIN_RIGHT = 8

# Font settings
FONT_COMPANY = "Helvetica-Bold"
FONT_HEADER = "Helvetica-Bold"
FONT_BODY = "Helvetica"
FONT_SMALL = "Helvetica"

FONT_SIZE_COMPANY = 14
FONT_SIZE_HEADER = 10
FONT_SIZE_BODY = 9
FONT_SIZE_SMALL = 7

# Colors (RGB)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (0.8, 0, 0)
COLOR_BORDER = (0.3, 0.3, 0.3)

# Table layout
TABLE_CELL_PADDING = 2
ROW_HEIGHT = 12  # Default row height in mm
LABEL_COL_WIDTH = 45  # Width of label column (left)
VALUE_COL_WIDTH = 95  # Width of value column (right)

# Pictogram settings
PICTOGRAM_SIZE = 20  # Width/height in mm
PICTOGRAM_SPACING = 2  # Space between pictograms

# Barcode settings
BARCODE_HEIGHT = 15  # Height in mm
BARCODE_WIDTH = 70  # Width in mm

# QR code settings
QR_SIZE = 25  # Width/height in mm

# Company details (customize for Valorem)
COMPANY_NAME = "Valorem Chemicals Pty Ltd"
COMPANY_ADDRESS = "Sydney, NSW, Australia"
COMPANY_PHONE = "+61 (0)2 XXXX XXXX"
COMPANY_EMAIL = "info@valoremchemicals.com.au"

# GHS pictogram folder
GHS_PICTOGRAM_FOLDER = "ghs_pictograms"

# Output folder
OUTPUT_FOLDER = "output"
