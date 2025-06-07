#!/usr/bin/env python3
import json

def analyze_one_day_cases():
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    one_day_cases = [case for case in cases if case['input']['trip_duration_days'] == 1]
    
    print(f"Found {len(one_day_cases)} 1-day cases")
    print("Miles | Receipts | Expected | Miles Component | Receipt Component | Remainder")
    print("-" * 80)
    
    for case in one_day_cases[:20]:  # Show first 20 cases
        miles = case['input']['miles_traveled'] 
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Estimate mileage component (using approximation)
        if miles <= 100:
            miles_comp = miles * 0.62
        elif miles <= 300:
            miles_comp = (100 * 0.62) + (miles - 100) * 0.52
        elif miles <= 600:
            miles_comp = (100 * 0.62) + (200 * 0.52) + (miles - 300) * 0.42
        else:
            miles_comp = (100 * 0.62) + (200 * 0.52) + (300 * 0.42) + (miles - 600) * 0.32
        
        # Estimate receipt component (basic approximation)
        if receipts <= 150:
            receipt_comp = receipts * 0.85
        elif receipts <= 800:
            receipt_comp = (150 * 0.85) + (receipts - 150) * 0.65
        elif receipts <= 1500:
            receipt_comp = (150 * 0.85) + (650 * 0.65) + (receipts - 800) * 0.45
        else:
            receipt_comp = (150 * 0.85) + (650 * 0.65) + (700 * 0.45) + (receipts - 1500) * 0.30
        
        remainder = expected - miles_comp - receipt_comp
        
        print(f"{miles:5.0f} | {receipts:8.2f} | {expected:8.2f} | {miles_comp:15.2f} | {receipt_comp:17.2f} | {remainder:9.2f}")

if __name__ == "__main__":
    analyze_one_day_cases() 