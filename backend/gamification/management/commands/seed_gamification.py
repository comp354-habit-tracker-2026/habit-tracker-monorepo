from django.core.management.base import BaseCommand

from gamification.models import Badge, Milestone


BADGES = [
    # --- Single activity badges ---
    {
        'name': 'First Steps',
        'description': 'Complete your first activity',
        'icon': 'first-steps',
        'badge_type': 'single',
        'activity_type': '',
        'threshold': 1,
        'metric': 'duration',
        'points': 10,
    },
    {
        'name': '10K Runner',
        'description': 'Run 10km in a single session',
        'icon': '10k-runner',
        'badge_type': 'single',
        'activity_type': 'running',
        'threshold': 10,
        'metric': 'distance',
        'points': 50,
    },
    {
        'name': 'Half Marathon',
        'description': 'Run 21.1km in a single session',
        'icon': 'half-marathon',
        'badge_type': 'single',
        'activity_type': 'running',
        'threshold': 21.1,
        'metric': 'distance',
        'points': 100,
    },
    {
        'name': 'Century Ride',
        'description': 'Cycle 100km in a single ride',
        'icon': 'century-ride',
        'badge_type': 'single',
        'activity_type': 'cycling',
        'threshold': 100,
        'metric': 'distance',
        'points': 150,
    },
    {
        'name': 'Calorie Crusher',
        'description': 'Burn 500 calories in a single session',
        'icon': 'calorie-crusher',
        'badge_type': 'single',
        'activity_type': '',
        'threshold': 500,
        'metric': 'calories',
        'points': 50,
    },

    # --- Cumulative badges ---
    {
        'name': '100km Club',
        'description': 'Run a total of 100km',
        'icon': '100km-club',
        'badge_type': 'cumulative',
        'activity_type': 'running',
        'threshold': 100,
        'metric': 'distance',
        'points': 100,
    },
    {
        'name': '500km Club',
        'description': 'Run a total of 500km',
        'icon': '500km-club',
        'badge_type': 'cumulative',
        'activity_type': 'running',
        'threshold': 500,
        'metric': 'distance',
        'points': 250,
    },
    {
        'name': 'Cycling Century',
        'description': 'Cycle a total of 1000km',
        'icon': 'cycling-century',
        'badge_type': 'cumulative',
        'activity_type': 'cycling',
        'threshold': 1000,
        'metric': 'distance',
        'points': 300,
    },
    {
        'name': 'Iron Will',
        'description': 'Log 100 total activities',
        'icon': 'iron-will',
        'badge_type': 'cumulative',
        'activity_type': '',
        'threshold': 100,
        'metric': 'count',
        'points': 200,
    },

    # --- Streak badges ---
    {
        'name': 'Week Warrior',
        'description': 'Maintain a 7-day activity streak',
        'icon': 'week-warrior',
        'badge_type': 'streak',
        'activity_type': '',
        'threshold': 7,
        'metric': 'count',
        'points': 75,
    },
    {
        'name': 'Fortnight Fighter',
        'description': 'Maintain a 14-day activity streak',
        'icon': 'fortnight-fighter',
        'badge_type': 'streak',
        'activity_type': '',
        'threshold': 14,
        'metric': 'count',
        'points': 150,
    },
    {
        'name': 'Monthly Machine',
        'description': 'Maintain a 30-day activity streak',
        'icon': 'monthly-machine',
        'badge_type': 'streak',
        'activity_type': '',
        'threshold': 30,
        'metric': 'count',
        'points': 300,
    },

    # --- Frequency badges ---
    {
        'name': 'Tri-Weekly Runner',
        'description': 'Run 3 times in a single week',
        'icon': 'tri-weekly-runner',
        'badge_type': 'frequency',
        'activity_type': 'running',
        'threshold': 3,
        'metric': 'count',
        'points': 50,
    },
    {
        'name': 'Daily Grinder',
        'description': 'Log 5 activities in a single week',
        'icon': 'daily-grinder',
        'badge_type': 'frequency',
        'activity_type': '',
        'threshold': 5,
        'metric': 'count',
        'points': 75,
    },
]


MILESTONES = [
    # Distance milestones
    {
        'name': '50km Total',
        'description': 'Logged 50km of total distance across all activities',
        'icon': '50km',
        'metric': 'total_distance',
        'threshold': 50,
        'activity_type': '',
        'points': 50,
    },
    {
        'name': '100km Total',
        'description': 'Logged 100km of total distance',
        'icon': '100km',
        'metric': 'total_distance',
        'threshold': 100,
        'activity_type': '',
        'points': 100,
    },
    {
        'name': '500km Total',
        'description': 'Logged 500km of total distance',
        'icon': '500km',
        'metric': 'total_distance',
        'threshold': 500,
        'activity_type': '',
        'points': 250,
    },
    {
        'name': '1000km Total',
        'description': 'Logged 1000km of total distance',
        'icon': '1000km',
        'metric': 'total_distance',
        'threshold': 1000,
        'activity_type': '',
        'points': 500,
    },

    # Activity count milestones
    {
        'name': '10 Activities',
        'description': 'Completed 10 activities',
        'icon': '10-activities',
        'metric': 'total_activities',
        'threshold': 10,
        'activity_type': '',
        'points': 25,
    },
    {
        'name': '50 Activities',
        'description': 'Completed 50 activities',
        'icon': '50-activities',
        'metric': 'total_activities',
        'threshold': 50,
        'activity_type': '',
        'points': 100,
    },
    {
        'name': '100 Activities',
        'description': 'Completed 100 activities',
        'icon': '100-activities',
        'metric': 'total_activities',
        'threshold': 100,
        'activity_type': '',
        'points': 200,
    },

    # Duration milestones
    {
        'name': '10 Hours Active',
        'description': 'Logged 600 minutes of total activity',
        'icon': '10-hours',
        'metric': 'total_duration',
        'threshold': 600,
        'activity_type': '',
        'points': 75,
    },
    {
        'name': '50 Hours Active',
        'description': 'Logged 3000 minutes of total activity',
        'icon': '50-hours',
        'metric': 'total_duration',
        'threshold': 3000,
        'activity_type': '',
        'points': 200,
    },

    # Calorie milestones
    {
        'name': '10,000 Calories',
        'description': 'Burned a total of 10,000 calories',
        'icon': '10k-cal',
        'metric': 'total_calories',
        'threshold': 10000,
        'activity_type': '',
        'points': 100,
    },
    {
        'name': '50,000 Calories',
        'description': 'Burned a total of 50,000 calories',
        'icon': '50k-cal',
        'metric': 'total_calories',
        'threshold': 50000,
        'activity_type': '',
        'points': 300,
    },
]


class Command(BaseCommand):
    help = 'Seed badge and milestone definitions for the gamification system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing badges and milestones before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            Badge.objects.all().delete()
            Milestone.objects.all().delete()
            self.stdout.write('Cleared existing badges and milestones.')

        badge_count = 0
        for badge_data in BADGES:
            _, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data,
            )
            if created:
                badge_count += 1

        milestone_count = 0
        for milestone_data in MILESTONES:
            _, created = Milestone.objects.get_or_create(
                name=milestone_data['name'],
                defaults=milestone_data,
            )
            if created:
                milestone_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {badge_count} badges and {milestone_count} milestones.'
        ))
