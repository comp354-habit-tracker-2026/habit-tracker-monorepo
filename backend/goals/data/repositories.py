from goals.models import Goal
from core.data import BaseRepository


class GoalRepository(BaseRepository):
    def __init__(self):
        super().__init__(Goal)

    def for_user(self, user):
        return self.model.objects.filter(user=user).order_by("-created_at")

    def apply_filters(self, queryset, params):
        status = params.get("status")
        goal_type = params.get("goal_type")
        start_date_from = params.get("start_date_from")
        end_date_to = params.get("end_date_to")

        if status:
            queryset = queryset.filter(status=status)
        if goal_type:
            queryset = queryset.filter(goal_type=goal_type)
        if start_date_from:
            queryset = queryset.filter(start_date__gte=start_date_from)
        if end_date_to:
            queryset = queryset.filter(end_date__lte=end_date_to)

        return queryset
