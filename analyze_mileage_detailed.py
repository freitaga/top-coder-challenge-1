#!/usr/bin/env python3
import json
import subprocess

def test_current_mileage_accuracy():
    """Test our current mileage calculation against expected results"""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print("=== CURRENT MILEAGE CALCULATION ACCURACY ===")
    print("Testing cases with minimal variables to isolate mileage performance...")
    print("Miles | Duration | Receipts | Expected | Current | Mileage Error | Rate Expected | Rate Current")
    print("-" * 100)
    
    # Focus on 1-day cases with low receipts to minimize other variables
    mileage_test_cases = []
    for case in cases:
        if (case['input']['trip_duration_days'] == 1 and 
            case['input']['total_receipts_amount'] < 30 and
            case['input']['miles_traveled'] > 0):
            mileage_test_cases.append(case)
    
    # Sort by mileage for easier analysis
    mileage_test_cases.sort(key=lambda x: x['input']['miles_traveled'])
    
    total_error = 0
    for case in mileage_test_cases[:20]:  # Test first 20 cases
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Get current result
        result = subprocess.run(['node', 'calculate.js', str(duration), str(miles), str(receipts)], 
                              capture_output=True, text=True)
        current = float(result.stdout.strip())
        
        # Calculate error
        error = abs(current - expected)
        total_error += error
        
        # Calculate implied rates
        rate_expected = expected / miles if miles > 0 else 0
        rate_current = current / miles if miles > 0 else 0
        
        print(f"{miles:5.0f} | {duration:8d} | {receipts:8.2f} | {expected:8.2f} | {current:7.2f} | {error:13.2f} | {rate_expected:13.2f} | {rate_current:12.2f}")
    
    avg_error = total_error / len(mileage_test_cases[:20])
    print(f"\nAverage error in mileage-focused cases: ${avg_error:.2f}")

def analyze_mileage_breakpoints():
    """Analyze specific mileage breakpoints to understand tier structure"""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    print("\n=== MILEAGE BREAKPOINT ANALYSIS ===")
    print("Looking for evidence of tiered rates at 100, 300, 600 mile breakpoints...")
    
    # Define breakpoint ranges to examine
    breakpoints = [
        (95, 105, "100-mile"),
        (295, 305, "300-mile"), 
        (595, 605, "600-mile")
    ]
    
    for min_miles, max_miles, label in breakpoints:
        print(f"\n{label} breakpoint analysis:")
        print("Miles | Duration | Receipts | Expected | $/Mile")
        print("-" * 50)
        
        breakpoint_cases = []
        for case in cases:
            miles = case['input']['miles_traveled']
            duration = case['input']['trip_duration_days']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            if (min_miles <= miles <= max_miles and 
                duration <= 3 and receipts < 100):  # Minimal variables
                per_mile = expected / miles
                breakpoint_cases.append({
                    'miles': miles,
                    'duration': duration, 
                    'receipts': receipts,
                    'expected': expected,
                    'per_mile': per_mile
                })
        
        # Sort by miles and show results
        breakpoint_cases.sort(key=lambda x: x['miles'])
        for case in breakpoint_cases[:10]:
            print(f"{case['miles']:5.0f} | {case['duration']:8d} | {case['receipts']:8.2f} | {case['expected']:8.2f} | {case['per_mile']:6.2f}")

def analyze_current_vs_optimal_rates():
    """Compare our current tiered rates with what the data suggests"""
    print("\n=== CURRENT VS OPTIMAL RATE ANALYSIS ===")
    
    # Our current rates
    current_rates = [
        (0, 100, 0.62),
        (100, 300, 0.52),
        (300, 600, 0.42),
        (600, float('inf'), 0.32)
    ]
    
    # Data-driven optimal rates (from the analysis above)
    suggested_rates = [
        (0, 50, 12.8),      # Very low mileage gets high rate
        (50, 100, 7.6),     # Low mileage
        (100, 200, 4.4),    # Medium-low mileage  
        (200, 300, 3.5),    # Medium mileage
        (300, 600, 2.5),    # Medium-high mileage
        (600, 1000, 1.8),   # High mileage
        (1000, float('inf'), 1.5)  # Very high mileage
    ]
    
    print("Current Tier Structure:")
    for min_m, max_m, rate in current_rates:
        if max_m == float('inf'):
            print(f"  {min_m}+ miles: ${rate:.2f}/mile")
        else:
            print(f"  {min_m}-{max_m} miles: ${rate:.2f}/mile")
    
    print("\nData-Suggested Tier Structure:")
    for min_m, max_m, rate in suggested_rates:
        if max_m == float('inf'):
            print(f"  {min_m}+ miles: ${rate:.2f}/mile")
        else:
            print(f"  {min_m}-{max_m} miles: ${rate:.2f}/mile")
    
    print("\nKey Observations:")
    print("1. Current rates are MUCH lower than data suggests")
    print("2. Data shows much steeper decline for low mileage")
    print("3. Need more granular tiers, especially for 0-300 mile range")

if __name__ == "__main__":
    test_current_mileage_accuracy()
    analyze_mileage_breakpoints()
    analyze_current_vs_optimal_rates() 