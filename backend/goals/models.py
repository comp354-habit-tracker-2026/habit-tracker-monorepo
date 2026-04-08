from django.db import models
from django.conf import settings

class Goal(models.Model):
    class ProgressState(models.TextChoices):
        ON_TRACK = "ON_TRACK", "On Track"
        ACHIEVED = "ACHIEVED", "Achieved"
        AT_RISK = "AT_RISK", "At Risk"
        MISSED = "MISSED", "Missed"

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('failed', 'Failed'),
    ]
    
    TYPE_CHOICES = [
        ('distance', 'Distance'),
        ('duration', 'Duration'),
        ('frequency', 'Frequency'),
        ('calories', 'Calories'),
        ('custom', 'Custom'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    goal_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='custom')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    # Stores the last progress state computed by the goal progress evaluator.
    progress_state = models.CharField(
        max_length=20,
        choices=ProgressState.choices,
        default=ProgressState.ON_TRACK,
    )
    # Records when progress_state most recently changed.
    progress_state_changed_at = models.DateTimeField(null=True, blank=True)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"

    @property
    def progress_percentage(self):
        if self.target_value > 0:
            return min(100, (self.current_value / self.target_value) * 100)
        return 0


class ProgressLog(models.Model):
    """Records which activities contribute to which goals.

    This is a many-to-many link between Goal and Activity — one activity
    can count towards multiple goals, and one goal can be fed by many activities.

    Added by Group 9 as part of the DB schema (issue #66).
    Groups 22/23 (goal logic) may want to add queries on top of this.
    """

    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='progress_logs')
    activity = models.ForeignKey(
        'activities.Activity',
        on_delete=models.CASCADE,
        related_name='progress_logs',
    )

    class Meta:
        db_table = 'progress_log'
        constraints = [
            # The same activity should only be counted towards a goal once
            models.UniqueConstraint(fields=['goal', 'activity'], name='unique_goal_activity'),
        ]

    def __str__(self):
        return f"Activity {self.activity_id} → Goal {self.goal_id}"
