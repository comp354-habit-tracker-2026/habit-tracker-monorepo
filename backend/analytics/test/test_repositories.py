# ============================================================
# G13 - cathytham - InactivityDetector - PR #241
# ============================================================
from datetime import date
from unittest.mock import patch

from analytics.data.repositories import AnalyticsRepository

repository = AnalyticsRepository()


class FakeQuerySet:
    def __init__(self, max_date=None):
        self._max_date = max_date

    def filter(self, user):
        return self

    def aggregate(self, **kwargs):
        return {"max_date": self._max_date}


# Test cases for inactivity evaluation logic for severe scenarios
def test_inactivity_evaluation_no_activity():
    with patch("analytics.data.repositories.date") as mock_date, \
         patch("analytics.data.repositories.Activity.objects", FakeQuerySet(max_date=None)):
        mock_date.today.return_value = date(2026, 4, 6)
        result = repository.inactivity_evaluation(object())

    assert result == {
        "days_since_last_activity": None,
        "inactive": True,
        "severity": "severe",
    }


# Test cases for inactivity evaluation logic for none severity scenarios
def test_inactivity_evaluation_recent_activity_none():
    with patch("analytics.data.repositories.date") as mock_date, \
         patch("analytics.data.repositories.Activity.objects", FakeQuerySet(max_date=date(2026, 4, 6))):
        mock_date.today.return_value = date(2026, 4, 6)
        result = repository.inactivity_evaluation(object())

    assert result == {
        "days_since_last_activity": 0,
        "inactive": False,
        "severity": "none",
    }


# Test cases for inactivity evaluation logic for mild severity scenarios
def test_inactivity_evaluation_four_days_ago_mild():
    with patch("analytics.data.repositories.date") as mock_date, \
         patch("analytics.data.repositories.Activity.objects", FakeQuerySet(max_date=date(2026, 4, 2))):
        mock_date.today.return_value = date(2026, 4, 6)
        result = repository.inactivity_evaluation(object())

    assert result == {
        "days_since_last_activity": 4,
        "inactive": True,
        "severity": "mild",
    }
