# ============================================================
# G13 - toby-fischer - Fitness Indicators - PR #287
# ============================================================

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
import statistics


class WorkoutType(str, Enum):
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    SPORTS = "sports"
    MIXED = "mixed"


@dataclass
class WorkoutSession:
    date: datetime
    duration_minutes: int
    intensity: float
    workout_type: WorkoutType
    user_id: str
    notes: Optional[str] = None

    def validate(self) -> bool:
        if not 0.5 <= self.intensity <= 2.0:
            raise ValueError(f"Intensity must be 0.5-2.0, got {self.intensity}")
        if not 10 <= self.duration_minutes <= 600:
            raise ValueError(f"Duration must be 10-600 minutes, got {self.duration_minutes}")
        if self.date > datetime.now():
            raise ValueError(f"Workout date cannot be in the future: {self.date}")
        return True


@dataclass
class VolumeResult:
    total_volume: float
    period_start: datetime
    period_end: datetime
    workout_count: int
    breakdown_by_type: Dict[WorkoutType, float]
    breakdown_by_intensity: Dict[str, float]
    interpretation: str


@dataclass
class ConsistencyResult:
    consistency_score: float
    workouts_completed: int
    target_workouts: int
    adherence_ratio: float
    average_interval_days: float
    interval_variance: float
    interpretation: str


