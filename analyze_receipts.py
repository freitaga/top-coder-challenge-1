#!/usr/bin/env python3
import json
import subprocess
import statistics
from collections import defaultdict

def load_test_cases():
    with open('public_cases.json', 'r') as f:
        return json.load(f)

def analyze_receipt_rates():
    """Analyze receipt reimbursement rates across different receipt amounts"""
    cases = load_test_cases()
    
    print("=== RECEIPT REIMBURSEMENT RATE ANALYSIS ===")
    print("Looking for patterns in receipt reimbursement rates...\n")
    
    # Group cases by receipt ranges
    receipt_ranges = [
        (0, 0),      # No receipts
        (0.01, 25),
        (25, 50),
        (50, 100),
        (100, 200),
        (200, 500),
        (500, 1000),
        (1000, 1500),
        (1500, 2000),
        (2000, float('inf'))
    ]
    
    by_receipts = defaultdict(list)
    for case in cases:
        receipts = case['input']['total_receipts_amount']
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        expected = case['expected_output']
        
        # Find appropriate range
        for min_receipts, max_receipts in receipt_ranges:
            if min_receipts <= receipts < max_receipts or (receipts == 0 and min_receipts == 0 and max_receipts == 0):
                # Estimate receipt component by subtracting rough per diem and mileage
                est_per_diem = duration * 80  # Rough estimate
                est_mileage = miles * 0.4     # Rough estimate
                est_receipt_reimb = expected - est_per_diem - est_mileage
                
                receipt_rate = est_receipt_reimb / receipts if receipts > 0 else 0
                
                by_receipts[(min_receipts, max_receipts)].append({
                    'receipts': receipts,
                    'duration': duration,
                    'miles': miles,
                    'expected': expected,
                    'est_receipt_reimb': est_receipt_reimb,
                    'receipt_rate': receipt_rate
                })
                break
    
    print("Receipt Range | Count | Avg Rate | Min Rate | Max Rate | Avg Est Reimb")
    print("-" * 70)
    
    for range_key in receipt_ranges:
        cases_in_range = by_receipts[range_key]
        if len(cases_in_range) > 5:  # Only show ranges with sufficient data
            if range_key[0] == 0 and range_key[1] == 0:
                range_str = "No receipts"
                avg_est_reimb = statistics.mean([case['est_receipt_reimb'] for case in cases_in_range])
                print(f"{range_str:13s} | {len(cases_in_range):5d} | {'N/A':8s} | {'N/A':8s} | {'N/A':8s} | {avg_est_reimb:12.2f}")
            else:
                receipt_rates = [case['receipt_rate'] for case in cases_in_range if case['receipts'] > 0]
                
                if receipt_rates:
                    avg_rate = statistics.mean(receipt_rates)
                    min_rate = min(receipt_rates)
                    max_rate = max(receipt_rates)
                    avg_est_reimb = statistics.mean([case['est_receipt_reimb'] for case in cases_in_range])
                    
                    if range_key[1] == float('inf'):
                        range_str = f"${range_key[0]:.0f}+"
                    else:
                        range_str = f"${range_key[0]:.0f}-{range_key[1]:.0f}"
                    
                    print(f"{range_str:13s} | {len(cases_in_range):5d} | {avg_rate:8.2f} | {min_rate:8.2f} | {max_rate:8.2f} | {avg_est_reimb:12.2f}")

def analyze_current_receipt_accuracy():
    """Test our current receipt calculation against expected results"""
    cases = load_test_cases()
    
    print("\n=== CURRENT RECEIPT CALCULATION ACCURACY ===")
    print("Testing cases to isolate receipt reimbursement performance...")
    print("Receipts | Duration | Miles | Expected | Current | Error | Est Receipt Component")
    print("-" * 85)
    
    # Focus on cases with significant receipts but minimal other variables
    receipt_test_cases = []
    for case in cases:
        receipts = case['input']['total_receipts_amount']
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        expected = case['expected_output']
        
        # Look for cases with meaningful receipts but low complexity
        if receipts > 50 and duration <= 3 and miles < 200:
            receipt_test_cases.append(case)
    
    # Sort by receipt amount for easier analysis
    receipt_test_cases.sort(key=lambda x: x['input']['total_receipts_amount'])
    
    total_error = 0
    for case in receipt_test_cases[:25]:  # Test first 25 cases
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Get current result
        result = subprocess.run(['node', 'calculate.js', str(duration), str(miles), str(receipts)], 
                              capture_output=True, text=True)
        current = float(result.stdout.strip())
        error = abs(current - expected)
        total_error += error
        
        # Estimate receipt component
        est_per_diem = duration * 80  # Rough estimate
        est_mileage = miles * 0.4     # Rough estimate
        est_receipt_component = expected - est_per_diem - est_mileage
        
        print(f"{receipts:8.2f} | {duration:8d} | {miles:5.0f} | {expected:8.2f} | {current:7.2f} | {error:5.2f} | {est_receipt_component:18.2f}")
    
    if receipt_test_cases:
        avg_error = total_error / len(receipt_test_cases[:25])
        print(f"\nAverage error in receipt-focused cases: ${avg_error:.2f}")

