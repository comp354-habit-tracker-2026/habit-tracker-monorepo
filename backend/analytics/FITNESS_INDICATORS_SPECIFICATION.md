# Fitness Indicators Specification
## Group 13 - Formal Mathematical Definitions

**Document Status:** Ready for Implementation Handoff
**Version:** 1.0
**Date:** April 6, 2026
**Reviewers:** Group 13

---

## Executive Summary

This document formally defines two key fitness indicators used to analyze and track user workout behavior: the **Volume Indicator** and the **Consistency Indicator**. Both indicators are designed to be computed from historical workout data and provide actionable insights into user fitness patterns.

---

## 1. VOLUME INDICATOR

### 1.1 Mathematical Definition

The Volume Indicator (V) is defined as the normalized sum of workout sessions weighted by their intensity and duration over a specified time period.

#### Formula:

$$V = \sum_{i=1}^{n} (D_i \cdot I_i \cdot (1 + 0.1 \times T_i))$$

Where:
- **V** = Volume score for the period [0 to ∞)
- **n** = Total number of workout sessions in the period
- **D_i** = Duration of session i in minutes
- **I_i** = Intensity factor of session i (0.5 to 2.0 scale)
  - 0.5 = Light intensity
  - 1.0 = Moderate intensity
  - 1.5 = High intensity
  - 2.0 = Maximum intensity
- **T_i** = Type coefficient of session i
  - Cardio: 1.0
  - Strength: 1.5
  - Flexibility: 0.5
  - Sports: 1.2
  - Mixed: 0.8

### 1.2 Variable Explanations

| Variable | Type | Range | Definition |
|----------|------|-------|-----------|
| V | Output | [0, ∞) | Cumulative volume score; higher values indicate greater total workout output |
| n | Integer | [0, ∞) | Number of distinct workout sessions recorded in the period |
| D_i | Float | [0, 600] | Session duration in minutes (practical limit: 10 minutes to 10 hours) |
| I_i | Float | [0.5, 2.0] | Perceived or measured intensity; scale factor for workout difficulty |
| T_i | Float | [0.5, 1.5] | Workout type multiplier; adjusts volume based on exercise category |

### 1.3 Interpretation

- **V < 100**: Minimal workout volume (light activity level)
- **100 ≤ V < 300**: Low to moderate workout volume
- **300 ≤ V < 600**: Moderate to high workout volume
- **V ≥ 600**: High workout volume (intense/frequent training)

### 1.4 Worked Examples

#### Example 1: Weekly Volume Calculation (Gym Training)

**Period:** Week of April 1-7, 2026

**Workout Data:**

| Date | Duration | Intensity | Type | Calculation |
|------|----------|-----------|------|-------------|
| Mon | 45 min | 1.5 (High) | Strength | 45 × 1.5 × (1 + 0.1×1.5) = 45 × 1.5 × 1.15 = 77.625 |
| Wed | 30 min | 1.0 (Moderate) | Cardio | 30 × 1.0 × (1 + 0.1×1.0) = 30 × 1.0 × 1.10 = 33.000 |
| Fri | 50 min | 1.5 (High) | Strength | 50 × 1.5 × (1 + 0.1×1.5) = 50 × 1.5 × 1.15 = 86.250 |
| Sat | 20 min | 0.5 (Light) | Flexibility | 20 × 0.5 × (1 + 0.1×0.5) = 20 × 0.5 × 1.05 = 10.500 |

**Calculation:**
$$V = 77.625 + 33.000 + 86.250 + 10.500 = 207.375$$

**Result:** V ≈ 207.4
**Interpretation:** This user achieved moderate workout volume for the week.

---

#### Example 2: Weekly Volume Calculation (Mixed Training)

**Period:** Week of April 8-14, 2026

**Workout Data:**

