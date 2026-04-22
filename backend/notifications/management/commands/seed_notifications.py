"""
================================================================================
G15 SEED DEMO: NOTIFICATION STATES
================================================================================

This command populates the database with goals in every possible health state:
[ ACHIEVED ] -> Goal met (e.g., 100/100 km)
[ AT RISK  ] -> Behind schedule (e.g., 10/200 km at halfway mark)
[ MISSED   ] -> Deadline passed without meeting target
[ ON TRACK ] -> Progressing as expected (e.g., 15/30 km)

Layout:
1. Identify User -> 2. Clear Old Data -> 3. Create Goals -> 4. Trigger Notifications
"""

from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analytics.business.goal_progress import GoalProgressService
from goals.models import Goal
from notifications.models import Notification

User = get_user_model()

# ------------------------------------------------------------------------------
# STEP 0: DEFINE DEMO SCENARIOS
# ------------------------------------------------------------------------------
DEMO_GOALS = [
    {
        "title": "[Demo] Run 100 km — ACHIEVED",
        "goal_type": "distance",
        "target_value": 100,
        "current_value": 100,        # TARGET MET
        "start_date": date.today() - timedelta(days=10),
        "end_date": date.today() + timedelta(days=10),
    },
    {
        "title": "[Demo] Cycle 200 km — AT_RISK",
        "goal_type": "distance",
        "target_value": 200,
        "current_value": 10,         # BEHIND SCHEDULE (5%)
        "start_date": date.today() - timedelta(days=15),
        "end_date": date.today() + timedelta(days=15),
    },
    {
        "title": "[Demo] Swim 50 km — MISSED",
        "goal_type": "distance",
        "target_value": 50,
        "current_value": 20,         # EXPIRED
        "start_date": date.today() - timedelta(days=30),
        "end_date": date.today() - timedelta(days=1),
    },
    {
        "title": "[Demo] Walk 30 km — ON_TRACK",
        "goal_type": "distance",
        "target_value": 30,
        "current_value": 15,         # PERFECT PACE (50%)
        "start_date": date.today() - timedelta(days=15),
        "end_date": date.today() + timedelta(days=15),
    },
]


class Command(BaseCommand):
    help = "Seed demo goal-progress notifications for all four health indicator states."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=None,
            help="Username to seed notifications for.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all [Demo] goals and their notifications before seeding.",
        )

    def handle(self, *args, **options):
        # ----------------------------------------------------------------------
        # STEP 1: RESOLVE TARGET USER
        # ----------------------------------------------------------------------
        user = self._resolve_user(options["username"])
        self.stdout.write(f"\nSeeding notifications for user: {user.username}")

        # ----------------------------------------------------------------------
        # STEP 2: CLEANUP (Optional)
        # ----------------------------------------------------------------------
        if options["clear"]:
            deleted, _ = Goal.objects.filter(user=user, title__startswith="[Demo]").delete()
            self.stdout.write(self.style.WARNING(f"Cleared {deleted} existing demo goal(s)."))

        svc = GoalProgressService()

        # ----------------------------------------------------------------------
        # STEP 3: DATABASE INSERTION & EVALUATION
        # ----------------------------------------------------------------------
        with transaction.atomic():
            for spec in DEMO_GOALS:
                # Create the Goal record
                goal = Goal.objects.create(
                    user=user,
                    status="active",
                    description="Auto-generated demo goal.",
                    **spec,
                )
                
                # Evaluation triggers the Notification logic
                result = svc.evaluate_goal(goal)
                state = result["state"]
                notified = result["notification_created"]

                # Output visual feedback to console
                label = self.style.SUCCESS(state) if notified else self.style.WARNING(f"{state} (no notif)")
                self.stdout.write(f"  [OK] Created {goal.title}: {label}")

        self.stdout.write(self.style.SUCCESS("\nDone! Check your inbox at: GET /api/v1/notifications/"))

    def _resolve_user(self, username):
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f"User '{username}' not found.")

        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not user:
            raise CommandError("No users found. Create a user first.")
        return user
