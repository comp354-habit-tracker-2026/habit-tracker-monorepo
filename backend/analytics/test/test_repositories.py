# ============================================================
# G13 - cathytham - InactivityDetector - PR #241
# ============================================================ 
import os
import sys
import types
from datetime import date
from unittest.mock import patch

# Ensure backend package root is on sys.path for standalone test execution.
here = os.path.dirname(__file__)
backend_root = os.path.abspath(os.path.join(here, "..", ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# Provide lightweight fake Django and activity modules
django_pkg = types.ModuleType("django")
django_db_pkg = types.ModuleType("django.db")
django_db_models = types.ModuleType("django.db.models")
django_db_models.Avg = lambda value: value
django_db_models.Sum = lambda value: value
django_db_models.Max = lambda value: value
django_db_pkg.models = django_db_models
django_pkg.db = django_db_pkg
sys.modules["django"] = django_pkg
sys.modules["django.db"] = django_db_pkg
sys.modules["django.db.models"] = django_db_models

activities_pkg = types.ModuleType("activities")
activities_models = types.ModuleType("activities.models")

class FakeQuerySet:
    def __init__(self, max_date=None):
        self._max_date = max_date

    def filter(self, user):
        return self

    def aggregate(self, **kwargs):
        return {"max_date": self._max_date}

class FakeActivity:
    objects = FakeQuerySet()

activities_models.Activity = FakeActivity
activities_pkg.models = activities_models
sys.modules["activities"] = activities_pkg
sys.modules["activities.models"] = activities_models

from analytics.data.repositories import AnalyticsRepository

repository = AnalyticsRepository()

#Test cases for inactivity evaluation logic for severe scenarios
@patch("analytics.data.repositories.date.today", return_value=date(2026, 4, 6))
def test_inactivity_evaluation_no_activity(mock_today):
    with patch("analytics.data.repositories.Activity.objects", FakeQuerySet(max_date=None)):
        result = repository.inactivity_evaluation(object())

    assert result == {
        "days_since_last_activity": None,
        "inactive": True,
        "severity": "severe",
    }

# Test cases for inactivity evaluation logic for none severity scenarios
@patch("analytics.data.repositories.date.today", return_value=date(2026, 4, 6))
def test_inactivity_evaluation_recent_activity_none(mock_today):
    with patch("analytics.data.repositories.Activity.objects", FakeQuerySet(max_date=date(2026, 4, 6))):
        result = repository.inactivity_evaluation(object())

    assert result == {
        "days_since_last_activity": 0,
        "inactive": False,
        "severity": "none",
    }

# Test cases for inactivity evaluation logic for mild severity scenarios
@patch("analytics.data.repositories.date.today", return_value=date(2026, 4, 6))
def test_inactivity_evaluation_four_days_ago_mild(mock_today):
    with patch("analytics.data.repositories.Activity.objects", FakeQuerySet(max_date=date(2026, 4, 2))):
        result = repository.inactivity_evaluation(object())

    assert result == {
        "days_since_last_activity": 4,
        "inactive": True,
        "severity": "mild",
    }
    