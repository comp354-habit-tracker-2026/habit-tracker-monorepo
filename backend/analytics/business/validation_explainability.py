# ============================================================
# G13 - MMingQwQ - Validation & Explainability
# ============================================================
from typing import Dict, Optional, List


# =========================
# Validation Logic
# =========================
def validate_explainability_inputs(
    indicators: Dict[str, Optional[float]],
    health_score: Optional[float],
    score_range: Optional[str],
    alerts: Optional[List[str]],
) -> None:
    """
    Validates inputs before explanation or response generation.
    Raises ValueError if invalid.
    """

    if not isinstance(indicators, dict):
        raise ValueError("Indicators must be a dictionary.")

    for key, value in indicators.items():
        if value is not None and not isinstance(value, (int, float)):
            raise ValueError(f"Indicator '{key}' must be numeric or None.")

    if health_score is not None:
        if not isinstance(health_score, (int, float)):
            raise ValueError("Health score must be numeric.")
        if not (0 <= health_score <= 100):
            raise ValueError("Health score must be between 0 and 100.")

    if alerts is not None and not isinstance(alerts, list):
        raise ValueError("Alerts must be a list of strings.")

    if alerts:
        for alert in alerts:
            if not isinstance(alert, str):
                raise ValueError("Each alert must be a string.")


# =========================
# Explainability Logic
# =========================
class ExplainabilityBuilder:
    """
    Builds human-readable explanations for health indicators.
    """

    def build_explanation(
        self,
        indicators: Dict[str, Optional[float]],
        health_score: Optional[float],
        score_range: Optional[str],
        alerts: Optional[List[str]],
    ) -> List[str]:

        explanations = []

        # Indicators explanation
        if indicators:
            for key, value in indicators.items():
                if value is None:
                    explanations.append(f"{key.capitalize()} data is missing.")
                else:
                    explanations.append(f"{key.capitalize()} value is {value}.")

        # Health score explanation
        if health_score is not None:
            explanations.append(f"Health score is {health_score}.")
            if score_range:
                explanations.append(f"Score range: {score_range}.")
        else:
            explanations.append("Health score could not be computed due to missing data.")

        # Alerts explanation
        if alerts:
            for alert in alerts:
                explanations.append(f"Alert: {alert}")

        return explanations


# =========================
# Error Formatting (Optional)
# =========================
def format_error_response(message: str) -> Dict[str, str]:
    """
    Standard error response format.
    """
    return {
        "status": "error",
        "message": message
    }


# =========================
# Success Formatting (Optional)
# =========================
def format_success_response(data: Dict) -> Dict:
    """
    Standard success response format.
    """
    return {
        "status": "success",
        "data": data
    }