from django.urls import path

from .views import AnalyticsOverviewView
from .views import personal_record_view

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
]

urlpatterns = [
    path("personal-record/<int:habit_id>/", personal_record_view),
]
