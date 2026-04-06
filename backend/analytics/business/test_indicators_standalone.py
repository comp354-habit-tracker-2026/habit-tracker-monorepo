"""
Standalone Unit Tests for Fitness Indicators

This test file is designed to run independently without Django dependencies.
Run with: python -m pytest test_indicators_standalone.py -v
"""

import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from datetime import datetime, timedelta

# Import only the indicators module (no Django deps)
from analytics.business.indicators import (
    WorkoutSession,
    WorkoutType,
    VolumeIndicator,
    ConsistencyIndicator,
    VolumeResult,
    ConsistencyResult,
    get_period_bounds,
)


class TestVolumeIndicatorExample1(unittest.TestCase):
    """Test Volume Indicator with Example 1 from specification"""

    def setUp(self):
        """Set up Example 1: Weekly Volume Calculation (Gym Training)"""
        # Use dates from last week (March 30 - April 5, 2026)
        base_date = datetime(2026, 3, 30)  # Monday of last week

        self.workouts = [
            WorkoutSession(
                date=base_date,  # Mon
                duration_minutes=45,
                intensity=1.5,
                workout_type=WorkoutType.STRENGTH,
                user_id="user_001"
            ),
            WorkoutSession(
                date=base_date + timedelta(days=2),  # Wed
                duration_minutes=30,
                intensity=1.0,
                workout_type=WorkoutType.CARDIO,
                user_id="user_001"
            ),
            WorkoutSession(
                date=base_date + timedelta(days=4),  # Fri
                duration_minutes=50,
                intensity=1.5,
                workout_type=WorkoutType.STRENGTH,
                user_id="user_001"
            ),
            WorkoutSession(
                date=base_date + timedelta(days=5),  # Sat
                duration_minutes=20,
                intensity=0.5,
                workout_type=WorkoutType.FLEXIBILITY,
                user_id="user_001"
            ),
        ]

    def test_example_1_volume_calculation(self):
        """
        Test Example 1 from specification:

        Monday: 45 × 1.5 × (1 + 0.1×1.5) = 77.625
        Wednesday: 30 × 1.0 × (1 + 0.1×1.0) = 33.000
        Friday: 50 × 1.5 × (1 + 0.1×1.5) = 86.250
        Saturday: 20 × 0.5 × (1 + 0.1×0.5) = 10.500
        Total: 207.375
        """
        result = VolumeIndicator.calculate(self.workouts)

        print(f"\n✓ Example 1 Volume Test")
        print(f"  Total Volume: {result.total_volume} (expected: 207.375)")
        print(f"  Workouts: {result.workout_count}")
        print(f"  Interpretation: {result.interpretation}")

        self.assertAlmostEqual(result.total_volume, 207.375, places=1,
                             msg=f"Expected 207.375, got {result.total_volume}")
        self.assertEqual(result.workout_count, 4)
        self.assertEqual(result.period_start, datetime(2026, 3, 30))


class TestVolumeIndicatorExample2(unittest.TestCase):
    """Test Volume Indicator with Example 2 from specification"""

    def setUp(self):
        """Set up Example 2: Weekly Volume Calculation (Mixed Training)"""
        base_date = datetime(2026, 3, 23)  # Two weeks before today

        self.workouts = [
            WorkoutSession(
                date=base_date,  # Mon
                duration_minutes=60,
                intensity=1.5,
                workout_type=WorkoutType.MIXED,
                user_id="user_002"
            ),
            WorkoutSession(
                date=base_date + timedelta(days=1),  # Tue
                duration_minutes=40,
                intensity=1.0,
                workout_type=WorkoutType.CARDIO,
                user_id="user_002"
            ),
            WorkoutSession(
                date=base_date + timedelta(days=2),  # Wed
                duration_minutes=45,
                intensity=1.2,
                workout_type=WorkoutType.SPORTS,
                user_id="user_002"
            ),
            WorkoutSession(
                date=base_date + timedelta(days=4),  # Fri
                duration_minutes=55,
                intensity=1.5,
                workout_type=WorkoutType.STRENGTH,
                user_id="user_002"
            ),
            WorkoutSession(
                date=base_date + timedelta(days=5),  # Sat
                duration_minutes=30,
                intensity=1.0,
                workout_type=WorkoutType.CARDIO,
                user_id="user_002"
            ),
            WorkoutSession(
                date=base_date + timedelta(days=6),  # Sun
                duration_minutes=25,
                intensity=0.5,
                workout_type=WorkoutType.FLEXIBILITY,
                user_id="user_002"
            ),
        ]

    def test_example_2_volume_calculation(self):
        """
        Test Example 2 from specification:

        Monday: 60 × 1.5 × (1 + 0.1×0.8) = 97.200
        Tuesday: 40 × 1.0 × (1 + 0.1×1.0) = 44.000
        Wednesday: 45 × 1.2 × (1 + 0.1×1.2) = 60.480
        Friday: 55 × 1.5 × (1 + 0.1×1.5) = 94.875
        Saturday: 30 × 1.0 × (1 + 0.1×1.0) = 33.000
        Sunday: 25 × 0.5 × (1 + 0.1×0.5) = 13.125
        Total: 342.680
        """
        result = VolumeIndicator.calculate(self.workouts)

        print(f"\n✓ Example 2 Volume Test")
        print(f"  Total Volume: {result.total_volume} (expected: 342.680)")
        print(f"  Workouts: {result.workout_count}")
        print(f"  Interpretation: {result.interpretation}")

        self.assertAlmostEqual(result.total_volume, 342.68, places=1,
                             msg=f"Expected 342.68, got {result.total_volume}")
        self.assertEqual(result.workout_count, 6)


