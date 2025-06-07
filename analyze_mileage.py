#!/usr/bin/env python3
import json
import statistics
from collections import defaultdict

def load_test_cases():
    with open('public_cases.json', 'r') as f:
        return json.load(f)

def analyze_mileage_patterns():
    cases = load_test_cases()
    
    print("=== MILEAGE ANALYSIS ===")
    print("Looking for patterns in mileage reimbursement rates...\n")
    
    # Group cases by mileage ranges
    mileage_ranges = [
        (0, 50),
        (50, 100),
        (100, 200),
        (200, 300),
        (300, 400),
        (400, 500),
        (500, 600),
        (600, 700),
        (700, 800),
        (800, 900),
        (900, 1000),
        (1000, 1200)
    ]
    
    by_mileage = defaultdict(list)
    for case in cases:
        miles = case['input']['miles_traveled']
        duration = case['input']['trip_duration_days']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Find appropriate range
        for min_miles, max_miles in mileage_ranges:
            if min_miles <= miles < max_miles:
                by_mileage[(min_miles, max_miles)].append({
                    'miles': miles,
                    'duration': duration,
                    'receipts': receipts,
                    'expected': expected,
                    'per_mile': expected / miles if miles > 0 else 0
                })
                break
    
    print("Mileage Range | Count | Avg $/Mile | Min $/Mile | Max $/Mile | Std Dev")
    print("-" * 75)
    
    for range_key in sorted(by_mileage.keys()):
        cases_in_range = by_mileage[range_key]
        if len(cases_in_range) > 5:  # Only show ranges with sufficient data
            per_mile_values = [case['per_mile'] for case in cases_in_range if case['miles'] > 0]
            
            if per_mile_values:
                avg_per_mile = statistics.mean(per_mile_values)
                min_per_mile = min(per_mile_values)
                max_per_mile = max(per_mile_values)
                std_dev = statistics.stdev(per_mile_values) if len(per_mile_values) > 1 else 0
                
                range_str = f"{range_key[0]}-{range_key[1]}"
                print(f"{range_str:12s} | {len(cases_in_range):5d} | {avg_per_mile:10.2f} | {min_per_mile:10.2f} | {max_per_mile:10.2f} | {std_dev:7.2f}")

def analyze_low_variable_cases():
    """Analyze cases with low receipts and short duration to isolate mileage component"""
    cases = load_test_cases()
    
    print("\n=== MILEAGE ISOLATION ANALYSIS ===")
    print("Cases with low receipts (<$50) and short duration (1-2 days) to isolate mileage rates:")
    print("Miles | Duration | Receipts | Expected | Est Per Diem | Est Receipts | Est Mileage | $/Mile")
    print("-" * 90)
    
    isolated_cases = []
    for case in cases:
        miles = case['input']['miles_traveled']
        duration = case['input']['trip_duration_days']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Look for cases with minimal other variables
        if receipts < 50 and duration <= 2 and miles > 0:
            # Estimate per diem component (rough approximation)
            if duration == 1:
                est_per_diem = 170  # From our per day analysis
            else:
                est_per_diem = duration * 100
            
            # Estimate receipt component (rough)
            est_receipts = receipts * 0.8 if receipts > 0 else 0
            
            # Estimated mileage component
            est_mileage = expected - est_per_diem - est_receipts
            per_mile = est_mileage / miles if miles > 0 else 0
            
            isolated_cases.append({
                'miles': miles,
                'duration': duration,
                'receipts': receipts,
                'expected': expected,
                'per_mile': per_mile
            })
            
            if len(isolated_cases) <= 20:  # Show first 20
                print(f"{miles:5.0f} | {duration:8d} | {receipts:8.2f} | {expected:8.2f} | {est_per_diem:11.2f} | {est_receipts:12.2f} | {est_mileage:11.2f} | {per_mile:6.2f}")
    
    if isolated_cases:
        per_mile_rates = [case['per_mile'] for case in isolated_cases]
        print(f"\nAverage $/mile in isolated cases: {statistics.mean(per_mile_rates):.3f}")
        print(f"Min $/mile: {min(per_mile_rates):.3f}")
        print(f"Max $/mile: {max(per_mile_rates):.3f}")

def analyze_mileage_tiers():
    """Look for evidence of tiered mileage rates"""
    cases = load_test_cases()
    
    print("\n=== MILEAGE TIER ANALYSIS ===")
    print("Looking for tiered rates at common breakpoints (100, 300, 600 miles)...")
    
    # Focus on cases with similar duration and low receipts
    filtered_cases = []
    for case in cases:
        miles = case['input']['miles_traveled']
        duration = case['input']['trip_duration_days']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # 1-day trips with low receipts to minimize other variables
        if duration == 1 and receipts < 100 and miles > 0:
            filtered_cases.append({
                'miles': miles,
                'expected': expected,
                'receipts': receipts
            })
    
    # Sort by mileage
    filtered_cases.sort(key=lambda x: x['miles'])
    
    print("Miles | Expected | Receipts | Estimated Mileage Component")
    print("-" * 55)
    
    for case in filtered_cases[:30]:  # Show first 30
        miles = case['miles']
        expected = case['expected'] 
        receipts = case['receipts']
        
        # Rough estimate of mileage component
        est_per_diem = 170  # Base for 1-day
        est_receipts = receipts * 0.8
        est_mileage = expected - est_per_diem - est_receipts
        
        print(f"{miles:5.0f} | {expected:8.2f} | {receipts:8.2f} | {est_mileage:19.2f}")

if __name__ == "__main__":
    analyze_mileage_patterns()
    analyze_low_variable_cases()
    analyze_mileage_tiers() 