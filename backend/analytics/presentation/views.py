from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.business import AnalyticsService

#team 13 and 14
from analytics.data.repositories import AnalyticsRepository

#team 12
from analytics.team12.services import Team12AnalyticsService

#team 15
from goals.business import GoalService

from dataclasses import dataclass
from datetime import date, timedelta
import logging
import random

from django.http import JsonResponse

from activities.models import Activity
from goals.models import Goal
from analytics.progress_series.models import DemoGoal, DemoActivity

import logging
logger = logging.getLogger(__name__)

from analytics.progress_series.service import (
    InvalidGranularityError,
    InvalidPaginationError,
    ProgressSeriesError,
    UnsupportedGoalTypeError,
    generate_progress_series,
    paginate_points,
)

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


# ============================================================
# G13 - cathytham - InactivityDetector - PR #241
# ============================================================
class HealthIndicatorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AnalyticsService()
        return Response({
            "activity_statistics": service.activity_statistics(request.user),
            "inactivity_evaluation": service.inactivity_evaluation(request.user),
        })
    #team 13
    
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
        except Exception:
            logger.exception("Error while generating activity forecast")
            return Response(
                {"Forecasting Engine Error": "An internal error occurred while generating the activity forecast."},
                status=500,
            )

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
        """Returns paginated list of user activities with filtering"""
        
        # Get filters from query params
        activity_type = request.query_params.get('activity_type')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        from analytics.repository import AnalyticsRepository
        
        service = AnalyticsRepository()
        
        try:
            activities = service.get_user_activities(request.user)
        except:
            # Dummy data for demonstration
            activities = self._get_demo_activities()
        
        # Apply filters
        if activity_type:
            activities = [a for a in activities if a.get('activity_type') == activity_type]
        if start_date:
            activities = [a for a in activities if a.get('date') >= start_date]
        if end_date:
            activities = [a for a in activities if a.get('date') <= end_date]
        
        # Apply pagination
        paginator = SmallResultsPagination()
        page = paginator.paginate_queryset(activities, request)
        
        if page is not None:
            return paginator.get_paginated_response({
                "activities": page,
                "filters_applied": {
                    "activity_type": activity_type,
                    "start_date": start_date,
                    "end_date": end_date
                }
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
    
class GoalProgressSeriesView(APIView):
    """Return chart-ready goal progress data for the authenticated user."""

    permission_classes = [IsAuthenticated]
    
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 30
    MAX_PAGE_SIZE = 100

    def get(self, request, goal_id: int, *args, **kwargs):
        granularity = request.GET.get("granularity", "daily")
        use_demo = request.GET.get("demo", "false").lower() == "true"

        try:
            page = int(request.GET.get("page", self.DEFAULT_PAGE))
            page_size = int(request.GET.get("page_size", self.DEFAULT_PAGE_SIZE))
            page_size = min(page_size, self.MAX_PAGE_SIZE)
            

            if use_demo:
                goal = DemoGoal(
                    id=1,
                    title="Run 500 km over 6 months",
                    goal_type="distance",
                    target_value=500,
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 6, 30),  # 180 days → for pagination testing
                    user_id=1,
                )

                activities = []
                current_date = goal.start_date

                while current_date <= goal.end_date:
                    # Simulate realistic behavior:
                    # - some days have activity
                    # - some days don't
                    if random.random() > 0.3:  # 70% active days
                        activities.append(
                            DemoActivity(
                                date=current_date,
                                distance=round(random.uniform(1.0, 10.0), 2),
                                user_id=1,
                            )
                        )

                    current_date += timedelta(days=1)
            else:
                # goal progress data.
                goal = Goal.objects.get(id=goal_id)
                activities = Activity.objects.filter(
                    user=goal.user,
                    date__gte=goal.start_date,
                    date__lte=goal.end_date,
                ).order_by("date")

            result = generate_progress_series(
                goal=goal,
                activities=activities,
                granularity=granularity,
            )

            paginated_points, pagination = paginate_points(
                result.points,
                page=page,
                page_size=page_size,
            )
            result.points = paginated_points
            result.pagination = pagination

            return JsonResponse(result.to_dict(), status=200)

        except Goal.DoesNotExist:
            return JsonResponse(
                {
                    "error": "Goal not found.",
                    "hint": "Try adding ?demo=true to test the endpoint."
                },
                status=404,
            )
        except InvalidGranularityError as exc:
            return JsonResponse({"error": "Invalid granularity parameter."}, status=400)
        except InvalidPaginationError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        except UnsupportedGoalTypeError as exc:
            return JsonResponse({"error": "Unsupported goal type for progress series."}, status=400)
        except ProgressSeriesError as exc:
            return JsonResponse({"error": "Unable to compute progress series."}, status=400)
        except Exception as exc:
            return JsonResponse(
                {"error": "Unexpected server error."},
                status=500,
            )
