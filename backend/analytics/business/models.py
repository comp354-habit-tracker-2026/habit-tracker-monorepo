# This file defines the data models for the Forecast API using Pydantic.
# These models are used for request validation and response formatting in the API endpoints.
# The ForecastRequest model captures the input parameters for generating a forecast, while the ForecastResponse model structures 
# the output of the forecast along with relevant metrics.
# The ForecastPoint model represents individual forecasted data points, and the Metrics model encapsulates performance metrics for the forecast.
# Note: The actual forecasting logic is not implemented in this file; it serves solely as a definition of the data structures used in the API.

from pydantic import BaseModel
from typing import List, Optional

# The ForecastRequest model captures the input parameters for generating a forecast, including the user ID, the number of days to forecast, and the type of forecast (baseline or trained).
class ForecastRequest(BaseModel):
    userID: str
    numOfDays: int
    forecastType: Optional[str] = "baseline"

# The ForecastPoint model represents a single point in the forecast, containing the date and the predicted value for that date.
class ForecastPoint(BaseModel):
    date: str
    predictedValue: float

# The Metrics model captures the performance metrics of the forecast, such as Mean Absolute Error (MAE) and Root Mean Square Error (RMSE).
class Metrics(BaseModel):
    mae: float
    rmse: float

# The ForecastResponse model structures the output of the forecast, including the user ID, the type of forecast, the list of forecasted points, and the associated performance metrics.
class ForecastResponse(BaseModel):
    userID: str
    forecastType: str
    forecast: List[ForecastPoint]
    metrics: Metrics