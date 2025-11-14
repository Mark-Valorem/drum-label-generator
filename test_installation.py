#!/usr/bin/env python3
"""
Test script to verify drum label generator installation
"""

import sys
import os
from pathlib import Path

def test_dependencies():
    """Test that all required packages are installed"""
    print("Testing dependencies...")
    
    required_packages = {
        'reportlab': 'reportlab',
        'pandas': 'pandas',
        'barcode': 'python-barcode',
        'qrcode': 'qrcode',
        'PIL': 'Pillow',
    }
    
    missing = []
    
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\nInstall missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    print("\nAll dependencies installed ✓")
    return True


def test_directories():
    """Test that required directories exist"""
    print("\nTesting directory structure...")
    
    required_dirs = [
        'ghs_pictograms',
        'output',
    ]
    
    for dirname in required_dirs:
        path = Path(dirname)
        if path.exists():
            print(f"✓ {dirname}/")
        else:
            print(f"✗ {dirname}/ - creating...")
            path.mkdir(exist_ok=True)
    
    return True


def test_ghs_pictograms():
    """Check for GHS pictogram files"""
    print("\nChecking GHS pictograms...")
    
    ghs_folder = Path('ghs_pictograms')
    ghs_codes = ['GHS01', 'GHS02', 'GHS03', 'GHS04', 'GHS05', 
                 'GHS06', 'GHS07', 'GHS08', 'GHS09']
    
    found = []
    missing = []
    
    for code in ghs_codes:
        # Try different case variations
        variants = [f"{code}.png", f"{code.lower()}.png", f"{code.upper()}.png"]
        found_variant = False
        
        for variant in variants:
            if (ghs_folder / variant).exists():
                found.append(code)
                found_variant = True
                break
        
        if not found_variant:
            missing.append(code)
    
    if found:
        print(f"✓ Found {len(found)} pictograms: {', '.join(found)}")
    
    if missing:
        print(f"\n⚠ Missing {len(missing)} pictograms: {', '.join(missing)}")
        print("Download from: https://unece.org/transport/standards/transport-dangerous-goods/ghs-pictograms")
        print("Place PNG files in ghs_pictograms/ folder")
    
    return len(found) > 0


def test_sample_data():
    """Check sample data file exists"""
    print("\nChecking sample data...")
    
    if Path('sample_data.csv').exists():
        print("✓ sample_data.csv exists")
        return True
    else:
        print("✗ sample_data.csv not found")
        return False


def test_generate_label():
    """Test generating a sample label"""
    print("\nTesting label generation...")
    
    if not Path('sample_data.csv').exists():
        print("✗ Cannot test - sample_data.csv not found")
        return False
    
    try:
        from drum_label_generator import DrumLabelGenerator
        
        generator = DrumLabelGenerator('sample_data.csv')
        
        # Test loading data
        if not generator.load_data():
            print("✗ Failed to load data")
            return False
        
        print(f"✓ Loaded {len(generator.data)} records")
        
        # Test validation
        if not generator.validate_data():
            print("✗ Data validation failed")
            return False
        
        print("✓ Data validation passed")
        
        # Generate first label only as test
        first_row = generator.data.iloc[0]
        test_output = Path('output') / 'TEST_LABEL.pdf'
        
        generator.create_label(first_row, test_output)
        
        if test_output.exists():
            print(f"✓ Test label generated: {test_output}")
            print(f"  Product: {first_row.get('product_name', 'N/A')}")
            return True
        else:
            print("✗ Label generation failed")
            return False
            
    except Exception as e:
        print(f"✗ Error during test: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Drum Label Generator - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Directories", test_directories),
        ("GHS Pictograms", test_ghs_pictograms),
        ("Sample Data", test_sample_data),
        ("Label Generation", test_generate_label),
    ]
    
    results = {}
    
    for name, test_func in tests:
        results[name] = test_func()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ All tests passed! Ready to generate labels.")
        print("\nUsage: python drum_label_generator.py sample_data.csv")
    else:
        print("\n⚠ Some tests failed. Review output above.")
        
        if not results.get("GHS Pictograms"):
            print("\nNote: Script will still work, but GHS pictograms won't display")
            print("      until PNG files are added to ghs_pictograms/ folder")
    
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