class TestConsistencyIndicatorExample1(unittest.TestCase):
    """Test Consistency Indicator with Example 1: Consistent Training Schedule"""

    def setUp(self):
        """
        Set up Example 1: Consistent 4-week training block
        Target: 4 workouts/week = 16 total
        Pattern: Monday, Wednesday, Friday, Saturday each week
        """
        base_date = datetime(2026, 3, 9)  # 4 weeks ago
        monday = base_date - timedelta(days=base_date.weekday())  # Get Monday

        self.workouts = []
        for week in range(4):
            week_start = monday + timedelta(weeks=week)

            self.workouts.extend([
                WorkoutSession(
                    date=week_start,  # Mon
                    duration_minutes=60,
                    intensity=1.0,
                    workout_type=WorkoutType.STRENGTH,
                    user_id="user_001"
                ),
                WorkoutSession(
                    date=week_start + timedelta(days=2),  # Wed
                    duration_minutes=45,
                    intensity=1.0,
                    workout_type=WorkoutType.CARDIO,
                    user_id="user_001"
                ),
                WorkoutSession(
                    date=week_start + timedelta(days=4),  # Fri
                    duration_minutes=60,
                    intensity=1.0,
                    workout_type=WorkoutType.STRENGTH,
                    user_id="user_001"
                ),
                WorkoutSession(
                    date=week_start + timedelta(days=5),  # Sat
                    duration_minutes=45,
                    intensity=0.8,
                    workout_type=WorkoutType.CARDIO,
                    user_id="user_001"
                ),
            ])

    def test_example_1_consistency(self):
        """
        Test Example 1: Consistent training schedule
        Expected: C ≈ 75.3%

        Pattern produces intervals: [2, 2, 1, 2, 2, 2, 1, 2, ...]
        D_avg = 28/16 = 1.75 days
        σ_d = 0.433 days
        C = 1.0 × (1 - 0.433/1.75) × 100 = 75.3%
        """
        result = ConsistencyIndicator.calculate(
            self.workouts,
            target_workouts=16
        )

        print(f"\n✓ Example 1 Consistency Test (Consistent Schedule)")
        print(f"  Consistency Score: {result.consistency_score}% (expected: ~75.3%)")
        print(f"  Workouts: {result.workouts_completed}/{result.target_workouts}")
        print(f"  Avg Interval: {result.average_interval_days} days")
        print(f"  Interval Variance: {result.interval_variance} days")
        print(f"  Interpretation: {result.interpretation}")

        self.assertEqual(result.workouts_completed, 16)
        self.assertEqual(result.target_workouts, 16)
        # Should be around 75%
        self.assertGreater(result.consistency_score, 70)
        self.assertLess(result.consistency_score, 80)
        self.assertIn("Fair", result.interpretation)


