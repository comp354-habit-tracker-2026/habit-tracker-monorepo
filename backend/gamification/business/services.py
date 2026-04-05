from datetime import date, timedelta
from decimal import Decimal

from core.business import BaseService
from gamification.data.repositories import (
    BadgeRepository,
    StreakRepository,
    MilestoneRepository,
    ActivityStatsRepository,
)


class GamificationService(BaseService):
    def __init__(self, badge_repo=None, streak_repo=None, milestone_repo=None, stats_repo=None):
        self.badge_repo = badge_repo or BadgeRepository()
        self.streak_repo = streak_repo or StreakRepository()
        self.milestone_repo = milestone_repo or MilestoneRepository()
        self.stats_repo = stats_repo or ActivityStatsRepository()

    # ------------------------------------------------------------------
    # Badge evaluation
    # ------------------------------------------------------------------

    def evaluate_badges(self, user, activity):
        """Check all badge rules against the user's activity. Returns list of newly earned badges."""
        newly_earned = []
        badges = self.badge_repo.get_all_badges()

        for badge in badges:
            if self.badge_repo.has_badge(user, badge):
                continue

            if self._check_badge(user, badge, activity):
                _, created = self.badge_repo.award_badge(user, badge)
                if created:
                    newly_earned.append(badge)

        return newly_earned

    def _check_badge(self, user, badge, activity):
        if badge.badge_type == 'single':
            return self._check_single_badge(badge, activity)
        elif badge.badge_type == 'cumulative':
            return self._check_cumulative_badge(user, badge)
        elif badge.badge_type == 'streak':
            streak = self.streak_repo.get_or_create_streak(user)
            return streak.current_count >= badge.threshold
        elif badge.badge_type == 'frequency':
            return self._check_frequency_badge(user, badge, activity)
        return False

    def _check_single_badge(self, badge, activity):
        if badge.activity_type and activity.activity_type != badge.activity_type:
            return False

        value = self._get_activity_metric(activity, badge.metric)
        return value is not None and value >= badge.threshold

    def _check_cumulative_badge(self, user, badge):
        stats = self.stats_repo.get_cumulative_stats(
            user,
            activity_type=badge.activity_type or None,
        )
        value = stats.get(f"total_{badge.metric}") or 0
        return value >= badge.threshold

    def _check_frequency_badge(self, user, badge, activity):
        """Check frequency badges like 'cycle 3x this week'.

        For frequency badges:
        - metric = 'count' (number of activities)
        - threshold = required count (e.g. 3)
        - The check looks at the current ISO week of the activity.
        """
        if badge.activity_type and activity.activity_type != badge.activity_type:
            return False

        # Calculate the current week boundaries
        activity_date = activity.date
        week_start = activity_date - timedelta(days=activity_date.weekday())  # Monday
        week_end = week_start + timedelta(days=6)  # Sunday

        count = self.stats_repo.get_activity_count_in_period(
            user,
            badge.activity_type or None,
            week_start,
            week_end,
        )
        return count >= badge.threshold

    @staticmethod
    def _get_activity_metric(activity, metric):
        metric_map = {
            'distance': activity.distance,
            'duration': activity.duration,
            'calories': activity.calories,
        }
        return metric_map.get(metric)

    # ------------------------------------------------------------------
    # Streak tracking
    # ------------------------------------------------------------------

    def update_streak(self, user, activity_date):
        """Update the user's streak based on a new activity date. Returns the updated Streak."""
        streak = self.streak_repo.get_or_create_streak(user)

        if streak.last_activity_date == activity_date:
            return streak

        if streak.last_activity_date == activity_date - timedelta(days=1):
            streak.current_count += 1
        elif streak.last_activity_date is None or streak.last_activity_date < activity_date - timedelta(days=1):
            streak.current_count = 1

        streak.last_activity_date = activity_date
        streak.longest_count = max(streak.longest_count, streak.current_count)
        self.streak_repo.save_streak(streak)

        return streak

    def get_streak(self, user):
        return self.streak_repo.get_or_create_streak(user)

    # ------------------------------------------------------------------
    # Milestone evaluation
    # ------------------------------------------------------------------

    def evaluate_milestones(self, user):
        """Check all milestones against user's cumulative stats. Returns newly reached milestones."""
        newly_reached = []
        milestones = self.milestone_repo.get_all_milestones()

        for milestone in milestones:
            if self.milestone_repo.has_milestone(user, milestone):
                continue

            stats = self.stats_repo.get_cumulative_stats(
                user,
                activity_type=milestone.activity_type or None,
            )
            value = stats.get(milestone.metric) or 0

            if value >= milestone.threshold:
                _, created = self.milestone_repo.award_milestone(user, milestone)
                if created:
                    newly_reached.append(milestone)

        return newly_reached

    # ------------------------------------------------------------------
    # Progress tracking
    # ------------------------------------------------------------------

    def get_badge_progress(self, user):
        """Return progress towards all unearned badges."""
        badges = self.badge_repo.get_all_badges()
        earned_ids = set(
            self.badge_repo.get_earned_badges(user).values_list('badge_id', flat=True)
        )
        streak = self.streak_repo.get_or_create_streak(user)
        progress = []

        for badge in badges:
            is_earned = badge.pk in earned_ids
            current_value = Decimal('0')

            if not is_earned:
                current_value = self._get_badge_current_value(user, badge, streak)

            pct = min(Decimal('100'), (current_value / badge.threshold * 100)) if badge.threshold else Decimal('0')

            progress.append({
                'badge': badge,
                'earned': is_earned,
                'current_value': current_value,
                'target_value': badge.threshold,
                'progress_percentage': pct,
            })

        return progress

    def _get_badge_current_value(self, user, badge, streak):
        if badge.badge_type == 'single':
            val = self.stats_repo.get_single_activity_max(
                user, badge.activity_type or None, badge.metric,
            )
            return Decimal(str(val))

        elif badge.badge_type == 'cumulative':
            stats = self.stats_repo.get_cumulative_stats(
                user, activity_type=badge.activity_type or None,
            )
            val = stats.get(f"total_{badge.metric}") or 0
            return Decimal(str(val))

        elif badge.badge_type == 'streak':
            return Decimal(str(streak.current_count))

        elif badge.badge_type == 'frequency':
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            count = self.stats_repo.get_activity_count_in_period(
                user, badge.activity_type or None, week_start, week_end,
            )
            return Decimal(str(count))

        return Decimal('0')

    def get_milestone_progress(self, user):
        """Return progress towards all milestones."""
        milestones = self.milestone_repo.get_all_milestones()
        reached_ids = set(
            self.milestone_repo.get_reached_milestones(user).values_list('milestone_id', flat=True)
        )
        progress = []

        for milestone in milestones:
            is_reached = milestone.pk in reached_ids
            current_value = Decimal('0')

            if not is_reached:
                stats = self.stats_repo.get_cumulative_stats(
                    user, activity_type=milestone.activity_type or None,
                )
                current_value = Decimal(str(stats.get(milestone.metric) or 0))

            pct = min(Decimal('100'), (current_value / milestone.threshold * 100)) if milestone.threshold else Decimal('0')

            progress.append({
                'milestone': milestone,
                'reached': is_reached,
                'current_value': current_value,
                'target_value': milestone.threshold,
                'progress_percentage': pct,
            })

        return progress

    # ------------------------------------------------------------------
    # Summary for frontend
    # ------------------------------------------------------------------

    def get_user_summary(self, user):
        """Return a complete gamification summary for a user."""
        streak = self.streak_repo.get_or_create_streak(user)
        earned_badges = self.badge_repo.get_earned_badges(user)
        reached_milestones = self.milestone_repo.get_reached_milestones(user)
        all_badges = self.badge_repo.get_all_badges()
        all_milestones = self.milestone_repo.get_all_milestones()

        total_points = (
            sum(ub.badge.points for ub in earned_badges)
            + sum(um.milestone.points for um in reached_milestones)
        )

        return {
            'streak': streak,
            'earned_badges': earned_badges,
            'reached_milestones': reached_milestones,
            'total_badges': all_badges.count(),
            'total_milestones': all_milestones.count(),
            'total_points': total_points,
        }
