function calculateReimbursement(trip_duration_days, miles_traveled, total_receipts_amount) {
    const D = trip_duration_days;
    const M = miles_traveled;
    const R = total_receipts_amount;
    
    // Constants from the high-performing approach (with targeted adjustments)
    const RECEIPT_CAP_UPPER = 1153.77;
    const RECEIPT_CAP_LOWER = 359.88;
    const MILEAGE_RATE = 0.426;
    const PER_DIEM_BASE = 73.58;
    const SECOND_WEEK_PENALTY_PER_DAY = 45.0;  // Reduced from 49.62 to be less harsh
    const ROUNDOFF_PENALTY_RATE = 1.11;
    const GLOBAL_OFFSET = 208.0;  // Balanced between 200 and 215.68
    const ROUNDOFF_OFFSET = -323.55;
    
    // ==========================================
    // FORMULA-BASED CALCULATION
    // ==========================================
    
    // 1. Per Diem Calculation
    let per_diem = PER_DIEM_BASE * D;
    
    // 2. Second week penalty (after day 7)
    let per_diem_penalty = SECOND_WEEK_PENALTY_PER_DAY * Math.max(0, D - 7);
    let per_diem_penalized = per_diem - per_diem_penalty;
    
    // 3. Mileage allowance (linear rate)
    let mileage_allowance = MILEAGE_RATE * M;
    
    // 4. Receipt reimbursement (capped, with adjustment for long trips)
    let receipt_cap_upper = RECEIPT_CAP_UPPER;
    let receipt_cap_lower = RECEIPT_CAP_LOWER;
    
    // Hypothesis: Long trips with low-to-medium mileage need higher receipt caps for business expenses
    // Analysis shows different mileage thresholds needed for different trip lengths
    if (D >= 10 && M < 300) {  // Very long trips with very low mileage need extra help
        receipt_cap_upper = 1600;  // Higher cap for conference-style very long trips
    } else if (D >= 10 && M < 600) {  // Very long trips get higher threshold for medium-high mileage
        receipt_cap_upper = 1400;  
    } else if (D >= 8 && M < 500) {  // Regular long trips with low-medium mileage
        receipt_cap_upper = 1400;  
    }
    
    let capped_receipts = Math.max(receipt_cap_lower, Math.min(R, receipt_cap_upper));
    
    // 5. Rounding penalty logic
    let roundoff_penalty = 0;
    const cents = parseFloat((R % 1).toFixed(2));
    if (cents === 0.49 || cents === 0.99) {
        roundoff_penalty = ROUNDOFF_PENALTY_RATE * capped_receipts + ROUNDOFF_OFFSET;
    }
    
    // 6. Base calculation
    let reimbursement = per_diem_penalized + mileage_allowance + capped_receipts - roundoff_penalty - GLOBAL_OFFSET;
    
    // ==========================================
    // CONTEXT-AWARE ADJUSTMENTS (Keep our best insights)
    // ==========================================
    
    const miles_per_day = M / D;
    const spending_per_day = R / D;
    
    // Kevin's efficiency bonus for the "sweet spot" (180-220 miles/day)
    if (miles_per_day >= 180 && miles_per_day <= 220) {
        reimbursement += 40;  // Reduced from 75 to be more conservative
    }
    
    // Vacation penalty for extreme cases (refined from our analysis)
    if (D >= 8 && miles_per_day < 50 && spending_per_day > 200) {
        reimbursement *= 0.65;  // Heavy vacation penalty
    }
    
    // High-effort bonus for exceptional cases
    if (D >= 4 && D <= 6 && miles_per_day > 200 && spending_per_day > 300 && spending_per_day < 440) {
        reimbursement *= 1.15;  // Moderate bonus for high-effort
    }
    
    // 5-day sweet spot bonus (confirmed in interviews)
    if (D === 5 && miles_per_day > 100 && spending_per_day < 350) {
        // Prevent over-reimbursement for very high mileage 5-day trips
        if (miles_per_day > 200) {
            reimbursement += 25;  // Reduced bonus for high-mileage 5-day trips
        } else {
            reimbursement += 50;  // Lisa's 5-day bonus for regular cases
        }
    }
    
    // ==========================================
    // FINAL VALIDATION
    // ==========================================
    if (reimbursement < 0) {
        reimbursement = 0;
    }
    
    return reimbursement.toFixed(2);
}

// ==========================================
// COMMAND LINE INTERFACE
// ==========================================
const args = process.argv.slice(2);
const trip_duration_days = parseInt(args[0], 10);
const miles_traveled = parseInt(args[1], 10);
const total_receipts_amount = parseFloat(args[2]);

const result = calculateReimbursement(trip_duration_days, miles_traveled, total_receipts_amount);
console.log(result); 