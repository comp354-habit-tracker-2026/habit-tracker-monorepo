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

    def delete_goal(self, goal_id: int, user):
        """
        Delete a goal by ID for the given user.
        Raises Goal.DoesNotExist if not found or not owned by user.
        """
        goal = Goal.objects.get(id=goal_id, user=user) # pylint: disable=no-member
        goal.delete()
