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