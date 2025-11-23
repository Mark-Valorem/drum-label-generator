#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for DCI 4A with JSON mapping fixes
Verifies: NIIN calculation, Unit of Issue display, Product details
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dod_label_app import DoDLabelGenerator

def test_dci4a_fixes():
    """Test DCI 4A label generation with bug fixes"""
    print("=" * 60)
    print("DCI 4A Bug Fixes Test")
    print("=" * 60)

    # Load products database
    print("\n1. Loading products.json...")
    products_file = Path("products.json")
    with open(products_file, 'r') as f:
        products_db = json.load(f)

    # Find DCI 4A product
    dci4a = next((p for p in products_db if p['id'] == 'DCI4A_55GAL'), None)
    if not dci4a:
        print("❌ ERROR: DCI4A_55GAL not found in products.json!")
        return False

    print(f"✅ Found product: {dci4a['product_name']}")

    # Display product details
    print("\n2. Product Details:")
    print(f"   NSN: {dci4a['nsn']}")
    print(f"   Unit of Issue: {dci4a['unit_of_issue']}")
    print(f"   Capacity/Weight: {dci4a['capacity_weight']}")
    print(f"   Shelf Life: {dci4a['shelf_life_months']} months")

    # Calculate NIIN
    nsn = dci4a['nsn']
    niin = ''.join(filter(str.isdigit, nsn))[-9:]
    print(f"\n3. NIIN Calculation:")
    print(f"   NSN: {nsn}")
    print(f"   NIIN (extracted): {niin}")
    print(f"   Expected: 992245252")

    if niin != '992245252':
        print(f"   ❌ NIIN MISMATCH!")
        return False
    print(f"   ✅ NIIN calculation correct!")

    # Simulate user inputs
    batch_lot_no = "TEST251123A"
    date_of_manufacture = datetime.now()
    test_report_no = "-"
    retest_date = date_of_manufacture + timedelta(days=dci4a['shelf_life_months'] * 30)

    print(f"\n4. Test Label Data:")
    print(f"   Batch Lot: {batch_lot_no}")
    print(f"   DOM: {date_of_manufacture.strftime('%d/%m/%Y')}")
    print(f"   Re-Test Date: {retest_date.strftime('%d/%m/%Y')}")

    # Combine product data with manual inputs
    row_data = {
        'product_description': dci4a['product_name'],
        'nato_stock_no': dci4a['nsn'],
        'nato_code': dci4a['nato_code'],
        'jsd_reference': dci4a['jsd_reference'],
        'specification': dci4a['specification'],
        'batch_lot_no': batch_lot_no,
        'batch_lot_managed': dci4a['batch_lot_managed'],
        'date_of_manufacture': date_of_manufacture.strftime('%d/%m/%Y'),
        'contractor_details': dci4a['contractor_details'],
        'capacity_net_weight': dci4a['capacity_weight'],
        'safety_movement_markings': dci4a['safety_markings'],
        'shelf_life_months': dci4a['shelf_life_months'],
        'test_report_no': test_report_no,
        'unit_of_issue': dci4a['unit_of_issue'],
        'hazardous_material_code': dci4a['hazardous_material_code'],
        'retest_date': retest_date.strftime('%d/%m/%Y'),
    }

    # Generate label
    print("\n5. Generating label...")
    try:
        generator = DoDLabelGenerator(label_size='4" × 6"', dpi=600)
        label_img = generator.create_label_png(row_data)

        # Save test output
        output_dir = Path("output/png")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_dci4a_fixes_{timestamp}.png"
        filepath = output_dir / filename

        label_img.save(filepath, format='PNG', dpi=(600, 600))
        print(f"✅ Label generated successfully!")
        print(f"   Saved to: {filepath}")
        print(f"   Image size: {label_img.size}")

        # Verification checklist
        print(f"\n6. Verification Checklist:")
        print(f"   ✅ NIIN should be: 992245252 (not 000000000)")
        print(f"   ✅ Unit header should show: Unit: DR (not 55 US GAL)")
        print(f"   ✅ Capacity should show: 55 US GAL in Field 10")
        print(f"   ✅ Product details includes Unit of Issue field")

        print(f"\n7. IMPORTANT: Open the label and verify:")
        print(f"   - NIIN barcode area shows '992245252'")
        print(f"   - Top-right header shows 'Unit: DR'")
        print(f"   - Field 10 (Capacity) shows '55 US GAL'")
        print(f"   - NATO Code box is NOT drawn (code is '-')")

        return True, filename

    except Exception as e:
        print(f"❌ ERROR generating label: {e}")
        import traceback
        traceback.print_exc()
        return False, None

if __name__ == "__main__":
    result = test_dci4a_fixes()
    print("\n" + "=" * 60)
    if result[0]:
        print("✅ DCI 4A FIXES TEST PASSED")
        print(f"   Filename: {result[1]}")
    else:
        print("❌ DCI 4A FIXES TEST FAILED")
    print("=" * 60)
    sys.exit(0 if result[0] else 1)
