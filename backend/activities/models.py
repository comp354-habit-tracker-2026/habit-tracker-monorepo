from django.db import models
from django.conf import settings

class Activity(models.Model):
    PROVIDER_CHOICES = [
        ('manual', 'Manual Entry'),
        ('strava', 'Strava'),
        ('mapmyrun', 'MapMyRun'),
        ('weski', 'We Ski'),
        ('mywhoosh', 'MyWhoosh'),
    ]
    
    activity_type = models.CharField(max_length=100)
    duration = models.IntegerField(help_text="Duration in minutes")
    date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    
    # External API fields
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='manual')
    external_id = models.CharField(max_length=255, blank=True, null=True)
    raw_data = models.JSONField(blank=True, null=True)
    # Some generic fields
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    calories = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Activities"
        unique_together = [['provider', 'external_id']]

    def __str__(self):
        return f"{self.activity_type} - {self.date} ({self.provider})"
