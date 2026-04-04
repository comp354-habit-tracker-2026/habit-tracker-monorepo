from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase

from gamification.business.services import GamificationService
from gamification.models import Badge, Streak


# ---------------------------------------------------------------------------
# Helper to build mock objects
# ---------------------------------------------------------------------------

def _mock_activity(activity_type='running', distance=5.0, duration=30, calories=200, activity_date=None):
    activity = MagicMock()
    activity.activity_type = activity_type
    activity.distance = Decimal(str(distance))
    activity.duration = duration
    activity.calories = calories
    activity.date = activity_date or date.today()
    return activity


def _mock_badge(badge_type='single', activity_type='running', threshold=10, metric='distance', points=50):
    badge = Badge(
        pk=1,
        name='Test Badge',
        badge_type=badge_type,
        activity_type=activity_type,
        threshold=Decimal(str(threshold)),
        metric=metric,
        points=points,
    )
    return badge


# ---------------------------------------------------------------------------
# Streak tests
# ---------------------------------------------------------------------------

class StreakUpdateTest(TestCase):
    """Test streak update logic without hitting the database."""

    def _make_service(self, streak):
        service = GamificationService()
        service.streak_repo = MagicMock()
        service.streak_repo.get_or_create_streak.return_value = streak
        return service

    def test_first_activity_starts_streak_at_one(self):
        streak = Streak(current_count=0, longest_count=0, last_activity_date=None)
        service = self._make_service(streak)

        result = service.update_streak(user=MagicMock(), activity_date=date(2026, 3, 1))

        self.assertEqual(result.current_count, 1)
        self.assertEqual(result.longest_count, 1)
        self.assertEqual(result.last_activity_date, date(2026, 3, 1))

    def test_consecutive_day_increments_streak(self):
        streak = Streak(current_count=3, longest_count=5, last_activity_date=date(2026, 3, 1))
        service = self._make_service(streak)

        result = service.update_streak(user=MagicMock(), activity_date=date(2026, 3, 2))

        self.assertEqual(result.current_count, 4)
        self.assertEqual(result.longest_count, 5)  # not beaten yet

    def test_consecutive_day_updates_longest_when_beaten(self):
        streak = Streak(current_count=5, longest_count=5, last_activity_date=date(2026, 3, 5))
        service = self._make_service(streak)

        result = service.update_streak(user=MagicMock(), activity_date=date(2026, 3, 6))

        self.assertEqual(result.current_count, 6)
        self.assertEqual(result.longest_count, 6)

    def test_missed_day_resets_streak_to_one(self):
        streak = Streak(current_count=5, longest_count=5, last_activity_date=date(2026, 3, 1))
        service = self._make_service(streak)

        result = service.update_streak(user=MagicMock(), activity_date=date(2026, 3, 4))

        self.assertEqual(result.current_count, 1)
        self.assertEqual(result.longest_count, 5)  # longest preserved

    def test_same_day_activity_no_change(self):
        streak = Streak(current_count=3, longest_count=3, last_activity_date=date(2026, 3, 1))
        service = self._make_service(streak)

        result = service.update_streak(user=MagicMock(), activity_date=date(2026, 3, 1))

        self.assertEqual(result.current_count, 3)  # unchanged

    def test_missed_multiple_days_resets(self):
        streak = Streak(current_count=10, longest_count=10, last_activity_date=date(2026, 3, 1))
        service = self._make_service(streak)

        result = service.update_streak(user=MagicMock(), activity_date=date(2026, 3, 15))

        self.assertEqual(result.current_count, 1)
        self.assertEqual(result.longest_count, 10)


# ---------------------------------------------------------------------------
# Single badge tests
# ---------------------------------------------------------------------------

class SingleBadgeTest(TestCase):

    def test_earned_when_metric_exceeds_threshold(self):
        service = GamificationService()
        badge = _mock_badge(threshold=10, metric='distance', activity_type='running')
        activity = _mock_activity(activity_type='running', distance=12.0)

        self.assertTrue(service._check_single_badge(badge, activity))

    def test_earned_when_metric_equals_threshold(self):
        service = GamificationService()
        badge = _mock_badge(threshold=10, metric='distance')
        activity = _mock_activity(activity_type='running', distance=10.0)

        self.assertTrue(service._check_single_badge(badge, activity))

    def test_not_earned_below_threshold(self):
        service = GamificationService()
        badge = _mock_badge(threshold=10, metric='distance')
        activity = _mock_activity(activity_type='running', distance=5.0)

        self.assertFalse(service._check_single_badge(badge, activity))

    def test_not_earned_wrong_activity_type(self):
        service = GamificationService()
        badge = _mock_badge(threshold=10, metric='distance', activity_type='running')
        activity = _mock_activity(activity_type='cycling', distance=50.0)

        self.assertFalse(service._check_single_badge(badge, activity))

    def test_earned_any_activity_type_when_blank(self):
        service = GamificationService()
        badge = _mock_badge(threshold=5, metric='distance', activity_type='')
        activity = _mock_activity(activity_type='swimming', distance=10.0)

        self.assertTrue(service._check_single_badge(badge, activity))

    def test_duration_metric(self):
        service = GamificationService()
        badge = _mock_badge(threshold=60, metric='duration', activity_type='')
        activity = _mock_activity(duration=90)

        self.assertTrue(service._check_single_badge(badge, activity))

    def test_calories_metric(self):
        service = GamificationService()
        badge = _mock_badge(threshold=500, metric='calories', activity_type='')
        activity = _mock_activity(calories=600)

        self.assertTrue(service._check_single_badge(badge, activity))


