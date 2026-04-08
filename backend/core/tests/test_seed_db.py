from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from activities.models import Activity, ConnectedAccount
from goals.models import Goal

User = get_user_model()


@pytest.mark.django_db
class TestSeedDbCommand:

    def test_seed_creates_users_goals_and_activities(self):
        """Running seed_db creates the requested number of users, goals, and activities."""
        out = StringIO()
        call_command("seed_db", "--users=2", "--habits-per-user=1", "--activities-per-user=2", stdout=out)
        output = out.getvalue()

        assert "Seeded" in output
        assert User.objects.filter(is_superuser=False).count() == 2
        assert Goal.objects.count() == 2
        assert Activity.objects.count() == 4

    def test_seed_activities_linked_to_connected_account(self):
        """Every seeded activity must be linked to a ConnectedAccount, not directly to a user."""
        call_command("seed_db", "--users=1", "--habits-per-user=0", "--activities-per-user=3", stdout=StringIO())

        for activity in Activity.objects.all():
            assert activity.account is not None
            assert activity.account.provider == "strava"

    def test_seed_clear_flag_removes_existing_data(self):
        """--clear deletes all activities, goals, and non-superuser accounts before seeding."""
        call_command("seed_db", "--users=2", "--habits-per-user=1", "--activities-per-user=1", stdout=StringIO())
        assert User.objects.filter(is_superuser=False).count() == 2

        out = StringIO()
        call_command("seed_db", "--users=1", "--habits-per-user=0", "--activities-per-user=0", "--clear", stdout=out)

        assert "Cleared" in out.getvalue()
        assert User.objects.filter(is_superuser=False).count() == 1
        assert Goal.objects.count() == 0

    def test_seed_zero_users_prints_warning(self):
        """Passing --users=0 should print a warning and create nothing."""
        out = StringIO()
        call_command("seed_db", "--users=0", stdout=out)

        assert "No users requested" in out.getvalue()
        assert User.objects.filter(is_superuser=False).count() == 0

    def test_seed_is_deterministic_with_seed_flag(self):
        """Running with the same --seed value twice produces the same usernames."""
        call_command("seed_db", "--users=2", "--habits-per-user=0", "--activities-per-user=0", "--seed=42", stdout=StringIO())
        usernames_first = set(User.objects.filter(is_superuser=False).values_list("username", flat=True))

        User.objects.filter(is_superuser=False).delete()

        call_command("seed_db", "--users=2", "--habits-per-user=0", "--activities-per-user=0", "--seed=42", stdout=StringIO())
        usernames_second = set(User.objects.filter(is_superuser=False).values_list("username", flat=True))

        assert usernames_first == usernames_second
