from django.urls import path, include

from .views import AnalyticsOverviewView

from analytics.progess_series.views import GoalProgressSeriesView

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics_overview"),
    path(
        "goals/<int:goal_id>/progress-series/",
        GoalProgressSeriesView.as_view(),
        name="goal-progress-series",
    ),
]