| Date | Duration | Intensity | Type | Calculation |
|------|----------|-----------|------|-------------|
| Mon | 60 min | 1.5 (High) | Mixed | 60 × 1.5 × (1 + 0.1×0.8) = 60 × 1.5 × 1.08 = 97.200 |
| Tue | 40 min | 1.0 (Moderate) | Cardio | 40 × 1.0 × (1 + 0.1×1.0) = 40 × 1.0 × 1.10 = 44.000 |
| Wed | 45 min | 1.2 (High) | Sports | 45 × 1.2 × (1 + 0.1×1.2) = 45 × 1.2 × 1.12 = 60.480 |
| Fri | 55 min | 1.5 (High) | Strength | 55 × 1.5 × (1 + 0.1×1.5) = 55 × 1.5 × 1.15 = 94.875 |
| Sat | 30 min | 1.0 (Moderate) | Cardio | 30 × 1.0 × (1 + 0.1×1.0) = 30 × 1.0 × 1.10 = 33.000 |
| Sun | 25 min | 0.5 (Light) | Flexibility | 25 × 0.5 × (1 + 0.1×0.5) = 25 × 0.5 × 1.05 = 13.125 |

**Calculation:**
$$V = 97.200 + 44.000 + 60.480 + 94.875 + 33.000 + 13.125 = 342.680$$

**Result:** V ≈ 342.7
**Interpretation:** This user achieved higher workout volume with more frequent and consistent sessions.

---

## 2. CONSISTENCY INDICATOR

### 2.1 Mathematical Definition

The Consistency Indicator (C) is defined as the adherence ratio adjusted for variance from the user's target workout frequency. It measures both the frequency of workouts and their uniformity across the period.

#### Formula:

$$C = \frac{n}{T} \times \left(1 - \frac{\sigma_d}{D_{avg}}\right) \times 100$$

Where:
- **C** = Consistency score [0 to 100] (percentage)
- **n** = Actual number of workouts completed in the period
- **T** = Target number of workouts for the period (user-defined or default)
- **σ_d** = Standard deviation of inter-workout intervals (days between sessions)
- **D_avg** = Mean inter-workout interval
- The variance penalty prevents the user from gaming the system by front-loading all workouts

### 2.2 Additional Definition (Alternative: Streak-Based)

For reference, an alternative **consecutive consistency** measure:

$$C_{streak} = \frac{\text{Current Streak Days}}{\text{Target Streak Days}} \times 100$$

Primary definition uses the frequency-variance model (Section 2.1) as it's more robust for varied training schedules.

### 2.3 Variable Explanations

| Variable | Type | Range | Definition |
|----------|------|-------|-----------|
| C | Output | [0, 100] | Consistency percentage; 100 = perfect adherence to plan |
| n | Integer | [0, ∞) | Actual workouts completed in the period |
| T | Integer | [1, ∞) | User's target number of workouts for the period |
| σ_d | Float | [0, ∞) | Standard deviation of days between consecutive workouts |
| D_avg | Float | [0, ∞) | Average days between workouts; lower = more frequent |

### 2.4 Special Cases

- **If σ_d > D_avg**: Variance penalty term becomes > 1, which would make C negative → clamp C to minimum of 0
- **If n > T**: Frequency ratio exceeds 1 → cap at 1.5× (bonus for exceeding targets by 50%)
- **If D_avg = 0** (multiple workouts per day): Treat as D_avg = 0.5 (daily micro-sessions)

### 2.5 Interpretation

| Score | Assessment | Description |
|-------|-----------|-------------|
| 90-100 | Excellent | Near-perfect adherence; highly predictable schedule |
| 75-89 | Good | Strong consistency with minor irregularities |
| 60-74 | Fair | Adequate consistency; some variance in schedule |
| 40-59 | Weak | Inconsistent pattern; significant gaps |
| 0-39 | Poor | Very inconsistent; minimal adherence to plan |

### 2.6 Worked Examples

#### Example 1: Consistent Training Schedule

**Period:** 4-week training block (28 days)
**Target:** 4 workouts per week = 16 total workouts

**Workout Dates (actual days when workouts occurred):**
- Week 1: Mon (day 1), Wed (day 3), Fri (day 5), Sat (day 6)
- Week 2: Mon (day 8), Wed (day 10), Fri (day 12), Sat (day 13)
- Week 3: Mon (day 15), Wed (day 17), Fri (day 19), Sat (day 20)
- Week 4: Mon (day 22), Wed (day 24), Fri (day 26), Sat (day 27)

**Inter-workout Intervals (days between sessions):**
- Day 1 to 3: 2 days
- Day 3 to 5: 2 days
- Day 5 to 6: 1 day
- Day 6 to 8: 2 days
- Day 8 to 10: 2 days
- ... (pattern repeats)

