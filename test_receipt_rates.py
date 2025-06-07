#!/usr/bin/env python3
import json
import subprocess

def test_specific_cases():
    """Test our current performance on specific problematic cases"""
    test_cases = [
        # High-receipt cases that should get good reimbursement
        (4, 764, 1417.94, 1682.10),
        (5, 789, 1853.31, 1792.88),
        (6, 372, 2494.69, 1742.34),
        # Medium receipt cases  
        (3, 154, 274.04, 406.91),
        (1, 181, 128.05, 225.12),
        # Tiny receipt cases
        (1, 181, 3.60, 126.06),
        (1, 47, 17.97, 128.91),
    ]
    
    print("=== CURRENT PERFORMANCE ON KEY CASES ===")
    print("Duration | Miles | Receipts | Expected | Current | Error | Type")
    print("-" * 70)
    
    for duration, miles, receipts, expected in test_cases:
        result = subprocess.run(['node', 'calculate.js', str(duration), str(miles), str(receipts)], 
                              capture_output=True, text=True)
        current = float(result.stdout.strip())
        error = abs(current - expected)
        
        if receipts < 30:
            case_type = "Tiny"
        elif receipts < 500:
            case_type = "Medium"
        else:
            case_type = "High"
            
        print(f"{duration:8d} | {miles:5.0f} | {receipts:8.2f} | {expected:8.2f} | {current:7.2f} | {error:5.0f} | {case_type}")

if __name__ == "__main__":
    test_specific_cases() 