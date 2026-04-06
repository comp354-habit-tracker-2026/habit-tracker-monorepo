from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.business import AnalyticsService

#team 12
from analytics.team12.services import Team12AnalyticsService

#team 13 and 14
from analytics.data.repositories import AnalyticsRepository

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

#team 12
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

#team 13
class HealthIndicatorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AnalyticsRepository()
        data = service.activity_statistics(request.user),        
        return Response(data)
    
class InactivitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AnalyticsRepository()
        data = {
            "inactivity_evaluation": service.inactivity_evaluation(request.user),
        }
        return Response(data)
    
class HealthTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AnalyticsRepository()
        data = service.trend_snapshot(request.user),        
        return Response(data)
    
class HealthForecastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AnalyticsRepository()
        data = service.forecast_preview(request.user),        
        return Response(data)
    
#team 14
class ActivityForecastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AnalyticsRepository()     #placeholder service
        try:
            data = service.forecast_preview(request.user)   #placeholder call
            response_data = {
                "predictions": data.get("predictions", []),  #list of {date,predictedValue} obj
                "metadata": {
                    "methodUsed": request.query_params.get("method", "baseline"),
                    "windowK": request.query_params.get("windowK", 3),
                    "fallbackUsed": data.get("fallbackUsed", False),
                }
            }
            return Response(response_data)
        except Exception as e:
            return Response({"Forecasting Engine Error": str(e)}, status=500)


