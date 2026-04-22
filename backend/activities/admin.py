from django.contrib import admin
from .models import Activity, ConnectedAccount


@admin.register(ConnectedAccount)
class ConnectedAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'external_user_id', 'connected_at']
    list_filter = ['provider']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'account', 'duration', 'date']
    list_filter = ['date', 'activity_type']
