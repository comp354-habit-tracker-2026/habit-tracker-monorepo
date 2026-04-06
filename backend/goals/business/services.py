from decimal import Decimal
from goals.models import Goal
from core.business import BaseService
from goals.data import GoalRepository


class GoalService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or GoalRepository()

    def get_user_queryset(self, user, params):
        queryset = self.repository.for_user(user)
        return self.repository.apply_filters(queryset, params)

    @staticmethod
    def progress_percentage(current_value, target_value):
        if target_value and target_value > 0:
            return min(Decimal("100"), (current_value / target_value) * 100)
        return Decimal("0")

    def delete_goal(self, goal_id, user):
        if not str(goal_id).isdigit():
            return "invalid_id"
        goal = Goal.objects.filter(id=goal_id).first()  # pylint: disable=no-member
        if goal is None:
            return "not_found"
        if goal.user != user:
            return "forbidden"
        goal.delete()
        return "deleted"

    def update_goal(self, goal_id, user, data):
        if not str(goal_id).isdigit():
            return "invalid_id"
        goal = Goal.objects.filter(id=goal_id).first()  # pylint: disable=no-member
        if goal is None:
            return "not_found"
        if goal.user != user:
            return "forbidden"
        allowed_fields = [
            "title",
            "description",
            "goal_type",
            "status",
            "current_value",
            "target_value",
            "start_date",
            "end_date",
        ]
        for field in allowed_fields:
            if field in data:
                setattr(goal, field, data[field])
        goal.save()
        return goal