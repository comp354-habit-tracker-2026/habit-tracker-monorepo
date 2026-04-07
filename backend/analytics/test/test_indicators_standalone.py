# ============================================================
# G13 - toby-fischer - Fitness Indicators - PR #287
# ============================================================
import unittest
from datetime import datetime, timedelta

from analytics.business.indicators import (
    WorkoutSession,
    WorkoutType,
    VolumeIndicator,
    ConsistencyIndicator,
)


class TestIndicatorsCoverageBoost(unittest.TestCase):
    def test_validate_rejects_low_intensity(self):
        workout = WorkoutSession(
            date=datetime.now() - timedelta(days=1),
            duration_minutes=30,
            intensity=0.4,
            workout_type=WorkoutType.CARDIO,
            user_id="u1",
        )
        with self.assertRaises(ValueError):
            workout.validate()

    def test_validate_rejects_bad_duration(self):
        workout = WorkoutSession(
            date=datetime.now() - timedelta(days=1),
            duration_minutes=5,
            intensity=1.0,
            workout_type=WorkoutType.CARDIO,
            user_id="u1",
        )
        with self.assertRaises(ValueError):
            workout.validate()

    def test_validate_rejects_future_date(self):
        workout = WorkoutSession(
            date=datetime.now() + timedelta(days=1),
            duration_minutes=30,
            intensity=1.0,
            workout_type=WorkoutType.CARDIO,
            user_id="u1",
        )
        with self.assertRaises(ValueError):
            workout.validate()

    def test_volume_period_filtering(self):
        old_workout = WorkoutSession(
            date=datetime(2025, 1, 1),
            duration_minutes=30,
            intensity=1.0,
            workout_type=WorkoutType.CARDIO,
            user_id="u1",
        )
        new_workout = WorkoutSession(
            date=datetime(2026, 4, 1),
            duration_minutes=40,
            intensity=1.0,
            workout_type=WorkoutType.CARDIO,
            user_id="u1",
        )
        result = VolumeIndicator.calculate(
            [old_workout, new_workout],
            period_start=datetime(2026, 1, 1),
        )
        self.assertEqual(result.workout_count, 1)
        self.assertGreater(result.total_volume, 0)

    def test_volume_period_filtering_to_empty(self):
        workout = WorkoutSession(
            date=datetime(2024, 1, 1),
            duration_minutes=30,
            intensity=1.0,
            workout_type=WorkoutType.CARDIO,
            user_id="u1",
        )
        result = VolumeIndicator.calculate(
            [workout],
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 12, 31),
        )
        self.assertEqual(result.workout_count, 0)
        self.assertEqual(result.total_volume, 0.0)

    def test_volume_interpretation_high(self):
        text = VolumeIndicator._get_interpretation(700)
        self.assertIn("High workout volume", text)

    def test_calculate_intervals_less_than_two(self):
        workout = WorkoutSession(
            date=datetime.now() - timedelta(days=1),
            duration_minutes=30,
            intensity=1.0,
            workout_type=WorkoutType.CARDIO,
            user_id="u1",
        )
        self.assertEqual(
            ConsistencyIndicator.calculate_inter_workout_intervals([workout]),
            []
        )

    def test_consistency_invalid_target_workouts(self):
        with self.assertRaises(ValueError):
            ConsistencyIndicator.calculate([], target_workouts=0)

    def test_consistency_period_filtering(self):
        old_workout = WorkoutSession(
            date=datetime(2025, 1, 1),
            duration_minutes=30,
            intensity=1.0,
            workout_type=WorkoutType.CARDIO,
            user_id="u1",
        )
        new_workout = WorkoutSession(
            date=datetime(2026, 4, 1),
            duration_minutes=40,
            intensity=1.0,
            workout_type=WorkoutType.CARDIO,
            user_id="u1",
        )
        result = ConsistencyIndicator.calculate(
            [old_workout, new_workout],
            target_workouts=2,
            period_start=datetime(2026, 1, 1),
        )
        self.assertEqual(result.workouts_completed, 1)

    def test_consistency_same_day_workouts_hits_davg_zero_branch(self):
        same_day = datetime(2026, 4, 1, 10, 0, 0)
        workouts = [
            WorkoutSession(
                date=same_day,
                duration_minutes=30,
                intensity=1.0,
                workout_type=WorkoutType.CARDIO,
                user_id="u1",
            ),
            WorkoutSession(
                date=same_day,
                duration_minutes=45,
                intensity=1.0,
                workout_type=WorkoutType.STRENGTH,
                user_id="u1",
            ),
        ]
        result = ConsistencyIndicator.calculate(workouts, target_workouts=2)
        self.assertEqual(result.workouts_completed, 2)
        self.assertGreaterEqual(result.consistency_score, 0)

    def test_consistency_interpretation_excellent(self):
        text = ConsistencyIndicator._get_interpretation(95)
        self.assertIn("Excellent", text)