# ---------------------------------------------------------------------------
# Cumulative badge tests
# ---------------------------------------------------------------------------

class CumulativeBadgeTest(TestCase):

    def _make_service(self, total_distance=0, total_duration=0, total_calories=0, total_activities=0):
        service = GamificationService()
        service.stats_repo = MagicMock()
        service.stats_repo.get_cumulative_stats.return_value = {
            'total_distance': total_distance,
            'total_duration': total_duration,
            'total_calories': total_calories,
            'total_activities': total_activities,
        }
        return service

    def test_cumulative_badge_earned(self):
        service = self._make_service(total_distance=150)
        badge = _mock_badge(badge_type='cumulative', threshold=100, metric='distance')

        self.assertTrue(service._check_cumulative_badge(MagicMock(), badge))

    def test_cumulative_badge_not_earned(self):
        service = self._make_service(total_distance=50)
        badge = _mock_badge(badge_type='cumulative', threshold=100, metric='distance')

        self.assertFalse(service._check_cumulative_badge(MagicMock(), badge))

    def test_cumulative_badge_exact_threshold(self):
        service = self._make_service(total_distance=100)
        badge = _mock_badge(badge_type='cumulative', threshold=100, metric='distance')

        self.assertTrue(service._check_cumulative_badge(MagicMock(), badge))

    def test_cumulative_badge_with_none_stats(self):
        service = GamificationService()
        service.stats_repo = MagicMock()
        service.stats_repo.get_cumulative_stats.return_value = {
            'total_distance': None,
        }
        badge = _mock_badge(badge_type='cumulative', threshold=100, metric='distance')

        self.assertFalse(service._check_cumulative_badge(MagicMock(), badge))


# ---------------------------------------------------------------------------
# Streak badge tests
# ---------------------------------------------------------------------------

class StreakBadgeTest(TestCase):

    def test_streak_badge_earned(self):
        service = GamificationService()
        service.streak_repo = MagicMock()
        streak = Streak(current_count=7, longest_count=7)
        service.streak_repo.get_or_create_streak.return_value = streak

        badge = _mock_badge(badge_type='streak', threshold=7)
        result = service._check_badge(MagicMock(), badge, _mock_activity())

        self.assertTrue(result)

    def test_streak_badge_not_earned(self):
        service = GamificationService()
        service.streak_repo = MagicMock()
        streak = Streak(current_count=3, longest_count=3)
        service.streak_repo.get_or_create_streak.return_value = streak

        badge = _mock_badge(badge_type='streak', threshold=7)
        result = service._check_badge(MagicMock(), badge, _mock_activity())

        self.assertFalse(result)


# ---------------------------------------------------------------------------
# Frequency badge tests
# ---------------------------------------------------------------------------

class FrequencyBadgeTest(TestCase):

    def _make_service(self, count_in_period):
        service = GamificationService()
        service.stats_repo = MagicMock()
        service.stats_repo.get_activity_count_in_period.return_value = count_in_period
        return service

    def test_frequency_badge_earned(self):
        service = self._make_service(count_in_period=3)
        badge = _mock_badge(badge_type='frequency', threshold=3, activity_type='running')
        activity = _mock_activity(activity_type='running', activity_date=date(2026, 3, 4))  # Wednesday

        self.assertTrue(service._check_frequency_badge(MagicMock(), badge, activity))

    def test_frequency_badge_not_enough(self):
        service = self._make_service(count_in_period=1)
        badge = _mock_badge(badge_type='frequency', threshold=3, activity_type='running')
        activity = _mock_activity(activity_type='running', activity_date=date(2026, 3, 4))

        self.assertFalse(service._check_frequency_badge(MagicMock(), badge, activity))

    def test_frequency_badge_wrong_activity_type(self):
        service = self._make_service(count_in_period=5)
        badge = _mock_badge(badge_type='frequency', threshold=3, activity_type='running')
        activity = _mock_activity(activity_type='cycling', activity_date=date(2026, 3, 4))

        self.assertFalse(service._check_frequency_badge(MagicMock(), badge, activity))

    def test_frequency_badge_any_type_when_blank(self):
        service = self._make_service(count_in_period=5)
        badge = _mock_badge(badge_type='frequency', threshold=5, activity_type='')
        activity = _mock_activity(activity_type='cycling', activity_date=date(2026, 3, 4))

        self.assertTrue(service._check_frequency_badge(MagicMock(), badge, activity))


# ---------------------------------------------------------------------------
# Full evaluate_badges integration (mocked repos)
# ---------------------------------------------------------------------------

