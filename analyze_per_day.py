#!/usr/bin/env python3
import json
import statistics
from collections import defaultdict

def load_test_cases():
    with open('public_cases.json', 'r') as f:
        return json.load(f)

def analyze_per_day_patterns():
    cases = load_test_cases()
    
    # Group cases by trip duration
    by_duration = defaultdict(list)
    for case in cases:
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        by_duration[duration].append({
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'per_day': expected / duration
        })
    
    print("=== PER DAY ANALYSIS ===")
    print("Duration | Count | Avg Per Day | Min Per Day | Max Per Day | Std Dev")
    print("-" * 70)
    
    duration_stats = {}
    for duration in sorted(by_duration.keys()):
        cases_for_duration = by_duration[duration]
        per_day_values = [case['per_day'] for case in cases_for_duration]
        
        avg_per_day = statistics.mean(per_day_values)
        min_per_day = min(per_day_values)
        max_per_day = max(per_day_values)
        std_dev = statistics.stdev(per_day_values) if len(per_day_values) > 1 else 0
        
        duration_stats[duration] = {
            'avg': avg_per_day,
            'min': min_per_day,
            'max': max_per_day,
            'std_dev': std_dev,
            'count': len(cases_for_duration)
        }
        
        print(f"{duration:8d} | {len(cases_for_duration):5d} | {avg_per_day:11.2f} | {min_per_day:11.2f} | {max_per_day:11.2f} | {std_dev:7.2f}")
    
    print("\n=== PATTERN ANALYSIS ===")
    
    # Look for the 5-day bonus pattern
    print("\n5-day cases analysis:")
    five_day_cases = by_duration[5]
    five_day_per_day = [case['per_day'] for case in five_day_cases]
    print(f"5-day average per day: {statistics.mean(five_day_per_day):.2f}")
    
    # Compare short vs medium vs long trips
    short_trips = []  # 1-3 days
    medium_trips = []  # 4-6 days
    long_trips = []   # 7+ days
    
    for duration, stats in duration_stats.items():
        if duration <= 3:
            short_trips.extend([stats['avg']] * stats['count'])
        elif duration <= 6:
            medium_trips.extend([stats['avg']] * stats['count'])
        else:
            long_trips.extend([stats['avg']] * stats['count'])
    
    print(f"\nTrip length comparison:")
    print(f"Short trips (1-3 days): avg {statistics.mean([duration_stats[d]['avg'] for d in range(1, 4) if d in duration_stats]):.2f}")
    print(f"Medium trips (4-6 days): avg {statistics.mean([duration_stats[d]['avg'] for d in range(4, 7) if d in duration_stats]):.2f}")
    print(f"Long trips (7+ days): avg {statistics.mean([duration_stats[d]['avg'] for d in range(7, 15) if d in duration_stats]):.2f}")
    
    # Analyze cases with minimal variables (low miles, low receipts)
    print("\n=== MINIMAL VARIABLE ANALYSIS ===")
    print("Looking at cases with low miles (<100) and low receipts (<100) to isolate per diem:")
    
    minimal_cases = defaultdict(list)
    for case in cases:
        if case['input']['miles_traveled'] < 100 and case['input']['total_receipts_amount'] < 100:
            duration = case['input']['trip_duration_days']
            minimal_cases[duration].append(case['expected_output'] / duration)
    
    for duration in sorted(minimal_cases.keys()):
        if minimal_cases[duration]:
            avg_minimal = statistics.mean(minimal_cases[duration])
            print(f"Duration {duration}: {len(minimal_cases[duration])} cases, avg per day: {avg_minimal:.2f}")

if __name__ == "__main__":
    analyze_per_day_patterns() 