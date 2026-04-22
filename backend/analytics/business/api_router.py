# This file defines the API router for the Forecast API, including the endpoint for generating forecasts based on user input.
# The router handles POST requests to the /forecast endpoint, where it validates the incoming request data using the ForecastRequest model.
# It checks for valid input parameters and then calls the generate_forecast_data function from the services module to produce the forecast and associated metrics.
# The response is structured according to the ForecastResponse model, ensuring consistent formatting of the API output.
from datetime import datetime
from typing import List, Optional, Dict, Any

from asgiref.sync import sync_to_async
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
    from activities.models import Activity as ActivityModel
    queryset = ActivityModel.objects.filter(
        account__user_id=user_id,
        date__range=(from_date.date(), to_date.date()),
    ).select_related("account")
    return [
        {
            "date": datetime(a.date.year, a.date.month, a.date.day),
            "duration_minutes": a.duration,
            "intensity": 1.0,
            "workout_type": a.activity_type,
            "user_id": str(user_id),
            "notes": None,
        }
        for a in queryset
    ]


def _check_pending_outbox(user_id: str) -> bool:
    from core.models import OutboxEvent
    return OutboxEvent.objects.filter(
        status=OutboxEvent.Status.PENDING,
        payload__user_id=user_id,
    ).exists()


def compute_inactivity(
    workouts: List[WorkoutSession],
    to_date: Optional[datetime] = None,
) -> Dict[str, Any]:
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
    return {
        "volume": volume_result.total_volume,
        "consistency": consistency_result.consistency_score,
        "inactive": 1 if inactivity_result["inactive"] else 0,
    }


@router.post("/health-indicators")
async def health_indicators_endpoint(request: HealthIndicatorsRequest):
    if request.from_date > request.to_date:
        raise HTTPException(
            status_code=400,
            detail=format_error_response("from_date must not be later than to_date"),
        )

    try:
        activity_data = await sync_to_async(fetch_activity_data)(
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
        workout_sessions = []
        for w in activity_data:
            parsed_date = (
                w["date"]
                if isinstance(w["date"], datetime)
                else datetime.fromisoformat(str(w["date"]))
            )
            workout_sessions.append(
                WorkoutSession(
                    date=parsed_date,
                    duration_minutes=w["duration_minutes"],
                    intensity=w["intensity"],
                    workout_type=WorkoutType(w["workout_type"]),
                    user_id=w["user_id"],
                    notes=w.get("notes"),
                )
            )

        volume_result = VolumeIndicator.calculate(workout_sessions)
        consistency_result = ConsistencyIndicator.calculate(
            workouts=workout_sessions,
            target_workouts=request.target_workouts,
        )

        inactivity_result = compute_inactivity(workout_sessions, to_date=request.to_date)

        indicators = build_score_input(
            volume_result=volume_result,
            consistency_result=consistency_result,
            inactivity_result=inactivity_result,
        )

        validate_explainability_inputs(
            indicators=indicators,
            health_score=None,
            score_range=None,
            alerts=request.alerts,
        )

        score_model = HealthScoreModel()
        score_result = score_model.compute_health_score(indicators)

        explanation_builder = ExplainabilityBuilder()
        explanations = explanation_builder.build_explanation(
            indicators=indicators,
            health_score=score_result.score,
            score_range=score_result.score_range,
            alerts=request.alerts,
        )

        inactivity_message = inactivity_result.get("message")
        if inactivity_message:
            explanations.append(inactivity_message)

        has_pending = await sync_to_async(_check_pending_outbox)(request.user_id)
        if has_pending:
            explanations.append(
                "New activity data has been detected. Please refresh your dashboard."
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
        raise HTTPException(
            status_code=400,
            detail=format_error_response(str(e)),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response(f"Internal server error: {str(e)}"),
        )
