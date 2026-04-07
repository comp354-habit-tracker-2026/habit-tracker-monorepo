from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.business import AnalyticsService


class AnalyticsOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AnalyticsService()
        data = {
            "activity_statistics": service.activity_statistics(request.user),
            "trend_analysis": service.trend_snapshot(request.user),
            "forecast": service.forecast_preview(request.user),
        }
        return Response(data)

# ============================================================
# G13 - cathytham - InactivityDetector - PR #241
# ============================================================
class HealthIndicatorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_service(self):
        """Returns analytics service instance."""
        return AnalyticsService()

    def get(self, request):
        """Returns inactivity-related health indicators."""
        service = self.get_service()
        data = {
            "activity_statistics": service.activity_statistics(request.user),
            "inactivity_evaluation": service.inactivity_evaluation(request.user),
        }
        return Response(data)
