#!/usr/bin/env python3
import json
import subprocess
import statistics
from collections import defaultdict

def load_test_cases():
    with open('public_cases.json', 'r') as f:
        return json.load(f)

def analyze_error_patterns():
    """Identify patterns in our highest error cases"""
    cases = load_test_cases()
    
    print("=== ERROR PATTERN ANALYSIS ===")
    print("Analyzing our worst performing cases to find systematic issues...\n")
    
    results = []
    for i, case in enumerate(cases):
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Get current result
        result = subprocess.run(['node', 'calculate.js', str(duration), str(miles), str(receipts)], 
                              capture_output=True, text=True)
        current = float(result.stdout.strip())
        error = abs(current - expected)
        
        results.append({
            'case_id': i,
            'duration': duration,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'current': current,
            'error': error,
            'miles_per_day': miles / duration,
            'spending_per_day': receipts / duration,
            'expected_per_day': expected / duration,
            'current_per_day': current / duration,
            'over_under': 'OVER' if current > expected else 'UNDER'
        })
    
    # Sort by error magnitude
    results.sort(key=lambda x: x['error'], reverse=True)
    
    # Analyze top 20 worst cases
    print("TOP 20 HIGHEST ERROR CASES:")
    print("Case | Duration | Miles | $/Day | Expected | Current | Error | Miles/Day | Type")
    print("-" * 85)
    
    for case in results[:20]:
        print(f"{case['case_id']:4d} | {case['duration']:8d} | {case['miles']:5.0f} | {case['spending_per_day']:5.0f} | {case['expected']:8.2f} | {case['current']:7.2f} | {case['error']:5.0f} | {case['miles_per_day']:9.1f} | {case['over_under']}")
    
    return results

def analyze_systematic_bias(results):
    """Look for systematic patterns in over/under reimbursement"""
    print("\n=== SYSTEMATIC BIAS ANALYSIS ===")
    
    # Group by characteristics
    by_duration = defaultdict(list)
    by_receipt_level = defaultdict(list)
    by_efficiency = defaultdict(list)
    
    for case in results:
        # Group by duration
        by_duration[case['duration']].append(case)
        
        # Group by receipt level
        if case['receipts'] == 0:
            by_receipt_level['None'].append(case)
        elif case['receipts'] < 100:
            by_receipt_level['Low'].append(case)
        elif case['receipts'] < 500:
            by_receipt_level['Medium'].append(case)
        elif case['receipts'] < 1500:
            by_receipt_level['High'].append(case)
        else:
            by_receipt_level['Very High'].append(case)
        
        # Group by efficiency
        if case['miles_per_day'] < 50:
            by_efficiency['Low'].append(case)
        elif case['miles_per_day'] < 150:
            by_efficiency['Medium'].append(case)
        else:
            by_efficiency['High'].append(case)
    
    # Analyze bias by duration
    print("BIAS BY DURATION:")
    print("Duration | Count | Avg Error | % Over | % Under | Avg Expected | Avg Current")
    print("-" * 75)
    
    for duration in sorted(by_duration.keys()):
        cases = by_duration[duration]
        if len(cases) > 5:  # Only analyze with sufficient data
            avg_error = statistics.mean([c['error'] for c in cases])
            pct_over = len([c for c in cases if c['over_under'] == 'OVER']) / len(cases) * 100
            pct_under = 100 - pct_over
            avg_expected = statistics.mean([c['expected'] for c in cases])
            avg_current = statistics.mean([c['current'] for c in cases])
            
            print(f"{duration:8d} | {len(cases):5d} | {avg_error:9.2f} | {pct_over:6.1f}% | {pct_under:7.1f}% | {avg_expected:12.2f} | {avg_current:11.2f}")
    
    # Analyze bias by receipt level
    print("\nBIAS BY RECEIPT LEVEL:")
    print("Level      | Count | Avg Error | % Over | % Under | Avg Expected | Avg Current")
    print("-" * 75)
    
    for level in ['None', 'Low', 'Medium', 'High', 'Very High']:
        cases = by_receipt_level[level]
        if len(cases) > 5:
            avg_error = statistics.mean([c['error'] for c in cases])
            pct_over = len([c for c in cases if c['over_under'] == 'OVER']) / len(cases) * 100
            pct_under = 100 - pct_over
            avg_expected = statistics.mean([c['expected'] for c in cases])
            avg_current = statistics.mean([c['current'] for c in cases])
            
            print(f"{level:10s} | {len(cases):5d} | {avg_error:9.2f} | {pct_over:6.1f}% | {pct_under:7.1f}% | {avg_expected:12.2f} | {avg_current:11.2f}")

