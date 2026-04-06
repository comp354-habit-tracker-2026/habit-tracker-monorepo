from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.business import AnalyticsService

#team 12
from analytics.team12.services import Team12AnalyticsService

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

class ActivityStatisticsView(APIView):
    def get(self, request):
        user = request.user

        service = Team12AnalyticsService()
        data = service.activity_statistics(user)

        return Response(data)


class PersonalRecordsView(APIView):
    def get(self, request):
        user = request.user
        service = Team12AnalyticsService()
        data = service.personal_records(user)
        return Response(data)


class ActivityTypeBreakdownView(APIView):
    def get(self, request):
        user = request.user
        service = Team12AnalyticsService()
        data = service.activity_type_breakdown(user)
        return Response(data)


class ActivityStreaksView(APIView):
    def get(self, request):
        user = request.user
        service = Team12AnalyticsService()
        data = service.activity_streaks(user)
        return Response(data)


class WeeklySummaryView(APIView):
    def get(self, request):
        user = request.user
        from_param = request.query_params.get("from")
        to_param = request.query_params.get("to")
        activity_type = request.query_params.get("activity_type")

        service = Team12AnalyticsService()
        data = service.weekly_summary(
            user=user,
            from_param=from_param,
            to_param=to_param,
            activity_type=activity_type,
        )

        return Response(data)

class HealthIndicatorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AnalyticsService()
        data = {
            "inactivity_evaluation": service.inactivity_evaluation(request.user),
        }
        return Response(data)
