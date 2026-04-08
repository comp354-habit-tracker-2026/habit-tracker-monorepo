from django.db import models

class FileRecord(models.Model):
    url_link = models.URLField(max_length=500)
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.file_name} ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
