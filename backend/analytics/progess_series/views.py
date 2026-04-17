from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import logging

from django.http import JsonResponse
from django.views import View

from activities.models import Activity
from goals.models import Goal
from .models import DemoGoal, DemoActivity

from analytics.progess_series.service import (
    InvalidGranularityError,
    ProgressSeriesError,
    UnsupportedGoalTypeError,
    get_cached_progress_series,
)

logger = logging.getLogger(__name__)

class GoalProgressSeriesView(View):
    """Return chart-ready goal progress data for the authenticated user."""

    def get(self, request, goal_id: int, *args, **kwargs):
        granularity = request.GET.get("granularity", "daily")
        provider = request.GET.get("provider") or None
        use_demo = request.GET.get("demo", "false").lower() == "true"

        try:
            if use_demo:
                # Demo mode is useful while wiring the frontend before real goal
                # records exist. It is intentionally isolated from DB reads.
                goal = DemoGoal(
                    id=1,
                    title="Run 20 km this week",
                    goal_type="distance",
                    target_value=20,
                    start_date=date(2026, 3, 1),
                    end_date=date(2026, 3, 7),
                    user_id=1,
                )
                activities = [
                    DemoActivity(date=date(2026, 3, 1), distance=2.5, user_id=1),
                    DemoActivity(date=date(2026, 3, 2), distance=3.5, user_id=1),
                    DemoActivity(date=date(2026, 3, 4), distance=4.0, user_id=1),
                ]
            else:
                # goal progress data.
                goal = Goal.objects.get(id=goal_id)
                activities = Activity.objects.filter(
                    account__user=goal.user,
                    date__gte=goal.start_date,
                    date__lte=goal.end_date,
                ).order_by("date")
                if provider:
                    activities = activities.filter(account__provider=provider)

            result = get_cached_progress_series(
                goal=goal,
                activities=activities,
                granularity=granularity,
                provider=provider,
            )
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
        except UnsupportedGoalTypeError as exc:
            return JsonResponse({"error": "Unsupported goal type for progress series."}, status=400)
        except ProgressSeriesError as exc:
            return JsonResponse({"error": "Unable to compute progress series."}, status=400)
        except Exception as exc:
            # Log unexpected errors server-side and avoid leaking internal details in responses.
            logger.exception("Unexpected error while generating goal progress series")
            return JsonResponse(
                {"error": "Unexpected server error."},
                status=500,
            )
