from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from django.http import JsonResponse
from django.views import View

from activities.models import Activity
from goals.models import Goal
from .models import DemoGoal, DemoActivity

from analytics.progess_series.service import (
    InvalidGranularityError,
    ProgressSeriesError,
    UnsupportedGoalTypeError,
    generate_progress_series,
)

class GoalProgressSeriesView(View):
    """Return chart-ready goal progress data for the authenticated user."""

    def get(self, request, goal_id: int, *args, **kwargs):
        granularity = request.GET.get("granularity", "daily").strip().lower()
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
                    user=goal.user,
                    date__gte=goal.start_date,
                    date__lte=goal.end_date,
                ).order_by("date")

            result = generate_progress_series(
                goal=goal,
                activities=activities,
                granularity=granularity,
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
            return JsonResponse({"error": str(exc)}, status=400)
        except UnsupportedGoalTypeError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        except ProgressSeriesError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        except Exception:
            # Avoid leaking internal exception details in production responses.
            return JsonResponse(
                {"error": "Unexpected server error."},
                status=500,
            )
