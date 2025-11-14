#!/bin/bash

# Drum Label Generator - Quick Setup Script

echo "========================================"
echo "Drum Label Generator - Quick Setup"
echo "========================================"
echo

# Check Python version
echo "Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi
echo

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi
echo

# Run installation test
echo "Running installation test..."
python3 test_installation.py
if [ $? -ne 0 ]; then
    echo
    echo "Warning: Some tests failed. Review output above."
    echo
fi

echo
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Add GHS pictogram PNG files to ghs_pictograms/ folder"
echo "2. Edit config.py with your company details"
echo "3. Prepare your data CSV/Excel file"
echo "4. Generate labels:"
echo "   python3 drum_label_generator.py your_data.csv"
echo
echo "For help, see README.md"
echo
