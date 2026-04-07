# ============================================================
# G13 - toby-fischer - Fitness Indicators - PR #287
# ============================================================
"""
Fitness Indicators Module

This module implements the Volume and Consistency indicators as formally
defined in FITNESS_INDICATORS_SPECIFICATION.md

Volume Indicator: Measures total weighted workout output
Consistency Indicator: Measures adherence to workout targets with scheduling variance
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from enum import Enum
import statistics



class WorkoutType(str, Enum):
    """Enum for workout types with their corresponding T_i coefficients"""
    CARDIO = "cardio"           # T_i = 1.0
    STRENGTH = "strength"       # T_i = 1.5
    FLEXIBILITY = "flexibility" # T_i = 0.5
    SPORTS = "sports"           # T_i = 1.2
    MIXED = "mixed"             # T_i = 0.8


@dataclass
class WorkoutSession:
    """Represents a single workout session with all required attributes"""
    date: datetime
    duration_minutes: int
    intensity: float  # 0.5 to 2.0
    workout_type: WorkoutType
    user_id: str
    notes: Optional[str] = None

    def validate(self) -> bool:
        """
        Validates workout session according to specification.

        Raises:
            ValueError: If any field violates constraints
        """
        if not 0.5 <= self.intensity <= 2.0:
            raise ValueError(f"Intensity must be 0.5-2.0, got {self.intensity}")

        if not 10 <= self.duration_minutes <= 600:
            raise ValueError(f"Duration must be 10-600 minutes, got {self.duration_minutes}")

        if self.date > datetime.now():
            raise ValueError(f"Workout date cannot be in the future: {self.date}")

        return True


@dataclass
class VolumeResult:
    """Result of volume indicator calculation"""
    total_volume: float
    period_start: datetime
    period_end: datetime
    workout_count: int
    breakdown_by_type: Dict[WorkoutType, float]
    breakdown_by_intensity: Dict[str, float]
    interpretation: str


@dataclass
class ConsistencyResult:
    """Result of consistency indicator calculation"""
    consistency_score: float  # 0-100
    workouts_completed: int
    target_workouts: int
    adherence_ratio: float    # n/T
    average_interval_days: float
    interval_variance: float  # σ_d
    interpretation: str


class VolumeIndicator:
    """
    Volume Indicator calculates weighted workout volume.

    Formula: V = Σ(D_i * I_i * (1 + 0.1 * T_i))

    Where:
    - D_i: Duration in minutes
    - I_i: Intensity factor (0.5-2.0)
    - T_i: Type coefficient
    """

    # Type coefficients as per specification
    TYPE_COEFFICIENTS = {
        WorkoutType.CARDIO: 1.0,
        WorkoutType.STRENGTH: 1.5,
        WorkoutType.FLEXIBILITY: 0.5,
        WorkoutType.SPORTS: 1.2,
        WorkoutType.MIXED: 0.8,
    }

    # Interpretation thresholds
    INTERPRETATION_THRESHOLDS = [
        (600, "High workout volume (intense/frequent training)"),
        (300, "Moderate to high workout volume"),
        (100, "Low to moderate workout volume"),
        (0, "Minimal workout volume (light activity level)"),
    ]

    @classmethod
    def get_type_coefficient(cls, workout_type: WorkoutType) -> float:
        """Get the T_i coefficient for a given workout type"""
        return cls.TYPE_COEFFICIENTS[workout_type]

    @classmethod
    def calculate_single_session(
        cls,
        duration_minutes: int,
        intensity: float,
        workout_type: WorkoutType
    ) -> float:
        """
        Calculate volume contribution from a single session.

        Args:
            duration_minutes: Duration in minutes (D_i)
            intensity: Intensity factor 0.5-2.0 (I_i)
            workout_type: Type of workout (WorkoutType)

        Returns:
            float: Volume contribution from this session
        """
        T_i = cls.get_type_coefficient(workout_type)
        volume = duration_minutes * intensity * (1 + 0.1 * T_i)
        return volume

    @classmethod
    def calculate(
        cls,
        workouts: List[WorkoutSession],
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> VolumeResult:
        """
        Calculate volume indicator for a list of workouts.

        Args:
            workouts: List of WorkoutSession objects
            period_start: Filter workouts after this date (optional)
            period_end: Filter workouts before this date (optional)

        Returns:
            VolumeResult: Detailed volume calculation results
        """
        # Validate all workouts
        for workout in workouts:
            workout.validate()

        # Filter by period if specified
        if period_start or period_end:
            start = period_start or datetime.min
            end = period_end or datetime.now()
            workouts = [
                w for w in workouts
                if start <= w.date <= end
            ]

        if not workouts:
            return VolumeResult(
                total_volume=0.0,
                period_start=period_start or datetime.now(),
                period_end=period_end or datetime.now(),
                workout_count=0,
                breakdown_by_type={},
                breakdown_by_intensity={},
                interpretation="Minimal workout volume (light activity level)",
            )

        # Calculate volume for each session
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
                workout.workout_type
            )
            total_volume += session_volume
            breakdown_by_type[workout.workout_type] += session_volume

            # Categorize by intensity
            if workout.intensity <= 0.75:
                breakdown_by_intensity["light"] += session_volume
            elif workout.intensity <= 1.25:
                breakdown_by_intensity["moderate"] += session_volume
            elif workout.intensity < 2.0:
                breakdown_by_intensity["high"] += session_volume
            else:
                breakdown_by_intensity["maximum"] += session_volume

        # Determine interpretation
        interpretation = cls._get_interpretation(total_volume)

        return VolumeResult(
            total_volume=round(total_volume, 2),
            period_start=period_start or min(w.date for w in workouts),
            period_end=period_end or max(w.date for w in workouts),
            workout_count=len(workouts),
            breakdown_by_type={k: round(v, 2) for k, v in breakdown_by_type.items()},
            breakdown_by_intensity={k: round(v, 2) for k, v in breakdown_by_intensity.items()},
            interpretation=interpretation,
        )

    @classmethod
    def _get_interpretation(cls, volume: float) -> str:
        """Get interpretation string based on volume score"""
        for threshold, description in cls.INTERPRETATION_THRESHOLDS:
            if volume >= threshold:
                return f"{description} (V = {volume:.1f})"
        return f"Minimal workout volume (light activity level) (V = {volume:.1f})"


class ConsistencyIndicator:
    """
    Consistency Indicator measures workout adherence and scheduling uniformity.

    Formula: C = (n/T) * (1 - σ_d/D_avg) * 100

    Where:
    - n: Actual workouts completed
    - T: Target workouts
    - σ_d: Standard deviation of inter-workout intervals
    - D_avg: Mean inter-workout interval
    """

    # Interpretation thresholds
    INTERPRETATION_BANDS = [
        (90, 100, "Excellent", "Near-perfect adherence; highly predictable schedule"),
        (75, 89, "Good", "Strong consistency with minor irregularities"),
        (60, 74, "Fair", "Adequate consistency; some variance in schedule"),
        (40, 59, "Weak", "Inconsistent pattern; significant gaps"),
        (0, 39, "Poor", "Very inconsistent; minimal adherence to plan"),
            ]

    @classmethod
    def calculate_inter_workout_intervals(
        cls,
        workouts: List[WorkoutSession]
    ) -> List[float]:
        """
        Calculate days between consecutive workouts.

        Args:
            workouts: List of WorkoutSession objects (should be sorted by date)

        Returns:
            List[float]: Days between consecutive workouts
        """
        if len(workouts) < 2:
            return []

        # Sort by date
        sorted_workouts = sorted(workouts, key=lambda w: w.date)

        intervals = []
        for i in range(1, len(sorted_workouts)):
            delta = sorted_workouts[i].date - sorted_workouts[i-1].date
            days = delta.days + delta.seconds / 86400  # Include fractional days
            intervals.append(days)

        return intervals

    @classmethod
    def calculate(
        cls,
        workouts: List[WorkoutSession],
        target_workouts: int,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> ConsistencyResult:
        """
        Calculate consistency indicator.

        Args:
            workouts: List of WorkoutSession objects
            target_workouts: Target number of workouts in period
            period_start: Start of period (optional)
            period_end: End of period (optional)

        Returns:
            ConsistencyResult: Detailed consistency calculation
        """
        if target_workouts <= 0:
            raise ValueError("Target workouts must be positive")

        # Validate all workouts
        for workout in workouts:
            workout.validate()

        # Filter by period
        if period_start or period_end:
            start = period_start or datetime.min
            end = period_end or datetime.now()
            workouts = [
                w for w in workouts
                if start <= w.date <= end
            ]

        n = len(workouts)

        # Special case: 0 workouts
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

        # Special case: 1 workout (can't calculate variance)
        if n == 1:
            adherence_ratio = min(n / target_workouts, 1.5)  # Cap at 1.5x
            consistency = adherence_ratio * 50  # 50% baseline for 1 workout
            consistency = min(consistency, 100)
            return ConsistencyResult(
                consistency_score=round(consistency, 1),
                workouts_completed=1,
                target_workouts=target_workouts,
                adherence_ratio=round(adherence_ratio, 3),
                average_interval_days=0.0,
                interval_variance=0.0,
                interpretation=cls._get_interpretation(consistency),
            )

        # Calculate intervals
        intervals = cls.calculate_inter_workout_intervals(workouts)

        # Calculate mean and standard deviation
        D_avg = statistics.mean(intervals)
        sigma_d = statistics.stdev(intervals) if len(intervals) > 1 else 0.0

        # Handle edge case: multiple workouts per day
        if D_avg == 0:
            D_avg = 0.5  # Treat as inter-daily sessions

        # Calculate adherence ratio
        adherence_ratio = n / target_workouts
        adherence_ratio = min(adherence_ratio, 1.5)  # Cap at 1.5x bonus

        # Calculate variance penalty
        variance_penalty = sigma_d / D_avg if D_avg > 0 else 0
        variance_penalty = min(variance_penalty, 1.0)  # Cap at 100% penalty

        # Calculate consistency score
        consistency_score = adherence_ratio * (1 - variance_penalty) * 100
        consistency_score = max(consistency_score, 0)  # Floor at 0
        consistency_score = min(consistency_score, 100)  # Ceiling at 100

        return ConsistencyResult(
            consistency_score=round(consistency_score, 1),
            workouts_completed=n,
            target_workouts=target_workouts,
            adherence_ratio=round(adherence_ratio, 3),
            average_interval_days=round(D_avg, 2),
            interval_variance=round(sigma_d, 2),
            interpretation=cls._get_interpretation(consistency_score),
        )

    @classmethod
    def _get_interpretation(cls, score: float) -> str:
        """Get interpretation based on consistency score"""
        for min_score, max_score, level, description in cls.INTERPRETATION_BANDS:
            if min_score <= score <= max_score:
                return f"{level}: {description} (C = {score:.1f}%)"
        return f"Poor: Very inconsistent; minimal adherence to plan (C = {score:.1f}%)"


# Utility function for common time periods
def get_period_bounds(period_type: str) -> tuple:
    """
    Get start and end dates for common period types.

    Args:
        period_type: 'daily', 'weekly', 'monthly', 'yearly'

    Returns:
        tuple: (start_datetime, end_datetime)
    """
    now = datetime.now()

    if period_type == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period_type == "weekly":
        start = now - timedelta(days=now.weekday())  # Monday
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period_type == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period_type == "yearly":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:
        raise ValueError(f"Unknown period type: {period_type}")

    return start, end