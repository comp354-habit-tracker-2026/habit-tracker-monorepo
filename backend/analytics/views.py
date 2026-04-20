<<<<<<< feature/group-16-reporting-insights
from analytics.presentation import (
    AnalyticsOverviewView,
    ActivityStatisticsView,
    PersonalRecordsView,
    ActivityTypeBreakdownView,
    WeeklySummaryView,
    ActivityStreaksView,
    ActivityForecastView
)

from analytics.presentation.views import AnalyticsOverviewView, HealthIndicatorsView

__all__ = ["AnalyticsOverviewView", "ActivityStatisticsView",
           "PersonalRecordsView",
           "ActivityTypeBreakdownView",
           "WeeklySummaryView",
           "ActivityStreaksView", "HealthIndicatorsView", "ActivityForecastView"]


=======
from analytics.presentation.views import AnalyticsOverviewView, HealthIndicatorsView

__all__ = ["AnalyticsOverviewView", "HealthIndicatorsView"]
>>>>>>> main
