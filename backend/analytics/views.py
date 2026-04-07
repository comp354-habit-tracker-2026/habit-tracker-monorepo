from analytics.presentation.views import AnalyticsOverviewView

__all__ = ["AnalyticsOverviewView"]

from django.http import JsonResponse
from analytics.team12.services import Team12AnalyticsService

service = Team12AnalyticsService()

# Made with the help of an LLM
def personal_record_view(request, habit_id):
    user = request.user
    metric_type = request.GET.get("metricType")

    try:
        result = service.personal_record_for_habit(user, habit_id, metric_type)

        if result is None:
            return JsonResponse(None, safe=False)

        return JsonResponse(result)

    except ValueError:
        return JsonResponse({"error": "Invalid metric type"}, status=400)