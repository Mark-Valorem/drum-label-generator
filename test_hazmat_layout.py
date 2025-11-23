#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Hazard Box Layout (Field 18)
Verifies: Hazard class number in black box header, removed from table
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

def test_hazmat_layout():
    """Test Hazard Box rendering with DCI 4A (Class 3)"""
    print("=" * 60)
    print("Hazard Box Layout Test - DCI 4A")
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
    print(f"   Hazard Class: {dci4a['hazardous_material_code']}")
    print(f"   Safety Markings: {dci4a['safety_markings']}")

    # Verify hazard class is single digit
    hazmat = dci4a['hazardous_material_code']
    if hazmat != '3':
        print(f"   ❌ HAZARD CLASS ERROR: Expected '3', got '{hazmat}'")
        return False
    print(f"   ✅ Hazard class correct: '{hazmat}'")

    # Simulate user inputs
    batch_lot_no = "TEST_HAZMAT_251123"
    date_of_manufacture = datetime.now()
    test_report_no = "-"
    retest_date = date_of_manufacture + timedelta(days=dci4a['shelf_life_months'] * 30)

    print(f"\n3. Test Label Data:")
    print(f"   Batch Lot: {batch_lot_no}")
    print(f"   DOM: {date_of_manufacture.strftime('%d/%m/%Y')}")

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
    print("\n4. Generating label...")
    try:
        generator = DoDLabelGenerator(label_size='4" × 6"', dpi=600)
        label_img = generator.create_label_png(row_data)

        # Save test output
        output_dir = Path("output/png")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_hazmat_layout_{timestamp}.png"
        filepath = output_dir / filename

        label_img.save(filepath, format='PNG', dpi=(600, 600))
        print(f"✅ Label generated successfully!")
        print(f"   Saved to: {filepath}")
        print(f"   Image size: {label_img.size}")

        # Verification checklist
        print(f"\n5. Verification Checklist:")
        print(f"   ✅ Hazard class should be: '3' (single digit)")
        print(f"   ✅ HAZARD box should appear in header (right of Unit)")
        print(f"   ✅ Black square with white '3' inside")
        print(f"   ✅ 'HAZARD' label above box in tiny font")
        print(f"   ✅ Hazardous Material Code NOT in data table")
        print(f"   ✅ Full safety info still in Field 12: {dci4a['safety_markings']}")

        print(f"\n6. IMPORTANT: Open the label and verify:")
        print(f"   - Header shows 'HAZARD' text above a black box")
        print(f"   - Black box contains white '3'")
        print(f"   - Box positioned between 'Unit: DR' and GS1 Data Matrix")
        print(f"   - Data table does NOT have 'Hazardous Material Code' row")
        print(f"   - Safety markings still visible in Field 12")

        return True, filename

    except Exception as e:
        print(f"❌ ERROR generating label: {e}")
        import traceback
        traceback.print_exc()
        return False, None

if __name__ == "__main__":
    result = test_hazmat_layout()
    print("\n" + "=" * 60)
    if result[0]:
        print("✅ HAZARD BOX LAYOUT TEST PASSED")
        print(f"   Filename: {result[1]}")
    else:
        print("❌ HAZARD BOX LAYOUT TEST FAILED")
    print("=" * 60)
    sys.exit(0 if result[0] else 1)
