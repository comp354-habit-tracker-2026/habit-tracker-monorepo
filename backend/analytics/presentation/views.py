from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.business import AnalyticsService

#team 13 and 14
from analytics.data.repositories import AnalyticsRepository

from dataclasses import dataclass
from datetime import date, timedelta
import logging
import random

from django.http import JsonResponse

from activities.models import Activity
from goals.models import Goal
from analytics.progress_series.models import DemoGoal, DemoActivity

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
