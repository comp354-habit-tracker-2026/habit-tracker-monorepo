# This file defines the API router for the Forecast API, including the endpoint for generating forecasts based on user input.
# The router handles POST requests to the /forecast endpoint, where it validates the incoming request data using the ForecastRequest model.
# It checks for valid input parameters and then calls the generate_forecast_data function from the services module to produce the forecast and associated metrics.
# The response is structured according to the ForecastResponse model, ensuring consistent formatting of the API output.
from fastapi import APIRouter, HTTPException
from .models import ForecastRequest, ForecastResponse
from .services import AnalyticsService

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

from datetime import datetime
from typing import List, Optional, Literal, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.analytics.business.indicators import (
    WorkoutSession,
    WorkoutType,
    VolumeIndicator,
    ConsistencyIndicator,
)
from backend.analytics.business.models import HealthScoreModel
from backend.analytics.business.validation_explainability import (
    validate_explainability_inputs,
    ExplainabilityBuilder,
    format_error_response,
    format_success_response,
)

router = APIRouter()


class WorkoutInput(BaseModel):
    """Represents one workout entry sent to the API."""
    date: datetime
    duration_minutes: int = Field(..., ge=10, le=600)
    intensity: float = Field(..., ge=0.5, le=2.0)
    workout_type: Literal["cardio", "strength", "flexibility", "sports", "mixed"]
    user_id: str
    notes: Optional[str] = None


class HealthIndicatorsRequest(BaseModel):
    """Request body for health indicators endpoint."""
    user_id: str
    workouts: List[WorkoutInput]
    target_workouts: int = Field(..., gt=0)
    alerts: Optional[List[str]] = None


def compute_inactivity(workouts: List[WorkoutSession]) -> Dict[str, Any]:
    """
    Computes inactivity status from workout history.
    This is a temporary local integration helper until Cathy’s module is fully merged.
    """
    if not workouts:
        return {
            "inactive": True,
            "days_since_last_activity": None,
            "severity": "severe",
            "message": "No activity data found."
        }

    latest_workout = max(workouts, key=lambda w: w.date)
    days_since_last_activity = (datetime.now() - latest_workout.date).days

    if days_since_last_activity >= 7:
        severity = "severe"
        inactive = True
    elif days_since_last_activity >= 3:
        severity = "mild"
        inactive = True
    else:
        severity = "none"
        inactive = False

    return {
        "inactive": inactive,
        "days_since_last_activity": days_since_last_activity,
        "severity": severity,
        "message": f"Last activity was {days_since_last_activity} day(s) ago."
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


@router.post("/api/health-indicators")
async def health_indicators_endpoint(request: HealthIndicatorsRequest):
    """Computes health indicators, health score, inactivity, and explanations."""
    try:
        workout_sessions = [
            WorkoutSession(
                date=w.date,
                duration_minutes=w.duration_minutes,
                intensity=w.intensity,
                workout_type=WorkoutType(w.workout_type),
                user_id=w.user_id,
                notes=w.notes,
            )
            for w in request.workouts
        ]

        # Fitness indicators
        volume_result = VolumeIndicator.calculate(workout_sessions)
        consistency_result = ConsistencyIndicator.calculate(
            workouts=workout_sessions,
            target_workouts=request.target_workouts,
        )

        # Inactivity
        inactivity_result = compute_inactivity(workout_sessions)

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