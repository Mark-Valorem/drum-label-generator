#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for JSON SKU workflow
Tests label generation with products.json database
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

def test_json_workflow():
    """Test label generation with JSON product database"""
    print("=" * 60)
    print("JSON SKU Workflow Test")
    print("=" * 60)

    # Load products database
    print("\n1. Loading products.json...")
    products_file = Path("products.json")
    if not products_file.exists():
        print("❌ ERROR: products.json not found!")
        return False

    with open(products_file, 'r') as f:
        products_db = json.load(f)

    print(f"✅ Loaded {len(products_db)} products:")
    for p in products_db:
        print(f"   - {p['id']}: {p['product_name']} ({p['unit_of_issue']})")

    # Test with first product (OM-11 20L)
    print("\n2. Testing with first product (OM-11 20L)...")
    selected_product = products_db[0]

    # Simulate user inputs
    batch_lot_no = "FM251122A"
    date_of_manufacture = datetime.now()
    test_report_no = "-"
    retest_date = date_of_manufacture + timedelta(days=selected_product['shelf_life_months'] * 30)

    print(f"   Batch Lot: {batch_lot_no}")
    print(f"   DOM: {date_of_manufacture.strftime('%d/%m/%Y')}")
    print(f"   Re-Test Date: {retest_date.strftime('%d/%m/%Y')}")
    print(f"   Shelf Life: {selected_product['shelf_life_months']} months")

    # Combine product data with manual inputs
    row_data = {
        'product_description': selected_product['product_name'],
        'nato_stock_no': selected_product['nsn'],
        'nato_code': selected_product['nato_code'],
        'jsd_reference': selected_product['jsd_reference'],
        'specification': selected_product['specification'],
        'batch_lot_no': batch_lot_no,
        'batch_lot_managed': selected_product['batch_lot_managed'],
        'date_of_manufacture': date_of_manufacture.strftime('%d/%m/%Y'),
        'contractor_details': selected_product['contractor_details'],
        'capacity_net_weight': selected_product['capacity_weight'],
        'safety_movement_markings': selected_product['safety_markings'],
        'shelf_life_months': selected_product['shelf_life_months'],
        'test_report_no': test_report_no,
        'unit_of_issue': selected_product['unit_of_issue'],
        'hazardous_material_code': selected_product['hazardous_material_code'],
        'retest_date': retest_date.strftime('%d/%m/%Y'),
    }

    # Generate label
    print("\n3. Generating label...")
    try:
        generator = DoDLabelGenerator(label_size='4" × 6"', dpi=600)
        label_img = generator.create_label_png(row_data)

        # Save test output
        output_dir = Path("output/png")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_json_workflow_{selected_product['id']}_{timestamp}.png"
        filepath = output_dir / filename

        label_img.save(filepath, format='PNG', dpi=(600, 600))
        print(f"✅ Label generated successfully!")
        print(f"   Saved to: {filepath}")
        print(f"   Image size: {label_img.size}")

        # Verify NIIN extraction
        nsn = selected_product['nsn']
        niin = nsn.replace('-', '')[-9:]
        print(f"\n4. Verification:")
        print(f"   NSN: {nsn}")
        print(f"   NIIN (extracted): {niin}")
        print(f"   Use by Date: {(date_of_manufacture + timedelta(days=selected_product['shelf_life_months'] * 30)).strftime('%d %b %y').upper()}")

        return True

    except Exception as e:
        print(f"❌ ERROR generating label: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_json_workflow()
    print("\n" + "=" * 60)
    if success:
        print("✅ JSON WORKFLOW TEST PASSED")
    else:
        print("❌ JSON WORKFLOW TEST FAILED")
    print("=" * 60)
    sys.exit(0 if success else 1)
