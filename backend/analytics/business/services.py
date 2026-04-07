from core.business import BaseService
from analytics.data import AnalyticsRepository
from core.business.predict_model import predict


import numpy as np


class AnalyticsService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or AnalyticsRepository()

    def activity_statistics(self, user):
        return self.repository.activity_statistics(user)

    def trend_snapshot(self, user):
        return self.repository.trend_snapshot(user)

    def forecast_preview(self, user):
        #this info is to be changed when the dataset is connected, just hardcoded to be able to output
        X_last=np.array([1,2,3])
        return predict(X_last, horizon=3)
        #return self.repository.forecast_preview(user)
        
    def inactivity_evaluation(self, user):
        return self.repository.inactivity_evaluation(user)

    def predict_activity_status(self, user):
        signals = self.repository.activity_signal(user)

        probability = 0.0

        days_since_last = signals["days_since_last_activity"]
        if days_since_last is None:
            probability += 0.0
        elif days_since_last <= 3:
            probability += 0.45
        elif days_since_last <= 7:
            probability += 0.30
        elif days_since_last <= 14:
            probability += 0.15
        else:
            probability += 0.05

        weekly_sessions = signals["weekly_sessions"]
        if weekly_sessions >= 3:
            probability += 0.35
        elif weekly_sessions == 2:
            probability += 0.22
        elif weekly_sessions == 1:
            probability += 0.10

        weekly_minutes = signals["weekly_minutes"]
        if weekly_minutes >= 150:
            probability += 0.20
        elif weekly_minutes >= 90:
            probability += 0.12
        elif weekly_minutes >= 45:
            probability += 0.06

        probability = round(min(max(probability, 0.01), 0.99), 2)
        activity_score = int(round(probability * 100))
        is_active = probability >= 0.50

        if probability >= 0.75 or probability <= 0.25:
            confidence = "high"
        elif probability >= 0.60 or probability <= 0.40:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "is_active": is_active,
            "probability_active": probability,
            "activity_score": activity_score,
            "confidence": confidence,
            "signals": signals,
            "model": "heuristic_activity_classifier_v1",
        }

    def health_indicators(self, user, start_date, end_date, window="weekly"):
        aggregates = self.repository.activity_aggregates_for_window(user, start_date, end_date)

        total_minutes = aggregates["total_minutes"]
        total_distance_km = aggregates["total_distance_km"]
        active_days = aggregates["active_days"]
        window_days = aggregates["window_days"]
        inactivity_streak_days = aggregates["inactivity_streak_days"]

        consistency_ratio = round(active_days / window_days, 2) if window_days > 0 else 0.0

        volume_score = min(40, int(round((total_minutes / 300) * 40)))
        consistency_score = min(35, int(round(consistency_ratio * 35)))
        inactivity_score = max(0, 25 - (inactivity_streak_days * 3))

        health_score = max(0, min(100, volume_score + consistency_score + inactivity_score))

        inactive = inactivity_streak_days >= 3
        alert_reason = (
            f"No activity recorded for {inactivity_streak_days} day(s)." if inactive else None
        )

        explanations = [
            f"You were active on {active_days} out of {window_days} days.",
            f"Your {window} volume was {total_minutes} minutes.",
        ]

        if inactive:
            explanations.append(
                f"An inactivity alert was triggered: {alert_reason}"
            )
        else:
            explanations.append("No inactivity alert was triggered for this time window.")

        return {
            "userId": str(user.id),
            "window": window,
            "range": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat(),
            },
            "indicators": {
                "volume": {
                    "totalDurationMinutes": total_minutes,
                    "totalDistanceKm": total_distance_km,
                },
                "consistency": {
                    "activeDays": active_days,
                    "totalDays": window_days,
                },
            },
            "healthScore": health_score,
            "alerts": {
                "inactive": inactive,
                "reason": alert_reason,
            },
            "explanations": explanations,
        }

