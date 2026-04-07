from datetime import date

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from analytics.business import AnalyticsService


class AnalyticsOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AnalyticsService()
        data = {
            "activity_statistics": service.activity_statistics(request.user),
            "trend_analysis": service.trend_snapshot(request.user),
            "forecast": service.forecast_preview(request.user),
            "active_status_prediction": service.predict_activity_status(request.user),
        }
        return Response(data)


class HealthIndicatorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id_raw = request.query_params.get("userId")
        window_raw = request.query_params.get("window", "weekly")
        from_raw = request.query_params.get("from")
        to_raw = request.query_params.get("to")

        errors = {}

        if user_id_raw is None:
            errors["userId"] = "This query parameter is required."
        if from_raw is None:
            errors["from"] = "This query parameter is required in YYYY-MM-DD format."
        if to_raw is None:
            errors["to"] = "This query parameter is required in YYYY-MM-DD format."

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = int(user_id_raw)
        except (TypeError, ValueError):
            return Response(
                {"errors": {"userId": "Must be an integer."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user_id != request.user.id:
            return Response(
                {"errors": {"userId": "You can only request your own indicators."}},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            start_date = date.fromisoformat(from_raw)
            end_date = date.fromisoformat(to_raw)
        except ValueError:
            return Response(
                {"errors": {"from_to": "Dates must be in YYYY-MM-DD format."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start_date > end_date:
            return Response(
                {"errors": {"from_to": "from must be earlier than or equal to to."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if window_raw not in {"daily", "weekly", "monthly"}:
            return Response(
                {"errors": {"window": "Must be one of: daily, weekly, monthly."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = AnalyticsService()
        data = service.health_indicators(request.user, start_date, end_date, window=window_raw)
        return Response(data)
