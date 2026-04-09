from django.contrib import admin

from .models import FileRecord

@admin.register(FileRecord)
class FileRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "file_name", "url_link", "created_at")
    search_fields = ("file_name", "url_link")
    list_filter = ("created_at",)
