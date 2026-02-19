from django.contrib import admin
from .models import Activity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'user', 'duration', 'date']
    list_filter = ['date', 'activity_type', 'user']
