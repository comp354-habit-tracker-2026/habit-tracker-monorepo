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
    
# ============================================================
# G13 - FadyRizkalla - Health Score Model - PR #296
# ============================================================

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class HealthScoreResult:
    """Stores the final health score response."""
    score: Optional[float]
    score_range: str
    explanation: str


class HealthScoreModel:
    """
    Combines indicators into a final health score.
    Handles missing data by reweighting available indicators.
    """

    DEFAULT_WEIGHTS = {
        "volume": 0.4,
        "consistency": 0.4,
        "inactive": 0.2,  # penalty-style indicator
    }

    def compute_health_score(self, indicators: Dict[str, Optional[float]]) -> HealthScoreResult:
        """
        Compute a health score from available indicators.

        Expected indicator keys:
        - volume: float
        - consistency: float
        - inactive: 0 or 1
        - days_since_last_activity: optional extra info

        Missing indicators are ignored and remaining weights are rebalanced.
        """
        available = {}

        for key, weight in self.DEFAULT_WEIGHTS.items():
            value = indicators.get(key)
            if value is not None:
                available[key] = value

        if not available:
            return HealthScoreResult(
                score=None,
                score_range="No Score",
                explanation="No sufficient data available to compute health score."
            )

        # Reweight available indicators
        total_weight = sum(self.DEFAULT_WEIGHTS[key] for key in available)
        normalized_weights = {
            key: self.DEFAULT_WEIGHTS[key] / total_weight
            for key in available
        }

        # Normalize each indicator to 0-100
        score_components = {}

        if "volume" in available:
            # Example: cap volume at 600 for max score
            volume_score = min((available["volume"] / 600) * 100, 100)
            score_components["volume"] = volume_score

        if "consistency" in available:
            # Assume consistency already comes as 0-100
            consistency_score = max(0, min(available["consistency"], 100))
            score_components["consistency"] = consistency_score

        if "inactive" in available:
            # inactivity is penalty style: inactive=1 means low score
            inactive_score = 0 if available["inactive"] == 1 else 100
            score_components["inactive"] = inactive_score

        final_score = 0
        for key, component_score in score_components.items():
            final_score += component_score * normalized_weights[key]

        final_score = round(final_score, 1)
        score_range = self._get_score_range(final_score)
        explanation = self._build_explanation(score_components, final_score)

        return HealthScoreResult(
            score=final_score,
            score_range=score_range,
            explanation=explanation,
        )

    def _get_score_range(self, score: float) -> str:
        """Return score category label."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Low"

    def _build_explanation(self, score_components: Dict[str, float], final_score: float) -> str:
        """Build a short explanation for the computed score."""
        used_parts = ", ".join(score_components.keys())
        return f"Health score computed from: {used_parts}. Final score = {final_score}."