def analyze_tiny_receipt_patterns():
    """Analyze the 'tiny receipts worse than no receipts' pattern"""
    cases = load_test_cases()
    
    print("\n=== TINY RECEIPT ANALYSIS ===")
    print("Analyzing very small receipt amounts vs no receipts...")
    
    # Compare very small receipts vs no receipts for similar trips
    no_receipt_cases = []
    tiny_receipt_cases = []
    
    for case in cases:
        receipts = case['input']['total_receipts_amount']
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        expected = case['expected_output']
        
        if duration <= 3 and miles < 300:  # Focus on simpler cases
            if receipts == 0:
                no_receipt_cases.append({
                    'duration': duration,
                    'miles': miles,
                    'expected': expected,
                    'per_day': expected / duration
                })
            elif 0 < receipts < 30:
                tiny_receipt_cases.append({
                    'duration': duration,
                    'miles': miles,
                    'receipts': receipts,
                    'expected': expected,
                    'per_day': expected / duration
                })
    
    print(f"No receipt cases (duration <= 3, miles < 300): {len(no_receipt_cases)}")
    print(f"Tiny receipt cases ($0-30, duration <= 3, miles < 300): {len(tiny_receipt_cases)}")
    
    if no_receipt_cases and tiny_receipt_cases:
        no_receipt_avg = statistics.mean([case['per_day'] for case in no_receipt_cases])
        tiny_receipt_avg = statistics.mean([case['per_day'] for case in tiny_receipt_cases])
        
        print(f"Average per-day reimbursement with no receipts: ${no_receipt_avg:.2f}")
        print(f"Average per-day reimbursement with tiny receipts: ${tiny_receipt_avg:.2f}")
        print(f"Difference: ${no_receipt_avg - tiny_receipt_avg:.2f}")
        
        if tiny_receipt_avg < no_receipt_avg:
            print("✓ Confirms: Tiny receipts DO result in lower reimbursements than no receipts")
        else:
            print("✗ Data doesn't support tiny receipt penalty")

def analyze_receipt_thresholds():
    """Look for evidence of specific receipt amount thresholds"""
    cases = load_test_cases()
    
    print("\n=== RECEIPT THRESHOLD ANALYSIS ===")
    print("Looking for breakpoints in receipt reimbursement rates...")
    
    # Focus on 1-day trips with varying receipt amounts
    filtered_cases = []
    for case in cases:
        if (case['input']['trip_duration_days'] == 1 and 
            case['input']['miles_traveled'] < 200 and
            case['input']['total_receipts_amount'] > 0):
            
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            miles = case['input']['miles_traveled']
            
            # Estimate receipt component
            est_per_diem = 170  # Rough 1-day estimate
            est_mileage = miles * 0.4
            est_receipt_component = expected - est_per_diem - est_mileage
            receipt_rate = est_receipt_component / receipts if receipts > 0 else 0
            
            filtered_cases.append({
                'receipts': receipts,
                'expected': expected,
                'est_receipt_component': est_receipt_component,
                'receipt_rate': receipt_rate
            })
    
    # Sort by receipt amount
    filtered_cases.sort(key=lambda x: x['receipts'])
    
    print("Receipts | Expected | Est Receipt Component | Rate")
    print("-" * 50)
    
    for case in filtered_cases[:30]:  # Show first 30
        print(f"{case['receipts']:8.2f} | {case['expected']:8.2f} | {case['est_receipt_component']:18.2f} | {case['receipt_rate']:4.2f}")

if __name__ == "__main__":
    analyze_receipt_rates()
    analyze_current_receipt_accuracy()
    analyze_tiny_receipt_patterns()
    analyze_receipt_thresholds() 