from django.contrib import admin
from .models import Goal

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'target_value', 'created_at']
    list_filter = ['created_at', 'user']
