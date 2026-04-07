from datetime import date, timedelta

from django.db.models import Sum, Count

from core.data import BaseRepository
from gamification.models import Badge, UserBadge, Streak, Milestone, UserMilestone


class BadgeRepository(BaseRepository):
    def __init__(self):
        super().__init__(Badge)

    def get_all_badges(self):
        return Badge.objects.all()

    def get_earned_badges(self, user):
        return UserBadge.objects.filter(user=user).select_related('badge')

    def has_badge(self, user, badge):
        return UserBadge.objects.filter(user=user, badge=badge).exists()

    def award_badge(self, user, badge):
        obj, created = UserBadge.objects.get_or_create(user=user, badge=badge)
        return obj, created


class StreakRepository(BaseRepository):
    def __init__(self):
        super().__init__(Streak)

    def get_or_create_streak(self, user):
        streak, _ = Streak.objects.get_or_create(user=user)
        return streak

    def save_streak(self, streak):
        streak.save()


class MilestoneRepository(BaseRepository):
    def __init__(self):
        super().__init__(Milestone)

    def get_all_milestones(self):
        return Milestone.objects.all()

    def get_reached_milestones(self, user):
        return UserMilestone.objects.filter(user=user).select_related('milestone')

    def has_milestone(self, user, milestone):
        return UserMilestone.objects.filter(user=user, milestone=milestone).exists()

    def award_milestone(self, user, milestone):
        obj, created = UserMilestone.objects.get_or_create(user=user, milestone=milestone)
        return obj, created


class ActivityStatsRepository:
    """Reads from the activities app to compute aggregate stats for a user."""

    def get_cumulative_stats(self, user, activity_type=None):
        from activities.models import Activity

        qs = Activity.objects.filter(user=user)
        if activity_type:
            qs = qs.filter(activity_type=activity_type)

        return qs.aggregate(
            total_distance=Sum('distance'),
            total_duration=Sum('duration'),
            total_calories=Sum('calories'),
            total_activities=Count('id'),
        )

    def get_active_dates(self, user, since=None):
        from activities.models import Activity

        qs = Activity.objects.filter(user=user)
        if since:
            qs = qs.filter(date__gte=since)

        return set(qs.values_list('date', flat=True).distinct())

    def get_activity_count_in_period(self, user, activity_type, start_date, end_date):
        from activities.models import Activity

        qs = Activity.objects.filter(user=user, date__gte=start_date, date__lte=end_date)
        if activity_type:
            qs = qs.filter(activity_type=activity_type)
        return qs.count()

    def get_single_activity_max(self, user, activity_type, metric):
        """Get the maximum value of a metric from any single activity."""
        from activities.models import Activity
        from django.db.models import Max

        qs = Activity.objects.filter(user=user)
        if activity_type:
            qs = qs.filter(activity_type=activity_type)

        result = qs.aggregate(max_val=Max(metric))
        return result['max_val'] or 0