**Intervals: [2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2]**

**Calculations:**

$$D_{avg} = \frac{2+2+1+2+2+2+1+2+2+2+1+2+2+2+1+2}{16} = \frac{28}{16} = 1.75 \text{ days}$$

$$\sigma_d = \sqrt{\frac{\sum(d_i - 1.75)^2}{16}} = 0.433 \text{ days}$$

$$C = \frac{16}{16} \times \left(1 - \frac{0.433}{1.75}\right) \times 100 = 1.0 \times (1 - 0.247) \times 100 = 75.3\%$$

**Result:** C ≈ 75.3%
**Interpretation:** Good consistency. User hit their target and maintained a predictable schedule with only minor variance (about 1-2 day shifts between sessions).

---

#### Example 2: Inconsistent Training Schedule

**Period:** 4-week training block (28 days)
**Target:** 4 workouts per week = 16 total workouts
**Actual Workouts Completed:** 13

**Workout Dates (actual):**
- Week 1: Mon (day 1), Fri (day 5) [skipped Wed and Sat]
- Week 2: Mon (day 8), Wed (day 10), Fri (day 12) [skipped Sat]
- Week 3: Sat (day 20) [long gap from previous, only 1 workout]
- Week 4: Wed (day 24), Fri (day 26), Sat (day 27), Mon (day 29) [went into week 5]

**Inter-workout Intervals:**
- 1→5: 4 days
- 5→8: 3 days
- 8→10: 2 days
- 10→12: 2 days
- 12→20: 8 days (large gap)
- 20→24: 4 days
- 24→26: 2 days
- 26→27: 1 day
- 27→29: 2 days

**Intervals: [4, 3, 2, 2, 8, 4, 2, 1, 2]** (9 intervals for 13 workouts)

**Calculations:**

$$n = 13 \text{ (missed 3 workouts)}$$

$$D_{avg} = \frac{4+3+2+2+8+4+2+1+2}{9} = \frac{28}{9} = 3.11 \text{ days}$$

$$\sigma_d = \sqrt{\frac{(4-3.11)^2 + (3-3.11)^2 + ... + (2-3.11)^2}{9}} = 2.44 \text{ days}$$

$$C = \frac{13}{16} \times \left(1 - \frac{2.44}{3.11}\right) \times 100 = 0.8125 \times (1 - 0.784) \times 100 = 17.4\%$$

**Result:** C ≈ 17.4%
**Interpretation:** Poor consistency. User completed only 81% of target workouts AND exhibited high variance in scheduling (especially the 8-day gap). The combination of missed workouts and unpredictable timing results in a low consistency score.

---

## 3. FULLY DRESSED USE CASE

### 3.1 Scenario: 8-Week Fitness Progress Tracking

**User Profile:**
- Name: Sarah
- Goal: Improve fitness consistency and increase weekly volume
- Target: 4 workouts/week, progressive volume increase
- Start Date: January 1, 2026

### 3.2 Week-by-Week Analysis

| Week | Volume (V) | Target | Consistency (C) | Notes |
|------|-----------|--------|-----------------|-------|
| 1 | 156.2 | 200 | 58% | Started weak, needs ramp-up |
| 2 | 218.4 | 220 | 72% | Improved but still below target |
| 3 | 289.5 | 240 | 85% | Strong week, found rhythm |
| 4 | 312.1 | 260 | 81% | Very consistent scheduling |
| 5 | 334.7 | 280 | 88% | Excellent; hit all 5 extra sessions |
| 6 | 298.3 | 300 | 76% | Slight dip; affected by travel |
| 7 | 356.2 | 320 | 92% | Best week; peak performance |
| 8 | 341.5 | 340 | 89% | Maintained high level; tapering |

### 3.3 Insights Generated

**Week 1-4 Trend:**
- Volume increased 100% (156.2 → 312.1)
- Consistency improved 23 percentage points (58% → 81%)
- **Recommendation:** User is successfully building routine; encourage continuation

**Week 5-6 Reversal:**
- Volume spike then dip (334.7 → 298.3)
- Consistency dips to 76% (travel detected)
- **Recommendation:** Expect recovery week; provide flexible micro-session options

**Week 7-8 Stabilization:**
- Volume stabilized at 340-356 (near target)
- Consistency sustained above 89%
- **Recommendation:** User ready for increased challenge; suggest progressive overload

