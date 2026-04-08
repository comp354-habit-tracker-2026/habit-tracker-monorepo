from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination


class SmallResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

from analytics.business import AnalyticsService

#team 12
from analytics.team12.services import Team12AnalyticsService

#team 13 and 14
from analytics.data.repositories import AnalyticsRepository

#team 15
from goals.business import GoalService

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
        data_from_service = service.inactivity_evaluation(request.user)
        data = {
            "days_since_last_activity": data_from_service.get("days_since_last_activity"),
            "inactive": data_from_service.get("inactive"),
            "severity": data_from_service.get("severity"),
        }
        return Response(data)
    
class HealthTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AnalyticsRepository()
        data = {
            "weekly_goal_completion":service.trend_snapshot(request.user), #currently no data yet
        }
               
        return Response(data)
    
class HealthForecastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AnalyticsRepository()
        data = {
            "next_week_prediction" : service.forecast_preview(request.user), #currently no data yet
        }
               
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

class GoalsAnalyticsSummaryView(APIView): #top level goals summary
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = GoalService()
        queryset = service.get_user_queryset(request.user, request.query_params)

        summaries = [service.get_status_summary(g) for g in queryset]

        data = {
            "totalGoals": len(summaries),
            "achieved": sum(1 for g in summaries if g["status"] == "ACHIEVED"),
            "onTrack": sum(1 for g in summaries if g["status"] == "ON_TRACK"),
            "atRisk": sum(1 for g in summaries if g["status"] == "AT_RISK"),
            "missed": sum(1 for g in summaries if g["status"] == "MISSED"),
            "averageCompletion": (
                sum(g["percentComplete"] for g in summaries) / len(summaries)
                if summaries else 0
            ),
        }

        return Response(data)

class AtRiskGoalsView(APIView): #returns goals that are at risk of being broken
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = GoalService()
        queryset = service.get_user_queryset(request.user, request.query_params)

        data = [
            s for g in queryset
            if (s := service.get_status_summary(g))["status"] == "AT_RISK"
        ]

        return Response({
            "count": len(data),
            "goals": data
        })

class GoalCompletionRateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = GoalService()
        queryset = service.get_user_queryset(request.user, request.query_params)

        summaries = [service.get_status_summary(g) for g in queryset]

        total = len(summaries)
        achieved = sum(1 for g in summaries if g["status"] == "ACHIEVED")

        return Response({
            "completionRate": (achieved / total * 100) if total else 0
        })

class GoalInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = GoalService()
        queryset = service.get_user_queryset(request.user, request.query_params)

        summaries = [service.get_status_summary(g) for g in queryset]

        at_risk = [g for g in summaries if g["status"] == "AT_RISK"]
        missed = [g for g in summaries if g["status"] == "MISSED"]

        insights = []

        if len(at_risk) > 0:
            insights.append(f"{len(at_risk)} goals are at risk")

        if len(missed) > 0:
            insights.append(f"{len(missed)} goals missed their deadline")

        if summaries:
            avg = sum(g["percentComplete"] for g in summaries) / len(summaries)
            if avg < 50:
                insights.append("Overall progress is below 50%")

        return Response({
            "insights": insights,
            "atRiskGoals": at_risk,
            "missedGoals": missed,
        })


# Class for paginated data (shortened data) for better organization
class PaginatedActivityHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Returns paginated list of user activities"""
        from analytics.repository import AnalyticsRepository
        
        service = AnalyticsRepository()
        
        # Get all activities (you may need to adjust this based on what's available)
        # If you don't have an actual activities table yet, use dummy data
        try:
            activities = service.get_user_activities(request.user)
        except:
            # Dummy data for demonstration
            activities = self._get_demo_activities()
        
        # Apply pagination
        paginator = SmallResultsPagination()
        page = paginator.paginate_queryset(activities, request)
        
        if page is not None:
            return paginator.get_paginated_response({
                "activities": page,
                "message": "Data exported in JSON format with pagination"
            })
        
        return Response({"activities": activities})
    
    def _get_demo_activities(self):
        """Temporary dummy data until other teams are done"""
        return [
            {"date": "2026-03-01", "activity_type": "Running", "distance_km": 5.2, "duration_min": 32},
            {"date": "2026-03-02", "activity_type": "Cycling", "distance_km": 15.0, "duration_min": 45},
            {"date": "2026-03-03", "activity_type": "Running", "distance_km": 7.5, "duration_min": 48},
            {"date": "2026-03-04", "activity_type": "Swimming", "distance_km": 1.2, "duration_min": 30},
            {"date": "2026-03-05", "activity_type": "Running", "distance_km": 10.0, "duration_min": 62},
            {"date": "2026-03-06", "activity_type": "Cycling", "distance_km": 20.0, "duration_min": 70},
            {"date": "2026-03-07", "activity_type": "Running", "distance_km": 4.0, "duration_min": 25},
            {"date": "2026-03-08", "activity_type": "Walking", "distance_km": 3.5, "duration_min": 45},
            {"date": "2026-03-09", "activity_type": "Running", "distance_km": 12.0, "duration_min": 75},
            {"date": "2026-03-10", "activity_type": "Cycling", "distance_km": 25.0, "duration_min": 90},
            {"date": "2026-03-11", "activity_type": "Running", "distance_km": 6.0, "duration_min": 38},
            {"date": "2026-03-12", "activity_type": "Swimming", "distance_km": 1.5, "duration_min": 35},
        ]