class EvaluateBadgesTest(TestCase):

    def test_evaluate_awards_new_badge(self):
        service = GamificationService()
        badge = _mock_badge(badge_type='single', threshold=5, metric='distance')

        service.badge_repo = MagicMock()
        service.badge_repo.get_all_badges.return_value = [badge]
        service.badge_repo.has_badge.return_value = False
        service.badge_repo.award_badge.return_value = (MagicMock(), True)  # created=True

        activity = _mock_activity(activity_type='running', distance=10.0)
        result = service.evaluate_badges(MagicMock(), activity)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], badge)

    def test_evaluate_skips_already_earned(self):
        service = GamificationService()
        badge = _mock_badge(badge_type='single', threshold=5, metric='distance')

        service.badge_repo = MagicMock()
        service.badge_repo.get_all_badges.return_value = [badge]
        service.badge_repo.has_badge.return_value = True  # already earned

        activity = _mock_activity(activity_type='running', distance=10.0)
        result = service.evaluate_badges(MagicMock(), activity)

        self.assertEqual(len(result), 0)
        service.badge_repo.award_badge.assert_not_called()

    def test_evaluate_does_not_award_unmet_badge(self):
        service = GamificationService()
        badge = _mock_badge(badge_type='single', threshold=50, metric='distance')

        service.badge_repo = MagicMock()
        service.badge_repo.get_all_badges.return_value = [badge]
        service.badge_repo.has_badge.return_value = False

        activity = _mock_activity(activity_type='running', distance=5.0)
        result = service.evaluate_badges(MagicMock(), activity)

        self.assertEqual(len(result), 0)
        service.badge_repo.award_badge.assert_not_called()


# ---------------------------------------------------------------------------
# Milestone evaluation tests
# ---------------------------------------------------------------------------

class EvaluateMilestonesTest(TestCase):

    def _make_service(self, stats, has_milestone=False):
        service = GamificationService()
        service.stats_repo = MagicMock()
        service.stats_repo.get_cumulative_stats.return_value = stats
        service.milestone_repo = MagicMock()
        service.milestone_repo.get_all_milestones.return_value = [
            MagicMock(
                pk=1, name='100km', metric='total_distance',
                threshold=Decimal('100'), activity_type='', points=100,
            )
        ]
        service.milestone_repo.has_milestone.return_value = has_milestone
        service.milestone_repo.award_milestone.return_value = (MagicMock(), True)
        return service

    def test_milestone_reached(self):
        service = self._make_service({'total_distance': 150})
        result = service.evaluate_milestones(MagicMock())

        self.assertEqual(len(result), 1)

    def test_milestone_not_reached(self):
        service = self._make_service({'total_distance': 50})
        result = service.evaluate_milestones(MagicMock())

        self.assertEqual(len(result), 0)

    def test_milestone_already_reached(self):
        service = self._make_service({'total_distance': 150}, has_milestone=True)
        result = service.evaluate_milestones(MagicMock())

        self.assertEqual(len(result), 0)


# ---------------------------------------------------------------------------
# Signal tests
# ---------------------------------------------------------------------------

class SignalTest(TestCase):

    @patch('gamification.business.services.GamificationService')
    def test_signal_calls_evaluate_on_create(self, MockService):
        from gamification.signals import evaluate_achievements_on_activity

        mock_service = MockService.return_value
        mock_service.update_streak.return_value = Streak(current_count=1, longest_count=1)
        mock_service.evaluate_badges.return_value = []
        mock_service.evaluate_milestones.return_value = []

        activity = MagicMock()
        activity.user = MagicMock(pk=1)
        activity.date = date.today()

        evaluate_achievements_on_activity(
            sender=MagicMock(), instance=activity, created=True,
        )

        mock_service.update_streak.assert_called_once_with(activity.user, activity.date)
        mock_service.evaluate_badges.assert_called_once()
        mock_service.evaluate_milestones.assert_called_once()

    @patch('gamification.business.services.GamificationService')
    def test_signal_skips_on_update(self, MockService):
        from gamification.signals import evaluate_achievements_on_activity

        activity = MagicMock()

        evaluate_achievements_on_activity(
            sender=MagicMock(), instance=activity, created=False,
        )

        MockService.assert_not_called()


# ---------------------------------------------------------------------------
# get_activity_metric tests
# ---------------------------------------------------------------------------

class GetActivityMetricTest(TestCase):

    def test_returns_distance(self):
        activity = _mock_activity(distance=15.5)
        result = GamificationService._get_activity_metric(activity, 'distance')
        self.assertEqual(result, Decimal('15.5'))

    def test_returns_duration(self):
        activity = _mock_activity(duration=45)
        result = GamificationService._get_activity_metric(activity, 'duration')
        self.assertEqual(result, 45)

    def test_returns_calories(self):
        activity = _mock_activity(calories=350)
        result = GamificationService._get_activity_metric(activity, 'calories')
        self.assertEqual(result, 350)

    def test_returns_none_for_unknown_metric(self):
        activity = _mock_activity()
        result = GamificationService._get_activity_metric(activity, 'unknown')
        self.assertIsNone(result)
