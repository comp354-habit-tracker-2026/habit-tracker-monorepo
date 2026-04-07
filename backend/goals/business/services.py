from decimal import Decimal

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

    def getGoalProgress(self, pk, user):
        try:
            goal = Goal.objects.get(pk=pk)
        except Goal.DoesNotExist:
            return "not_found"
        except (ValueError, TypeError):
            return "invalid_id"

        if goal.user != user:
            return "forbidden"

        # Calculating progress as percentage
        if goal.target_value and goal.target_value > 0:
            percent = round((goal.current_value / goal.target_value) * 100, 1)
        else:
            percent = 0.0
    
        # Determining if on track 
        today = date.today()
        days_remaining = (goal.end_date - today).days if goal.end_date else None

        on_track = False
        summary = "No end date set."

        if goal.end_date and goal.start_date:
            total_days = (goal.end_date - goal.start_date).days
            elapsed_days = (today - goal.start_date).days
            if total_days > 0:
                expected_percent = round((elapsed_days / total_days) * 100, 1)
                on_track = percent >= expected_percent
                if percent >= 100:
                    summary = "Goal complete!"
                elif on_track:
                    summary = f"On track! {percent}% done, {days_remaining} days remaining."
                else:
                    summary = f"Behind schedule. {percent}% done but {expected_percent}% is expected by now."

        return {
            "current_value": goal.current_value,
            "target_value": goal.target_value,
            "percent_complete": percent,
            "on_track": on_track,
            "days_remaining": days_remaining,
            "summary": summary,
        }
