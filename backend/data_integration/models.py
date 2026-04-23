from django.db import models

class FileRecord(models.Model):
    url_link = models.URLField(max_length=500)
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.file_name} ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"


class MapMyRunActivity(models.Model):
    user_id = models.IntegerField(null=False, blank=False)

    activity_key = models.CharField(max_length=255, null=True, blank=True)

    workout_date = models.DateField()
    activity_type = models.CharField(max_length=100, null=True, blank=True)
    calories_burned_kcal = models.FloatField(null=True, blank=True)
    distance_km = models.FloatField()
    workout_time_seconds = models.IntegerField()

    avg_pace_min_per_km = models.FloatField(null=True, blank=True)
    max_pace_min_per_km = models.FloatField(null=True, blank=True)

    avg_speed_kmh = models.FloatField(null=True, blank=True)
    max_speed_kmh = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-workout_date"]

    def __str__(self):
        return f"{self.workout_date} - {self.activity_type or 'Activity'}"
    
class Meta:
    constraints = [
        models.UniqueConstraint(fields=["user_id", "activity_key"], name="unique_user_activity_key")
    ]