def analyze_spending_penalty_issues(results):
    """Analyze cases where spending penalties seem incorrect"""
    print("\n=== SPENDING PENALTY ANALYSIS ===")
    
    # Look for cases with high receipts but very different expected outcomes
    high_receipt_cases = [case for case in results if case['receipts'] > 1000]
    
    # Group by expected per-day rates despite high receipts
    low_expected = [case for case in high_receipt_cases if case['expected_per_day'] < 150]
    high_expected = [case for case in high_receipt_cases if case['expected_per_day'] > 250]
    
    print(f"High receipt cases (>$1000): {len(high_receipt_cases)}")
    print(f"  - Low expected per day (<$150): {len(low_expected)}")
    print(f"  - High expected per day (>$250): {len(high_expected)}")
    
    print("\nLOW EXPECTED CASES (should get heavy penalties):")
    print("Case | Duration | Miles | Receipts | $/Day | Expected | Current | Miles/Day | Spending/Day")
    print("-" * 90)
    
    for case in sorted(low_expected, key=lambda x: x['error'], reverse=True)[:10]:
        print(f"{case['case_id']:4d} | {case['duration']:8d} | {case['miles']:5.0f} | {case['receipts']:8.2f} | {case['spending_per_day']:5.0f} | {case['expected']:8.2f} | {case['current']:7.2f} | {case['miles_per_day']:9.1f} | {case['spending_per_day']:12.1f}")
    
    print("\nHIGH EXPECTED CASES (should get good reimbursement despite high receipts):")
    print("Case | Duration | Miles | Receipts | $/Day | Expected | Current | Miles/Day | Spending/Day")
    print("-" * 90)
    
    for case in sorted(high_expected, key=lambda x: x['error'], reverse=True)[:10]:
        print(f"{case['case_id']:4d} | {case['duration']:8d} | {case['miles']:5.0f} | {case['receipts']:8.2f} | {case['spending_per_day']:5.0f} | {case['expected']:8.2f} | {case['current']:7.2f} | {case['miles_per_day']:9.1f} | {case['spending_per_day']:12.1f}")

def identify_improvement_opportunities(results):
    """Identify the highest-impact improvement opportunities"""
    print("\n=== IMPROVEMENT OPPORTUNITIES ===")
    
    # Calculate potential score improvement by fixing different categories
    total_error = sum([case['error'] for case in results])
    
    # Categories of cases that could be improved
    over_cases = [case for case in results if case['over_under'] == 'OVER']
    under_cases = [case for case in results if case['over_under'] == 'UNDER']
    
    high_error_cases = [case for case in results if case['error'] > 500]
    
    print(f"Current total error: ${total_error:.2f}")
    print(f"Average error per case: ${total_error/len(results):.2f}")
    print()
    
    print("ERROR DISTRIBUTION:")
    print(f"  Over-reimbursing: {len(over_cases)} cases, total error: ${sum([c['error'] for c in over_cases]):.2f}")
    print(f"  Under-reimbursing: {len(under_cases)} cases, total error: ${sum([c['error'] for c in under_cases]):.2f}")
    print(f"  High error (>$500): {len(high_error_cases)} cases, total error: ${sum([c['error'] for c in high_error_cases]):.2f}")
    
    # Most common characteristics of high-error cases
    print(f"\nHIGH ERROR CASE PATTERNS:")
    duration_counts = defaultdict(int)
    receipt_patterns = defaultdict(int)
    
    for case in high_error_cases:
        duration_counts[case['duration']] += 1
        
        if case['receipts'] > 1500:
            receipt_patterns['Very High Receipts'] += 1
        elif case['receipts'] > 500:
            receipt_patterns['High Receipts'] += 1
        else:
            receipt_patterns['Low/Medium Receipts'] += 1
    
    print("  Most problematic durations:")
    for duration, count in sorted(duration_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    {duration} days: {count} cases")
    
    print("  Most problematic receipt patterns:")
    for pattern, count in sorted(receipt_patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"    {pattern}: {count} cases")

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE SOLUTION ANALYSIS")
    print("="*50)
    
    results = analyze_error_patterns()
    analyze_systematic_bias(results)
    analyze_spending_penalty_issues(results)
    identify_improvement_opportunities(results) 