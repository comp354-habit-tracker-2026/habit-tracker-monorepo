# This file defines the API router for the Forecast API, including the endpoint for generating forecasts based on user input.
# The router handles POST requests to the /forecast endpoint, where it validates the incoming request data using the ForecastRequest model.
# It checks for valid input parameters and then calls the generate_forecast_data function from the services module to produce the forecast and associated metrics.
# The response is structured according to the ForecastResponse model, ensuring consistent formatting of the API output.
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .models import ForecastRequest, ForecastResponse
from .services import AnalyticsService
from analytics.business.indicators import (
    WorkoutSession,
    WorkoutType,
    VolumeIndicator,
    ConsistencyIndicator,
)
from analytics.business.models import HealthScoreModel
from analytics.business.validation_explainability import (
    validate_explainability_inputs,
    ExplainabilityBuilder,
    format_error_response,
    format_success_response,
)

router = APIRouter()

service = AnalyticsService()


@router.post("/forecast", response_model=ForecastResponse)
def forecast_endpoint(request: ForecastRequest):

    if request.numOfDays <= 0:
        raise HTTPException(status_code=400, detail="numOfDays must be > 0")

    if request.forecastType not in ["baseline", "trained"]:
        raise HTTPException(status_code=422, detail="Invalid forecastType")

    # Call teammate's service
    result = service.forecast_preview(request.userID)

    # FORMAT result to match your API contract
    forecast = []
    for i, val in enumerate(result):
        forecast.append({
            "date": f"2026-04-{i+1:02d}",
            "predictedValue": float(val)
        })

    return {
        "userID": request.userID,
        "forecastType": request.forecastType,
        "forecast": forecast,
        "metrics": {
            "mae": 0.0,
            "rmse": 0.0
        }
    }

# ============================================================
# G13 - MMingQwQ - Health Indicators API  - Issue #22
# ============================================================


class HealthIndicatorsRequest(BaseModel):
    """Request body for health indicators endpoint."""
    user_id: str
    from_date: datetime
    to_date: datetime
    window: Optional[str] = None
    target_workouts: int = Field(..., gt=0)
    alerts: Optional[List[str]] = None


def fetch_activity_data(
    user_id: str,
    from_date: datetime,
    to_date: datetime,
) -> List[Dict[str, Any]]:
    """
    Fetches activity data for the given user and date range.
    Returns a list of workout dicts with keys: date, duration_minutes, intensity,
    workout_type, user_id, and optionally notes.
    """
    # Placeholder - replace with real data-source call when available.
    return []


def compute_inactivity(
    workouts: List[WorkoutSession],
    to_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Computes inactivity status from workout history relative to *to_date*.

    A user is considered inactive only when they have had no workout in the
    last 7 days (severe inactivity).  3-6 days without a workout is flagged as
    a mild warning but does not set inactive=True.
    """
    if not workouts:
        return {
            "inactive": True,
            "days_since_last_activity": None,
            "severity": "severe",
            "message": "No activity data found.",
        }

    reference = to_date or datetime.now()
    latest_workout = max(workouts, key=lambda w: w.date)
    days_since_last_activity = (reference - latest_workout.date).days

    if days_since_last_activity >= 7:
        severity = "severe"
        inactive = True
    elif days_since_last_activity >= 3:
        severity = "mild"
        inactive = False
    else:
        severity = "none"
        inactive = False

    return {
        "inactive": inactive,
        "days_since_last_activity": days_since_last_activity,
        "severity": severity,
        "message": f"Last activity was {days_since_last_activity} day(s) ago.",
    }


def build_score_input(
    volume_result,
    consistency_result,
    inactivity_result: Dict[str, Any],
) -> Dict[str, Optional[float]]:
    """Builds normalized indicator dict for health score calculation."""
    return {
        "volume": volume_result.total_volume,
        "consistency": consistency_result.consistency_score,
        "inactive": 1 if inactivity_result["inactive"] else 0,
    }


@router.post("/health-indicators")
async def health_indicators_endpoint(request: HealthIndicatorsRequest):
    """Computes health indicators, health score, inactivity, and explanations."""
    # Validate date range
    if request.from_date > request.to_date:
        raise HTTPException(
            status_code=400,
            detail=format_error_response("from_date must not be later than to_date"),
        )

    # Fetch activity data (503 if the data source is unavailable)
    try:
        activity_data = fetch_activity_data(
            user_id=request.user_id,
            from_date=request.from_date,
            to_date=request.to_date,
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=format_error_response(f"Activity data service unavailable: {str(e)}"),
        )

    try:
        # Convert raw dicts to WorkoutSession objects
        workout_sessions = []
        for w in activity_data:
            date = (
                w["date"]
                if isinstance(w["date"], datetime)
                else datetime.fromisoformat(str(w["date"]))
            )
            workout_sessions.append(
                WorkoutSession(
                    date=date,
                    duration_minutes=w["duration_minutes"],
                    intensity=w["intensity"],
                    workout_type=WorkoutType(w["workout_type"]),
                    user_id=w["user_id"],
                    notes=w.get("notes"),
                )
            )

        # Fitness indicators
        volume_result = VolumeIndicator.calculate(workout_sessions)
        consistency_result = ConsistencyIndicator.calculate(
            workouts=workout_sessions,
            target_workouts=request.target_workouts,
        )

        # Inactivity (relative to to_date)
        inactivity_result = compute_inactivity(workout_sessions, to_date=request.to_date)

        # Build score input
        indicators = build_score_input(
            volume_result=volume_result,
            consistency_result=consistency_result,
            inactivity_result=inactivity_result,
        )

        # Validate explanation inputs
        validate_explainability_inputs(
            indicators=indicators,
            health_score=None,
            score_range=None,
            alerts=request.alerts,
        )

        # Health score
        score_model = HealthScoreModel()
        score_result = score_model.compute_health_score(indicators)

        # Explanation
        explanation_builder = ExplainabilityBuilder()
        explanations = explanation_builder.build_explanation(
            indicators=indicators,
            health_score=score_result.score,
            score_range=score_result.score_range,
            alerts=request.alerts,
        )

        # Include the inactivity message in the explanations for visibility
        inactivity_message = inactivity_result.get("message")
        if inactivity_message and inactivity_message not in explanations:
            explanations.append(inactivity_message)

        response_data = {
            "user_id": request.user_id,
            "indicators": {
                "volume": {
                    "total_volume": volume_result.total_volume,
                    "workout_count": volume_result.workout_count,
                    "interpretation": volume_result.interpretation,
                },
                "consistency": {
                    "consistency_score": consistency_result.consistency_score,
                    "workouts_completed": consistency_result.workouts_completed,
                    "target_workouts": consistency_result.target_workouts,
                    "interpretation": consistency_result.interpretation,
                },
            },
            "health_score": {
                "score": score_result.score,
                "score_range": score_result.score_range,
                "explanation": score_result.explanation,
            },
            "inactivity": inactivity_result,
            "alerts": request.alerts or [],
            "messages": explanations,
        }

        return format_success_response(response_data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=format_error_response(str(e)))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response(f"Internal server error: {str(e)}")
        )
