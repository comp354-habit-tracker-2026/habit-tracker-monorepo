from __future__ import annotations

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from activities.models import Activity, ConnectedAccount
from goals.models import Goal


ACTIVITY_TYPES = [
    "running",
    "cycling",
    "swimming",
    "yoga",
    "strength",
    "hiking",
    "skiing",
]

GOAL_TARGET_RANGES = {
    "distance": (5, 100),
    "duration": (30, 600),
    "frequency": (3, 30),
    "calories": (200, 3000),
    "custom": (1, 100),
}


class Command(BaseCommand):
    help = "Seed database with sample users, goals, and activities"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=10)
        parser.add_argument("--habits-per-user", type=int, default=3)
        parser.add_argument("--activities-per-user", type=int, default=10)
        parser.add_argument("--clear", action="store_true")
        parser.add_argument("--seed", type=int, default=None)

    def handle(self, *args, **options):
        users_count = max(options["users"], 0)
        habits_per_user = max(options["habits_per_user"], 0)
        activities_per_user = max(options["activities_per_user"], 0)
        seed = options.get("seed")

        fake = Faker()
        if seed is not None:
            random.seed(seed)
            fake.seed_instance(seed)

        User = get_user_model()
        today = timezone.now().date()

        if options["clear"]:
            Activity.objects.all().delete()
            Goal.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write("Cleared activities, goals, and non-superuser accounts.")

        if users_count == 0:
            self.stdout.write(self.style.WARNING("No users requested; nothing to seed."))
            return

        goal_types = [choice[0] for choice in Goal.TYPE_CHOICES]

        created_users = 0
        created_goals = 0
        created_activities = 0

        with transaction.atomic():
            for _ in range(users_count):
                user = self._create_user(User, fake)
                created_users += 1

                for _ in range(habits_per_user):
                    goal = self._create_goal(user, goal_types, fake, today)
                    created_goals += 1

                for _ in range(activities_per_user):
                    self._create_activity(user, fake, today)
                    created_activities += 1

        self.stdout.write(self.style.SUCCESS(
            "Seeded "
            f"{created_users} users, "
            f"{created_goals} goals, "
            f"{created_activities} activities."
        ))

    def _create_user(self, User, fake):
        base_username = fake.user_name()
        username = base_username
        suffix = 0
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base_username}{suffix}"

        email = fake.email()
        password = "Password_123"
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
        )

    def _create_goal(self, user, goal_types, fake, today):
        goal_type = random.choice(goal_types)
        title = fake.sentence(nb_words=4).rstrip(".")
        description = fake.sentence(nb_words=10)
        target_min, target_max = GOAL_TARGET_RANGES[goal_type]
        target_value = self._random_decimal(target_min, target_max)
        current_value = self._random_decimal(0, float(target_value))

        start_date = fake.date_between(start_date="-120d", end_date="-7d")
        end_date = start_date + timedelta(days=random.randint(7, 120))

        return Goal.objects.create(
            user=user,
            title=title,
            description=description,
            target_value=target_value,
            current_value=current_value,
            goal_type=goal_type,
            status="active",
            start_date=start_date,
            end_date=end_date,
        )

    def _create_activity(self, user, fake, today):
        activity_type = random.choice(ACTIVITY_TYPES)
        duration = random.randint(15, 180)
        activity_date = fake.date_between(start_date="-90d", end_date=today)

        distance = None
        if activity_type in {"running", "cycling", "hiking", "skiing"}:
            distance = self._random_decimal(1, 40)

        calories = random.randint(100, 900)

        # Activities must be linked to a ConnectedAccount, not directly to a user.
        # We use strava as the default provider for seeded data.
        account, _ = ConnectedAccount.objects.get_or_create(
            user=user,
            provider="strava",
            defaults={"external_user_id": f"seed_{user.pk}"},
        )

        return Activity.objects.create(
            account=account,
            activity_type=activity_type,
            duration=duration,
            date=activity_date,
            distance=distance,
            calories=calories,
        )

    def _random_decimal(self, minimum, maximum):
        value = random.uniform(float(minimum), float(maximum))
        return Decimal(f"{value:.2f}")
