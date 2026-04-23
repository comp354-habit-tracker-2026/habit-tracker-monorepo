# Generated with assistance from Claude (Anthropic LLM)
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase

from activities.models import ConnectedAccount
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
        activity.account.user = MagicMock(pk=1)
        activity.date = date.today()

        evaluate_achievements_on_activity(
            sender=MagicMock(), instance=activity, created=True,
        )

        mock_service.update_streak.assert_called_once_with(activity.account.user, activity.date)
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


# ---------------------------------------------------------------------------
# API / Integration tests – covers viewsets, serializers, URLs
# ---------------------------------------------------------------------------

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class BadgeAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        self.badge = Badge.objects.create(
            name='Test Badge', badge_type='single', activity_type='running',
            threshold=Decimal('10'), metric='distance', points=50,
        )

    def test_list_badges(self):
        response = self.client.get('/api/v1/gamification/badges/')
        self.assertEqual(response.status_code, 200)
        # Response may be paginated (dict with 'results') or a plain list
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertGreaterEqual(len(results), 1)

    def test_list_badges_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/gamification/badges/')
        self.assertEqual(response.status_code, 401)

    def test_earned_badges_empty(self):
        response = self.client.get('/api/v1/gamification/badges/earned/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_earned_badges_with_badge(self):
        from gamification.models import UserBadge
        UserBadge.objects.create(user=self.user, badge=self.badge)
        response = self.client.get('/api/v1/gamification/badges/earned/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['badge']['name'], 'Test Badge')

    def test_badge_progress(self):
        response = self.client.get('/api/v1/gamification/badges/progress/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class MilestoneAPITest(TestCase):

    def setUp(self):
        from gamification.models import Milestone
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser2', email='test2@test.com', password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        self.milestone = Milestone.objects.create(
            name='Test Milestone', metric='total_distance',
            threshold=Decimal('100'), points=100,
        )

    def test_list_milestones(self):
        response = self.client.get('/api/v1/gamification/milestones/')
        self.assertEqual(response.status_code, 200)
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertGreaterEqual(len(results), 1)

    def test_reached_milestones_empty(self):
        response = self.client.get('/api/v1/gamification/milestones/reached/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_milestone_progress(self):
        response = self.client.get('/api/v1/gamification/milestones/progress/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class StreakAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser3', email='test3@test.com', password='testpass123',
        )
        self.client.force_authenticate(user=self.user)

    def test_get_streak(self):
        response = self.client.get('/api/v1/gamification/streaks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['current_count'], 0)
        self.assertEqual(response.data['longest_count'], 0)


class SummaryAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser4', email='test4@test.com', password='testpass123',
        )
        self.client.force_authenticate(user=self.user)

    def test_get_summary(self):
        response = self.client.get('/api/v1/gamification/summary/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_points', response.data)
        self.assertIn('streak', response.data)
        self.assertIn('earned_badges', response.data)
        self.assertIn('reached_milestones', response.data)

    def test_summary_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/gamification/summary/')
        self.assertEqual(response.status_code, 401)


class EvaluateAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser5', email='test5@test.com', password='testpass123',
        )
        self.account = ConnectedAccount.objects.create(
            user=self.user, provider='strava', external_user_id='eval_ext',
        )
        self.client.force_authenticate(user=self.user)

    def test_evaluate_no_activities(self):
        response = self.client.post('/api/v1/gamification/evaluate/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'No activities found for user')

    def test_evaluate_bad_activity_id(self):
        response = self.client.post('/api/v1/gamification/evaluate/', {'activity_id': 99999}, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Activity not found')

    def test_evaluate_with_activity(self):
        from activities.models import Activity
        activity = Activity.objects.create(
            account=self.account, activity_type='running',
            duration=30, date=date.today(),
            distance=Decimal('5.00'),
        )
        response = self.client.post('/api/v1/gamification/evaluate/', {'activity_id': activity.pk}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('streak', response.data)
        self.assertIn('new_badges', response.data)
        self.assertIn('new_milestones', response.data)


class SerializerTest(TestCase):

    def test_badge_serializer(self):
        from gamification.serializers import BadgeSerializer
        badge = Badge.objects.create(
            name='Ser Badge', badge_type='single', activity_type='',
            threshold=Decimal('5'), metric='distance', points=10,
        )
        data = BadgeSerializer(badge).data
        self.assertEqual(data['name'], 'Ser Badge')
        self.assertEqual(data['points'], 10)

    def test_streak_serializer(self):
        from gamification.serializers import StreakSerializer
        user = User.objects.create_user(username='seruser', email='s@t.com', password='p')
        streak = Streak.objects.create(user=user, current_count=5, longest_count=10)
        data = StreakSerializer(streak).data
        self.assertEqual(data['current_count'], 5)
        self.assertEqual(data['longest_count'], 10)

    def test_milestone_serializer(self):
        from gamification.serializers import MilestoneSerializer
        from gamification.models import Milestone
        ms = Milestone.objects.create(
            name='Ser MS', metric='total_distance',
            threshold=Decimal('50'), points=25,
        )
        data = MilestoneSerializer(ms).data
        self.assertEqual(data['name'], 'Ser MS')
        self.assertEqual(data['points'], 25)


# ---------------------------------------------------------------------------
# Seed command tests
# ---------------------------------------------------------------------------

from django.core.management import call_command
from io import StringIO


class SeedGamificationTest(TestCase):

    def test_seed_creates_badges_and_milestones(self):
        out = StringIO()
        call_command('seed_gamification', stdout=out)
        output = out.getvalue()
        self.assertIn('Seeded', output)
        self.assertGreater(Badge.objects.count(), 0)
        from gamification.models import Milestone
        self.assertGreater(Milestone.objects.count(), 0)

    def test_seed_is_idempotent(self):
        call_command('seed_gamification', stdout=StringIO())
        count1 = Badge.objects.count()
        call_command('seed_gamification', stdout=StringIO())
        count2 = Badge.objects.count()
        self.assertEqual(count1, count2)

    def test_seed_clear_flag(self):
        call_command('seed_gamification', stdout=StringIO())
        out = StringIO()
        call_command('seed_gamification', '--clear', stdout=out)
        self.assertIn('Cleared', out.getvalue())


# ---------------------------------------------------------------------------
# views.py re-export coverage
# ---------------------------------------------------------------------------

class ViewsReExportTest(TestCase):

    def test_views_exports_all_viewsets(self):
        from gamification import views
        self.assertTrue(hasattr(views, 'BadgeViewSet'))
        self.assertTrue(hasattr(views, 'MilestoneViewSet'))
        self.assertTrue(hasattr(views, 'StreakViewSet'))
        self.assertTrue(hasattr(views, 'SummaryViewSet'))
        self.assertTrue(hasattr(views, 'EvaluateViewSet'))


# ---------------------------------------------------------------------------
# Model __str__ tests (covers models.py lines 48, 67, 85, 117, 136)
# ---------------------------------------------------------------------------

class ModelStrTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='struser', email='str@test.com', password='testpass123',
        )

    def test_badge_str(self):
        badge = Badge.objects.create(
            name='Str Badge', badge_type='single',
            threshold=Decimal('10'), metric='distance',
        )
        self.assertEqual(str(badge), 'Str Badge')

    def test_user_badge_str(self):
        from gamification.models import UserBadge
        badge = Badge.objects.create(
            name='UB Badge', badge_type='single',
            threshold=Decimal('10'), metric='distance',
        )
        ub = UserBadge.objects.create(user=self.user, badge=badge)
        self.assertIn('UB Badge', str(ub))

    def test_streak_str(self):
        streak = Streak.objects.create(user=self.user, current_count=5, longest_count=10)
        self.assertIn('5 day streak', str(streak))

    def test_milestone_str(self):
        from gamification.models import Milestone
        ms = Milestone.objects.create(
            name='MS Str', metric='total_distance',
            threshold=Decimal('100'),
        )
        self.assertEqual(str(ms), 'MS Str')

    def test_user_milestone_str(self):
        from gamification.models import Milestone, UserMilestone
        ms = Milestone.objects.create(
            name='UM MS', metric='total_distance',
            threshold=Decimal('100'),
        )
        um = UserMilestone.objects.create(user=self.user, milestone=ms)
        self.assertIn('UM MS', str(um))


# ---------------------------------------------------------------------------
# Repository direct tests (covers repositories.py missing lines)
# ---------------------------------------------------------------------------

class RepositoryTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='repouser', email='repo@test.com', password='testpass123',
        )
        self.account = ConnectedAccount.objects.create(
            user=self.user, provider='strava', external_user_id='repo_ext',
        )

    def test_badge_repo_get_all(self):
        from gamification.data.repositories import BadgeRepository
        Badge.objects.create(name='R1', badge_type='single', threshold=Decimal('1'), metric='distance')
        repo = BadgeRepository()
        self.assertGreaterEqual(repo.get_all_badges().count(), 1)

    def test_badge_repo_has_badge(self):
        from gamification.data.repositories import BadgeRepository
        from gamification.models import UserBadge
        badge = Badge.objects.create(name='R2', badge_type='single', threshold=Decimal('1'), metric='distance')
        repo = BadgeRepository()
        self.assertFalse(repo.has_badge(self.user, badge))
        UserBadge.objects.create(user=self.user, badge=badge)
        self.assertTrue(repo.has_badge(self.user, badge))

    def test_badge_repo_award_badge(self):
        from gamification.data.repositories import BadgeRepository
        badge = Badge.objects.create(name='R3', badge_type='single', threshold=Decimal('1'), metric='distance')
        repo = BadgeRepository()
        obj, created = repo.award_badge(self.user, badge)
        self.assertTrue(created)
        obj2, created2 = repo.award_badge(self.user, badge)
        self.assertFalse(created2)

    def test_badge_repo_get_earned(self):
        from gamification.data.repositories import BadgeRepository
        from gamification.models import UserBadge
        badge = Badge.objects.create(name='R4', badge_type='single', threshold=Decimal('1'), metric='distance')
        repo = BadgeRepository()
        self.assertEqual(repo.get_earned_badges(self.user).count(), 0)
        UserBadge.objects.create(user=self.user, badge=badge)
        self.assertEqual(repo.get_earned_badges(self.user).count(), 1)

    def test_streak_repo(self):
        from gamification.data.repositories import StreakRepository
        repo = StreakRepository()
        streak = repo.get_or_create_streak(self.user)
        self.assertEqual(streak.current_count, 0)
        streak.current_count = 5
        repo.save_streak(streak)
        streak2 = repo.get_or_create_streak(self.user)
        self.assertEqual(streak2.current_count, 5)

    def test_milestone_repo(self):
        from gamification.data.repositories import MilestoneRepository
        from gamification.models import Milestone
        Milestone.objects.create(name='MR1', metric='total_distance', threshold=Decimal('50'))
        repo = MilestoneRepository()
        self.assertGreaterEqual(repo.get_all_milestones().count(), 1)

    def test_milestone_repo_has_and_award(self):
        from gamification.data.repositories import MilestoneRepository
        from gamification.models import Milestone
        ms = Milestone.objects.create(name='MR2', metric='total_distance', threshold=Decimal('50'))
        repo = MilestoneRepository()
        self.assertFalse(repo.has_milestone(self.user, ms))
        obj, created = repo.award_milestone(self.user, ms)
        self.assertTrue(created)
        self.assertTrue(repo.has_milestone(self.user, ms))

    def test_milestone_repo_get_reached(self):
        from gamification.data.repositories import MilestoneRepository
        from gamification.models import Milestone, UserMilestone
        ms = Milestone.objects.create(name='MR3', metric='total_distance', threshold=Decimal('50'))
        repo = MilestoneRepository()
        self.assertEqual(repo.get_reached_milestones(self.user).count(), 0)
        UserMilestone.objects.create(user=self.user, milestone=ms)
        self.assertEqual(repo.get_reached_milestones(self.user).count(), 1)

    def test_activity_stats_cumulative(self):
        from gamification.data.repositories import ActivityStatsRepository
        from activities.models import Activity
        Activity.objects.create(
            account=self.account, activity_type='running', duration=30,
            date=date.today(), distance=Decimal('10.00'), calories=200,
        )
        repo = ActivityStatsRepository()
        stats = repo.get_cumulative_stats(self.user)
        self.assertEqual(stats['total_activities'], 1)
        self.assertEqual(stats['total_distance'], Decimal('10.00'))

    def test_activity_stats_cumulative_with_type(self):
        from gamification.data.repositories import ActivityStatsRepository
        from activities.models import Activity
        Activity.objects.create(
            account=self.account, activity_type='running', duration=30,
            date=date.today(), distance=Decimal('10.00'),
        )
        Activity.objects.create(
            account=self.account, activity_type='cycling', duration=60,
            date=date.today(), distance=Decimal('25.00'),
        )
        repo = ActivityStatsRepository()
        stats = repo.get_cumulative_stats(self.user, activity_type='running')
        self.assertEqual(stats['total_activities'], 1)

    def test_activity_stats_active_dates(self):
        from gamification.data.repositories import ActivityStatsRepository
        from activities.models import Activity
        Activity.objects.create(
            account=self.account, activity_type='running', duration=30,
            date=date.today(), distance=Decimal('5.00'),
        )
        repo = ActivityStatsRepository()
        dates = repo.get_active_dates(self.user)
        self.assertIn(date.today(), dates)

    def test_activity_stats_active_dates_with_since(self):
        from gamification.data.repositories import ActivityStatsRepository
        from activities.models import Activity
        Activity.objects.create(
            account=self.account, activity_type='running', duration=30,
            date=date.today(), distance=Decimal('5.00'),
        )
        repo = ActivityStatsRepository()
        dates = repo.get_active_dates(self.user, since=date.today() - timedelta(days=7))
        self.assertIn(date.today(), dates)

    def test_activity_stats_count_in_period(self):
        from gamification.data.repositories import ActivityStatsRepository
        from activities.models import Activity
        Activity.objects.create(
            account=self.account, activity_type='running', duration=30,
            date=date.today(), distance=Decimal('5.00'),
        )
        repo = ActivityStatsRepository()
        count = repo.get_activity_count_in_period(
            self.user, 'running',
            date.today() - timedelta(days=7), date.today(),
        )
        self.assertEqual(count, 1)

    def test_activity_stats_single_max(self):
        from gamification.data.repositories import ActivityStatsRepository
        from activities.models import Activity
        Activity.objects.create(
            account=self.account, activity_type='running', duration=30,
            date=date.today(), distance=Decimal('5.00'),
        )
        Activity.objects.create(
            account=self.account, activity_type='running', duration=60,
            date=date.today(), distance=Decimal('15.00'),
        )
        repo = ActivityStatsRepository()
        max_val = repo.get_single_activity_max(self.user, 'running', 'distance')
        self.assertEqual(max_val, Decimal('15.00'))


# ---------------------------------------------------------------------------
# Signal integration tests (covers signals.py lines 26-38, 56-66)
# ---------------------------------------------------------------------------

class SignalIntegrationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='siguser', email='sig@test.com', password='testpass123',
        )
        self.account = ConnectedAccount.objects.create(
            user=self.user, provider='strava', external_user_id='sig_ext',
        )
        Badge.objects.create(
            name='Signal Badge', badge_type='single', activity_type='running',
            threshold=Decimal('1'), metric='duration', points=10,
        )

    def test_signal_fires_on_activity_create(self):
        """Creating an activity triggers the signal and awards the badge."""
        from activities.models import Activity
        from gamification.models import UserBadge
        Activity.objects.create(
            account=self.account, activity_type='running', duration=30,
            date=date.today(), distance=Decimal('5.00'),
        )
        # Signal should have evaluated and awarded the badge
        self.assertTrue(UserBadge.objects.filter(user=self.user).exists())

    def test_signal_updates_streak_on_create(self):
        from activities.models import Activity
        Activity.objects.create(
            account=self.account, activity_type='running', duration=30,
            date=date.today(), distance=Decimal('5.00'),
        )
        streak = Streak.objects.get(user=self.user)
        self.assertEqual(streak.current_count, 1)

    def test_send_achievement_event_logs_when_no_notification_service(self):
        from gamification.signals import _send_achievement_event
        # Should not raise — gracefully logs instead
        _send_achievement_event(self.user, 'badge_earned', {'badge_name': 'test'})


# ---------------------------------------------------------------------------
# Services progress tests (covers services.py lines 155-209)
# ---------------------------------------------------------------------------

class ServiceProgressTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='proguser', email='prog@test.com', password='testpass123',
        )
        self.account = ConnectedAccount.objects.create(
            user=self.user, provider='strava', external_user_id='prog_ext',
        )

    def test_get_badge_progress(self):
        Badge.objects.create(
            name='Prog Badge', badge_type='single', activity_type='running',
            threshold=Decimal('10'), metric='distance', points=50,
        )
        from activities.models import Activity
        Activity.objects.create(
            account=self.account, activity_type='running', duration=30,
            date=date.today(), distance=Decimal('5.00'),
        )
        service = GamificationService()
        progress = service.get_badge_progress(self.user)
        self.assertGreaterEqual(len(progress), 1)
        for p in progress:
            self.assertIn('badge', p)
            self.assertIn('progress_percentage', p)

    def test_get_badge_progress_cumulative(self):
        Badge.objects.create(
            name='Cum Prog', badge_type='cumulative', activity_type='',
            threshold=Decimal('100'), metric='distance', points=100,
        )
        service = GamificationService()
        progress = service.get_badge_progress(self.user)
        self.assertGreaterEqual(len(progress), 1)

    def test_get_badge_progress_streak(self):
        Badge.objects.create(
            name='Str Prog', badge_type='streak', activity_type='',
            threshold=Decimal('7'), metric='count', points=75,
        )
        service = GamificationService()
        progress = service.get_badge_progress(self.user)
        self.assertGreaterEqual(len(progress), 1)

    def test_get_badge_progress_frequency(self):
        Badge.objects.create(
            name='Freq Prog', badge_type='frequency', activity_type='running',
            threshold=Decimal('3'), metric='count', points=50,
        )
        service = GamificationService()
        progress = service.get_badge_progress(self.user)
        self.assertGreaterEqual(len(progress), 1)

    def test_get_milestone_progress(self):
        from gamification.models import Milestone
        Milestone.objects.create(
            name='Prog MS', metric='total_distance',
            threshold=Decimal('100'), points=100,
        )
        service = GamificationService()
        progress = service.get_milestone_progress(self.user)
        self.assertGreaterEqual(len(progress), 1)
        for p in progress:
            self.assertIn('milestone', p)
            self.assertIn('progress_percentage', p)

    def test_get_user_summary(self):
        service = GamificationService()
        summary = service.get_user_summary(self.user)
        self.assertIn('total_points', summary)
        self.assertIn('streak', summary)
        self.assertEqual(summary['total_points'], 0)


# ============================================================================
# Gamification signals coverage tests
# ============================================================================

class AchievementEventSignalsTest(TestCase):
    """Test signal handling and notification integration in gamification"""

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            username='signal-user',
            email='signal@test.com',
            password='TestPass123!'
        )

    def test_send_achievement_notification_success(self):
        """Covers _send_achievement_event function with successful NotificationService call"""
        from gamification.signals import _send_achievement_event
        from notifications.models import NotificationType
        
        with patch('notifications.business.services.NotificationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            _send_achievement_event(self.user, 'badge_earned', {
                'badge_id': 1,
                'badge_name': 'First Badge',
                'points': 50,
            })
            
            # Verify service was instantiated
            mock_service_class.assert_called_once()
            # Verify notify was called with MILESTONE_ACHIEVED type
            mock_service.notify.assert_called_once()
            call_args = mock_service.notify.call_args
            # notify signature: notify(title, description, payload, recipient_id, event_type, goal=None)
            assert call_args[0][3] == self.user.id
            assert call_args[0][4] == NotificationType.MILESTONE_ACHIEVED

    def test_send_achievement_notification_fallback_logging(self):
        """Covers _send_achievement_event function exception handling and logging"""
        from gamification.signals import _send_achievement_event
        
        with patch('notifications.business.services.NotificationService', side_effect=ImportError("NotificationService not available")):
            with patch('gamification.signals.logger.info') as mock_logger:
                _send_achievement_event(self.user, 'milestone_reached', {
                    'milestone_id': 1,
                    'milestone_name': 'Distance Milestone',
                    'points': 100,
                })
                
                # Verify fallback logging occurred
                mock_logger.assert_called_once()
                logged_message = mock_logger.call_args[0][0]
                assert 'Achievement event' in logged_message
                assert 'pending notification integration' in logged_message

    def test_send_achievement_event_with_streak_milestone(self):
        """Covers _send_achievement_event with streak_milestone event type"""
        from gamification.signals import _send_achievement_event
        
        with patch('notifications.business.services.NotificationService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            _send_achievement_event(self.user, 'streak_milestone', {
                'streak_days': 30,
            })
            
            mock_service.notify.assert_called_once()