### 3.4 API Usage

```json
{
  "user_id": "sarah_001",
  "period": "week",
  "date_range": {
    "start": "2026-01-01",
    "end": "2026-02-28"
  },
  "metrics": {
    "volume": {
      "current": 341.5,
      "target": 340,
      "trend": "stable",
      "week_over_week_change": "+1.4%"
    },
    "consistency": {
      "current": 89,
      "target": 85,
      "trend": "improving",
      "week_over_week_change": "+3%"
    }
  },
  "recommendations": [
    "Maintain current schedule",
    "Consider progressive overload in volume",
    "You're exceeding consistency targets"
  ]
}
```

---

## 4. IMPLEMENTATION SPECIFICATIONS

### 4.1 Data Requirements

Each workout entry must include:
- `user_id` (string, UUID)
- `date` (datetime)
- `duration_minutes` (integer, 10-600)
- `intensity` (float, 0.5-2.0)
- `workout_type` (enum: cardio, strength, flexibility, sports, mixed)
- `notes` (optional string)

### 4.2 Calculation Windows

- **Daily:** Last 24 hours
- **Weekly:** Last 7 days (Monday-Sunday)
- **Monthly:** Last 30 calendar days
- **Custom:** Any user-specified range

### 4.3 Storage

Indicators should be pre-calculated and cached with:
- Calculation timestamp
- Period start/end
- Raw values (V, C, intermediate values)
- Confidence level (based on data completeness)

### 4.4 Performance Requirements

- Calculation time: < 500ms for 6-month history
- Database queries: ≤ 3 for indicator calculation
- Cache expiration: 6 hours or manual refresh

---

## 5. QUALITY ASSURANCE

### 5.1 Edge Cases Handled

- ✅ Zero workouts in period (V=0, C=0)
- ✅ Single workout (σ_d undefined, treat as C = 50 + 0.5×(n/T)×100 clamped at 100)
- ✅ Workouts outside period boundaries (exclude from calculation)
- ✅ Invalid intensity/duration (reject with validation error)
- ✅ Future dates (reject gracefully)

### 5.2 Validation Rules

```python
assert 0 <= intensity <= 2.0, "Intensity must be 0.5-2.0"
assert 10 <= duration_minutes <= 600, "Duration must be 10-600 min"
assert workout_type in VALID_TYPES, f"Invalid type: {workout_type}"
assert volume >= 0, "Volume cannot be negative"
assert 0 <= consistency <= 100, "Consistency must be 0-100%"
```

### 5.3 Unit Tests Required

- [ ] Test Volume with various intensities and types
- [ ] Test Volume with edge cases (0 workouts, single workout, long duration)
- [ ] Test Consistency calculation with perfect adherence
- [ ] Test Consistency with missed workouts
- [ ] Test Consistency with high variance scheduling
- [ ] Test clamping and boundary conditions
- [ ] Test calculation time performance

---

## 6. REVIEW CHECKLIST

- [x] Mathematical formulas clearly defined
- [x] Variables explained with ranges and units
- [x] At least 2 worked examples per indicator
- [x] Use case scenario with week-by-week data
- [x] Implementation specifications documented
- [x] Edge cases identified and handled
- [x] Data requirements specified
- [x] Interpretation guidelines provided
- [x] Ready for handoff to development team

---

## 7. NEXT STEPS

1. **Development Phase:**
   - Implement formulas in `indicators.py` module
   - Create unit tests with provided examples
   - Integrate with existing analytics repository

2. **Integration Phase:**
   - Add endpoints to analytics API router
   - Connect to workout data sources
   - Implement caching strategy

3. **Validation Phase:**
   - Run unit tests with provided examples
   - Performance testing with realistic data volumes
   - UAT with select users

---

## Appendix A: Formula Card

**Volume Indicator:**
$$V = \sum_{i=1}^{n} (D_i \cdot I_i \cdot (1 + 0.1 \times T_i))$$

**Consistency Indicator:**
$$C = \frac{n}{T} \times \left(1 - \frac{\sigma_d}{D_{avg}}\right) \times 100$$

---

**Document prepared by:** Group 13
**Final review date:** April 6, 2026
**Status:** ✅ **APPROVED FOR IMPLEMENTATION**
