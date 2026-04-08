from django.db import models
from django.conf import settings


class Badge(models.Model):
    """A badge definition -- what it takes to earn it.

    Group 22 defines high-level goals/rewards; this model stores the
    concrete badge rules that Group 24 evaluates against incoming activities.
    """

    BADGE_TYPE_CHOICES = [
        ('single', 'Single Activity'),     # e.g. "run 10km in one session"
        ('cumulative', 'Cumulative'),       # e.g. "run 100km total"
        ('streak', 'Streak'),              # e.g. "7-day activity streak"
        ('frequency', 'Frequency'),        # e.g. "cycle 3x per week"
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text="Icon identifier for frontend")

    badge_type = models.CharField(max_length=20, choices=BADGE_TYPE_CHOICES)
    activity_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Activity type this badge applies to, blank = any activity",
    )

    threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The value the user must reach (km, minutes, count, etc.)",
    )
    metric = models.CharField(
        max_length=50,
        default='distance',
        help_text="What is being measured: distance, duration, calories, count",
    )
    points = models.PositiveIntegerField(default=0, help_text="Coins/points awarded")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['badge_type', 'threshold']

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """Record of a badge earned by a specific user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='earned_badges',
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='awards')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'badge']]
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user} earned {self.badge.name}"


class Streak(models.Model):
    """Tracks consecutive active days for a user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streak',
    )
    current_count = models.PositiveIntegerField(default=0)
    longest_count = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.current_count} day streak"


class Milestone(models.Model):
    """A cumulative milestone definition (e.g. 100km total running)."""

    METRIC_CHOICES = [
        ('total_distance', 'Total Distance'),
        ('total_duration', 'Total Duration'),
        ('total_calories', 'Total Calories'),
        ('total_activities', 'Total Activities'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)

    metric = models.CharField(max_length=30, choices=METRIC_CHOICES)
    threshold = models.DecimalField(max_digits=10, decimal_places=2)
    activity_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Blank = all activity types",
    )
    points = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['metric', 'threshold']

    def __str__(self):
        return self.name


class UserMilestone(models.Model):
    """Record of a milestone reached by a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reached_milestones',
    )
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='awards')
    reached_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'milestone']]
        ordering = ['-reached_at']

    def __str__(self):
        return f"{self.user} reached {self.milestone.name}"
