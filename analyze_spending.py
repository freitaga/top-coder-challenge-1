#!/usr/bin/env python3
import json
import subprocess

def analyze_high_receipt_cases():
    """Analyze cases with high receipts to understand spending logic"""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print("=== HIGH RECEIPT SPENDING ANALYSIS ===")
    print("Cases with high receipts to understand spending penalty patterns...")
    print("Duration | Miles | Receipts | $/Day | Expected | Current | Error | Expected $/Day")
    print("-" * 85)
    
    high_receipt_cases = []
    for case in cases:
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Focus on cases with high receipts (>$1000)
        if receipts > 1000 and duration >= 4:
            spending_per_day = receipts / duration
            expected_per_day = expected / duration
            
            # Get current result
            result = subprocess.run(['node', 'calculate.js', str(duration), str(miles), str(receipts)], 
                                  capture_output=True, text=True)
            current = float(result.stdout.strip())
            error = abs(current - expected)
            
            high_receipt_cases.append({
                'duration': duration,
                'miles': miles,
                'receipts': receipts,
                'spending_per_day': spending_per_day,
                'expected': expected,
                'current': current,
                'error': error,
                'expected_per_day': expected_per_day
            })
    
    # Sort by error (highest first)
    high_receipt_cases.sort(key=lambda x: x['error'], reverse=True)
    
    for case in high_receipt_cases[:20]:  # Show top 20 error cases
        print(f"{case['duration']:8d} | {case['miles']:5.0f} | {case['receipts']:8.2f} | {case['spending_per_day']:5.0f} | {case['expected']:8.2f} | {case['current']:7.2f} | {case['error']:5.0f} | {case['expected_per_day']:14.2f}")
    
    print(f"\nTotal high-receipt cases analyzed: {len(high_receipt_cases)}")
    avg_error = sum(case['error'] for case in high_receipt_cases) / len(high_receipt_cases)
    print(f"Average error in high-receipt cases: ${avg_error:.2f}")

def analyze_spending_limits():
    """Analyze what spending limits the legacy system actually uses"""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print("\n=== SPENDING LIMIT ANALYSIS ===")
    print("Looking for patterns in spending vs expected reimbursement...")
    
    # Group by duration and analyze spending patterns
    by_duration = {}
    for case in cases:
        duration = case['input']['trip_duration_days']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        if duration not in by_duration:
            by_duration[duration] = []
        
        if receipts > 0:
            spending_per_day = receipts / duration
            expected_per_day = expected / duration
            by_duration[duration].append({
                'spending_per_day': spending_per_day,
                'expected_per_day': expected_per_day,
                'receipts': receipts,
                'expected': expected
            })
    
    for duration in sorted(by_duration.keys()):
        if duration <= 14 and len(by_duration[duration]) > 10:  # Enough data
            cases_for_duration = by_duration[duration]
            
            # Find cases with high spending but still good expected reimbursement
            high_spending_good_reimb = [
                case for case in cases_for_duration 
                if case['spending_per_day'] > 200 and case['expected_per_day'] > 150
            ]
            
            if high_spending_good_reimb:
                print(f"\n{duration}-day trips with high spending but good reimbursement:")
                print("  Spending/Day | Expected/Day | Total Receipts | Total Expected")
                for case in high_spending_good_reimb[:5]:
                    print(f"  ${case['spending_per_day']:10.2f} | ${case['expected_per_day']:11.2f} | ${case['receipts']:13.2f} | ${case['expected']:13.2f}")

if __name__ == "__main__":
    analyze_high_receipt_cases()
    analyze_spending_limits() 