class VolumeIndicator:
    TYPE_COEFFICIENTS = {
        WorkoutType.CARDIO: 1.0,
        WorkoutType.STRENGTH: 1.5,
        WorkoutType.FLEXIBILITY: 0.5,
        WorkoutType.SPORTS: 1.2,
        WorkoutType.MIXED: 0.8,
    }

    INTERPRETATION_THRESHOLDS = [
        (600, "High workout volume (intense/frequent training)"),
        (300, "Moderate to high workout volume"),
        (100, "Low to moderate workout volume"),
        (0, "Minimal workout volume (light activity level)"),
    ]

    @classmethod
    def get_type_coefficient(cls, workout_type: WorkoutType) -> float:
        return cls.TYPE_COEFFICIENTS[workout_type]

    @classmethod
    def calculate_single_session(
        cls,
        duration_minutes: int,
        intensity: float,
        workout_type: WorkoutType
    ) -> float:
        t_i = cls.get_type_coefficient(workout_type)
        return duration_minutes * intensity * (1 + 0.1 * t_i)

    @classmethod
    def calculate(
        cls,
        workouts: List[WorkoutSession],
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> VolumeResult:
        for workout in workouts:
            workout.validate()

        if period_start or period_end:
            start = period_start or datetime.min
            end = period_end or datetime.now()
            workouts = [w for w in workouts if start <= w.date <= end]

        if not workouts:
            now = datetime.now()
            return VolumeResult(
                total_volume=0.0,
                period_start=period_start or now,
                period_end=period_end or now,
                workout_count=0,
                breakdown_by_type={},
                breakdown_by_intensity={},
                interpretation="Minimal workout volume (light activity level)",
            )

        total_volume = 0.0
        breakdown_by_type: Dict[WorkoutType, float] = {t: 0.0 for t in WorkoutType}
        breakdown_by_intensity: Dict[str, float] = {
            "light": 0.0,
            "moderate": 0.0,
            "high": 0.0,
            "maximum": 0.0,
        }

        for workout in workouts:
            session_volume = cls.calculate_single_session(
                workout.duration_minutes,
                workout.intensity,
                workout.workout_type,
            )
            total_volume += session_volume
            breakdown_by_type[workout.workout_type] += session_volume

            if workout.intensity <= 0.75:
                breakdown_by_intensity["light"] += session_volume
            elif workout.intensity <= 1.25:
                breakdown_by_intensity["moderate"] += session_volume
            elif workout.intensity < 2.0:
                breakdown_by_intensity["high"] += session_volume
            else:
                breakdown_by_intensity["maximum"] += session_volume

        return VolumeResult(
            total_volume=round(total_volume, 2),
            period_start=period_start or min(w.date for w in workouts),
            period_end=period_end or max(w.date for w in workouts),
            workout_count=len(workouts),
            breakdown_by_type={k: round(v, 2) for k, v in breakdown_by_type.items()},
            breakdown_by_intensity={k: round(v, 2) for k, v in breakdown_by_intensity.items()},
            interpretation=cls._get_interpretation(total_volume),
        )

    @classmethod
    def _get_interpretation(cls, volume: float) -> str:
        for threshold, description in cls.INTERPRETATION_THRESHOLDS:
            if volume >= threshold:
                return f"{description} (V = {volume:.1f})"
        # unreachable for valid inputs, kept for safety
        return f"Minimal workout volume (light activity level) (V = {volume:.1f})"


class ConsistencyIndicator:
    INTERPRETATION_BANDS = [
        (90, 100, "Excellent", "Near-perfect adherence; highly predictable schedule"),
        (75, 89, "Good", "Strong consistency with minor irregularities"),
        (60, 74, "Fair", "Adequate consistency; some variance in schedule"),
        (40, 59, "Weak", "Inconsistent pattern; significant gaps"),
        (0, 39, "Poor", "Very inconsistent; minimal adherence to plan"),
    ]

    @classmethod
    def calculate_inter_workout_intervals(cls, workouts: List[WorkoutSession]) -> List[float]:
        if len(workouts) < 2:
            return []

        sorted_workouts = sorted(workouts, key=lambda w: w.date)
        intervals = []
        for i in range(1, len(sorted_workouts)):
            delta = sorted_workouts[i].date - sorted_workouts[i - 1].date
            intervals.append(delta.days + delta.seconds / 86400)
        return intervals

    @classmethod
    def calculate(
        cls,
        workouts: List[WorkoutSession],
        target_workouts: int,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> ConsistencyResult:
        if target_workouts <= 0:
            raise ValueError("Target workouts must be positive")

        for workout in workouts:
            workout.validate()

        if period_start or period_end:
            start = period_start or datetime.min
            end = period_end or datetime.now()
            workouts = [w for w in workouts if start <= w.date <= end]

        n = len(workouts)

        if n == 0:
            return ConsistencyResult(
                consistency_score=0.0,
                workouts_completed=0,
                target_workouts=target_workouts,
                adherence_ratio=0.0,
                average_interval_days=0.0,
                interval_variance=0.0,
                interpretation="Poor: Very inconsistent; minimal adherence to plan",
            )

        if n == 1:
            adherence_ratio = min(n / target_workouts, 1.5)
            consistency = min(adherence_ratio * 50, 100)
            return ConsistencyResult(
                consistency_score=round(consistency, 1),
                workouts_completed=1,
                target_workouts=target_workouts,
                adherence_ratio=round(adherence_ratio, 3),
                average_interval_days=0.0,
                interval_variance=0.0,
                interpretation=cls._get_interpretation(consistency),
            )

        intervals = cls.calculate_inter_workout_intervals(workouts)
        d_avg = statistics.mean(intervals)
        sigma_d = statistics.stdev(intervals) if len(intervals) > 1 else 0.0

        if d_avg == 0:
            d_avg = 0.5

        adherence_ratio = min(n / target_workouts, 1.5)
        variance_penalty = min((sigma_d / d_avg) if d_avg > 0 else 0, 1.0)
        consistency_score = adherence_ratio * (1 - variance_penalty) * 100
        consistency_score = max(0, min(consistency_score, 100))

        return ConsistencyResult(
            consistency_score=round(consistency_score, 1),
            workouts_completed=n,
            target_workouts=target_workouts,
            adherence_ratio=round(adherence_ratio, 3),
            average_interval_days=round(d_avg, 2),
            interval_variance=round(sigma_d, 2),
            interpretation=cls._get_interpretation(consistency_score),
        )

    @classmethod
    def _get_interpretation(cls, score: float) -> str:
        for min_score, max_score, level, description in cls.INTERPRETATION_BANDS:
            if min_score <= score <= max_score:
                return f"{level}: {description} (C = {score:.1f}%)"
        return f"Poor: Very inconsistent; minimal adherence to plan (C = {score:.1f}%)"