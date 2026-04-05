from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from django.http import JsonResponse
from django.views import View

from activities.models import Activity
from goals.models import Goal

from analytics.progess_series.service import (
    InvalidGranularityError,
    ProgressSeriesError,
    UnsupportedGoalTypeError,
    generate_progress_series,
)


@dataclass
class DemoGoal:
    id: int
    title: str
    goal_type: str
    target_value: float
    start_date: date
    end_date: date
    user_id: int


@dataclass
class DemoActivity:
    date: date
    distance: float = 0.0
    duration: float = 0.0
    calories: float = 0.0
    user_id: int = 1


class GoalProgressSeriesView(View):
    def get(self, request, goal_id: int, *args, **kwargs):
        granularity = request.GET.get("granularity", "daily")
        use_demo = request.GET.get("demo", "false").lower() == "true"

        try:
            if use_demo:
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
            return JsonResponse(result, status=200)

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

        except Exception as exc:
            return JsonResponse(
                {"error": "Unexpected server error.", "details": str(exc)},
                status=500,
            )