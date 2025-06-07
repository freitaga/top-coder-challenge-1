#!/usr/bin/env python3
import json
import subprocess

def test_improvements():
    # Load test cases
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    # Test first 50 cases
    test_cases = cases[:50]
    
    total_error = 0
    for i, case in enumerate(test_cases):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Run our solution
        try:
            result = subprocess.run(['node', 'calculate.js', str(duration), str(miles), str(receipts)], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                print(f"Error in case {i}: {result.stderr}")
                continue
                
            actual = float(result.stdout.strip())
            error = abs(actual - expected)
            total_error += error
            
            if i < 10:  # Show first 10 cases
                print(f"Case {i}: D={duration}, M={miles}, R={receipts:.2f}")
                print(f"  Expected: {expected:.2f}, Actual: {actual:.2f}, Error: {error:.2f}")
                
        except Exception as e:
            print(f"Exception in case {i}: {e}")
    
    avg_error = total_error / len(test_cases)
    print(f"\nAverage error over {len(test_cases)} cases: {avg_error:.2f}")
    
    # Test a few 1-day cases specifically
    print("\n=== 1-DAY CASES ANALYSIS ===")
    one_day_cases = [case for case in cases if case['input']['trip_duration_days'] == 1][:10]
    
    one_day_error = 0
    for case in one_day_cases:
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        result = subprocess.run(['node', 'calculate.js', str(duration), str(miles), str(receipts)], 
                              capture_output=True, text=True)
        actual = float(result.stdout.strip())
        error = abs(actual - expected)
        one_day_error += error
        
        print(f"1-day: M={miles}, R={receipts:.2f} -> Expected: {expected:.2f}, Actual: {actual:.2f}, Error: {error:.2f}")
    
    print(f"Average 1-day error: {one_day_error / len(one_day_cases):.2f}")

if __name__ == "__main__":
    test_improvements() 