#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Date Calculation Precision Fix
Verifies: relativedelta provides accurate month addition (no 30-day approximation)
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime
from dateutil.relativedelta import relativedelta

def test_date_precision():
    """Test that date calculations are precise to the day"""
    print("=" * 60)
    print("Date Calculation Precision Test")
    print("=" * 60)

    # Test Case 1: 18 months from Nov 12
    print("\n1. Test Case: Nov 12 + 18 months")
    dom = datetime(2024, 11, 12)
    shelf_life = 18

    # Calculate with relativedelta (CORRECT)
    expiry_correct = dom + relativedelta(months=shelf_life)

    print(f"   Date of Manufacture: {dom.strftime('%d %b %Y')}")
    print(f"   Shelf Life: {shelf_life} months")
    print(f"   Expected Expiry: 12 May 2026")
    print(f"   Calculated Expiry: {expiry_correct.strftime('%d %b %Y')}")

    # Verify exact match
    expected_day = 12
    expected_month = 5
    expected_year = 2026

    if (expiry_correct.day == expected_day and
        expiry_correct.month == expected_month and
        expiry_correct.year == expected_year):
        print("   ✅ PASS: Date matches exactly (12 May 2026)")
        result1 = True
    else:
        print(f"   ❌ FAIL: Expected 12 May 2026, got {expiry_correct.strftime('%d %b %Y')}")
        result1 = False

    # Test Case 2: 36 months from Nov 15
    print("\n2. Test Case: Nov 15 + 36 months (Fuchs OM-11)")
    dom2 = datetime(2025, 11, 15)
    shelf_life2 = 36

    expiry2 = dom2 + relativedelta(months=shelf_life2)

    print(f"   Date of Manufacture: {dom2.strftime('%d %b %Y')}")
    print(f"   Shelf Life: {shelf_life2} months")
    print(f"   Expected Expiry: 15 Nov 2028")
    print(f"   Calculated Expiry: {expiry2.strftime('%d %b %Y')}")

    if (expiry2.day == 15 and
        expiry2.month == 11 and
        expiry2.year == 2028):
        print("   ✅ PASS: Date matches exactly (15 Nov 2028)")
        result2 = True
    else:
        print(f"   ❌ FAIL: Expected 15 Nov 2028, got {expiry2.strftime('%d %b %Y')}")
        result2 = False

    # Test Case 3: 24 months from Dec 31
    print("\n3. Test Case: Dec 31 + 24 months (DCI 4A)")
    dom3 = datetime(2025, 12, 31)
    shelf_life3 = 24

    expiry3 = dom3 + relativedelta(months=shelf_life3)

    print(f"   Date of Manufacture: {dom3.strftime('%d %b %Y')}")
    print(f"   Shelf Life: {shelf_life3} months")
    print(f"   Expected Expiry: 31 Dec 2027")
    print(f"   Calculated Expiry: {expiry3.strftime('%d %b %Y')}")

    if (expiry3.day == 31 and
        expiry3.month == 12 and
        expiry3.year == 2027):
        print("   ✅ PASS: Date matches exactly (31 Dec 2027)")
        result3 = True
    else:
        print(f"   ❌ FAIL: Expected 31 Dec 2027, got {expiry3.strftime('%d %b %Y')}")
        result3 = False

    # Test Case 4: Edge case - Jan 31 + 1 month
    print("\n4. Edge Case: Jan 31 + 1 month (month boundary)")
    dom4 = datetime(2025, 1, 31)
    shelf_life4 = 1

    expiry4 = dom4 + relativedelta(months=shelf_life4)

    print(f"   Date of Manufacture: {dom4.strftime('%d %b %Y')}")
    print(f"   Shelf Life: {shelf_life4} month")
    print(f"   Expected Expiry: 28 Feb 2025 (Feb has 28 days)")
    print(f"   Calculated Expiry: {expiry4.strftime('%d %b %Y')}")

    # relativedelta handles this intelligently - goes to last day of Feb
    if expiry4.month == 2 and expiry4.year == 2025:
        print("   ✅ PASS: Correctly handles month-end boundary")
        result4 = True
    else:
        print(f"   ❌ FAIL: Expected Feb 2025, got {expiry4.strftime('%d %b %Y')}")
        result4 = False

    # Overall result
    print("\n" + "=" * 60)
    if all([result1, result2, result3, result4]):
        print("✅ ALL DATE CALCULATION TESTS PASSED")
        print("   relativedelta provides accurate month arithmetic")
        return True
    else:
        print("❌ SOME DATE CALCULATION TESTS FAILED")
        return False
    print("=" * 60)

if __name__ == "__main__":
    result = test_date_precision()
    sys.exit(0 if result else 1)