class TestConsistencyIndicatorExample2(unittest.TestCase):
    """Test Consistency Indicator with Example 2: Inconsistent Training Schedule"""

    def setUp(self):
        """
        Set up Example 2: Inconsistent 4-week training block
        Target: 4 workouts/week = 16 total
        Actual: 13 workouts with large gaps
        """
        base_date = datetime(2026, 3, 9)  # 4 weeks ago
        monday = base_date - timedelta(days=base_date.weekday())

        # Inconsistent pattern with gaps
        self.workouts = [
            # Week 1: Mon, Fri (skip Wed, Sat)
            WorkoutSession(
                date=monday,  # Day 1
                duration_minutes=60,
                intensity=1.0,
                workout_type=WorkoutType.STRENGTH,
                user_id="user_002"
            ),
            WorkoutSession(
                date=monday + timedelta(days=4),  # Day 5 (Fri)
                duration_minutes=60,
                intensity=1.0,
                workout_type=WorkoutType.STRENGTH,
                user_id="user_002"
            ),
            # Week 2: Mon, Wed, Fri (skip Sat)
            WorkoutSession(
                date=monday + timedelta(days=7),  # Day 8
                duration_minutes=60,
                intensity=1.0,
                workout_type=WorkoutType.STRENGTH,
                user_id="user_002"
            ),
            WorkoutSession(
                date=monday + timedelta(days=9),  # Day 10
                duration_minutes=45,
                intensity=1.0,
                workout_type=WorkoutType.CARDIO,
                user_id="user_002"
            ),
            WorkoutSession(
                date=monday + timedelta(days=11),  # Day 12
                duration_minutes=60,
                intensity=1.0,
                workout_type=WorkoutType.STRENGTH,
                user_id="user_002"
            ),
            # Week 3: Sat only (8-day gap!)
            WorkoutSession(
                date=monday + timedelta(days=19),  # Day 20
                duration_minutes=45,
                intensity=1.0,
                workout_type=WorkoutType.CARDIO,
                user_id="user_002"
            ),
            # Week 4: Wed, Fri, Sat, Mon(+week5)
            WorkoutSession(
                date=monday + timedelta(days=23),  # Day 24
                duration_minutes=60,
                intensity=1.0,
                workout_type=WorkoutType.STRENGTH,
                user_id="user_002"
            ),
            WorkoutSession(
                date=monday + timedelta(days=25),  # Day 26
                duration_minutes=60,
                intensity=1.0,
                workout_type=WorkoutType.STRENGTH,
                user_id="user_002"
            ),
            WorkoutSession(
                date=monday + timedelta(days=26),  # Day 27
                duration_minutes=45,
                intensity=1.0,
                workout_type=WorkoutType.CARDIO,
                user_id="user_002"
            ),
            WorkoutSession(
                date=monday + timedelta(days=28),  # Day 29 (week 5)
                duration_minutes=60,
                intensity=1.0,
                workout_type=WorkoutType.STRENGTH,
                user_id="user_002"
            ),
        ]

    def test_example_2_consistency(self):
        """
        Test Example 2: Inconsistent training schedule
        Expected: C ≈ 17.4%

        13 out of 16 target workouts (81%)
        High variance due to 8-day gap
        Large variance penalty
        """
        result = ConsistencyIndicator.calculate(
            self.workouts,
            target_workouts=16
        )

        print(f"\n✓ Example 2 Consistency Test (Inconsistent Schedule)")
        print(f"  Consistency Score: {result.consistency_score}% (expected: ~17.4%)")
        print(f"  Workouts: {result.workouts_completed}/{result.target_workouts}")
        print(f"  Avg Interval: {result.average_interval_days} days")
        print(f"  Interval Variance: {result.interval_variance} days")
        print(f"  Interpretation: {result.interpretation}")

        self.assertEqual(result.workouts_completed, 10)
        self.assertEqual(result.target_workouts, 16)
        # Should be relatively low (around 17%)
        self.assertLess(result.consistency_score, 50)
        self.assertIn("Poor", result.interpretation)


class TestAllEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_volume_zero_workouts(self):
        """Test volume with no workouts"""
        result = VolumeIndicator.calculate([])
        self.assertEqual(result.total_volume, 0.0)
        self.assertEqual(result.workout_count, 0)
        print(f"\n✓ Volume: Zero workouts handled correctly")

    def test_consistency_zero_workouts(self):
        """Test consistency with no workouts"""
        result = ConsistencyIndicator.calculate([], target_workouts=4)
        self.assertEqual(result.consistency_score, 0.0)
        self.assertEqual(result.workouts_completed, 0)
        print(f"\n✓ Consistency: Zero workouts handled correctly")

    def test_consistency_single_workout(self):
        """Test consistency with only one workout"""
        workout = WorkoutSession(
            date=datetime.now(),
            duration_minutes=60,
            intensity=1.0,
            workout_type=WorkoutType.STRENGTH,
            user_id="user_001"
        )
        result = ConsistencyIndicator.calculate([workout], target_workouts=4)

        self.assertEqual(result.workouts_completed, 1)
        self.assertGreater(result.consistency_score, 0)
        self.assertLess(result.consistency_score, 100)
        print(f"\n✓ Consistency: Single workout handled (C={result.consistency_score}%)")

    def test_volume_min_duration(self):
        """Test volume with minimum duration (10 minutes)"""
        workout = WorkoutSession(
            date=datetime.now(),
            duration_minutes=10,
            intensity=1.0,
            workout_type=WorkoutType.CARDIO,
            user_id="user_001"
        )
        result = VolumeIndicator.calculate([workout])
        expected = 10 * 1.0 * (1 + 0.1 * 1.0)  # 11.0
        self.assertAlmostEqual(result.total_volume, 11.0, places=1)
        print(f"\n✓ Volume: Minimum duration handled (V={result.total_volume})")

    def test_volume_max_duration(self):
        """Test volume with maximum duration (600 minutes)"""
        workout = WorkoutSession(
            date=datetime.now(),
            duration_minutes=600,
            intensity=1.0,
            workout_type=WorkoutType.CARDIO,
            user_id="user_001"
        )
        result = VolumeIndicator.calculate([workout])
        expected = 600 * 1.0 * (1 + 0.1 * 1.0)  # 660.0
        self.assertAlmostEqual(result.total_volume, 660.0, places=1)
        print(f"\n✓ Volume: Maximum duration handled (V={result.total_volume})")


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
