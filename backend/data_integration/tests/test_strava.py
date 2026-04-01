from datetime import date, datetime, timezone
from unittest.mock import Mock, patch

import pytest

from data_integration.business import (
    DataIntegrationService,
    StravaActivityFactory,
    StravaActivitySummary,
)
from data_integration.data import StravaActivityFetcher


RAW_ACTIVITY = {
    "id": 12345,
    "name": "Lunch Run",
    "type": "Run",
    "sport_type": "Run",
    "distance": 5000.4,
    "moving_time": 1500,
    "elapsed_time": 1560,
    "total_elevation_gain": 48.2,
    "start_date": "2026-03-20T16:30:00Z",
    "start_date_local": "2026-03-20T12:30:00-04:00",
    "timezone": "(GMT-04:00) America/Toronto",
    "average_speed": 3.33,
    "max_speed": 4.9,
}


def test_activity_factory_creates_summary():
    summary = StravaActivityFactory.create_activity_summary(RAW_ACTIVITY)

    assert isinstance(summary, StravaActivitySummary)
    assert summary.external_id == "12345"
    assert summary.name == "Lunch Run"
    assert summary.sport_type == "Run"
    assert summary.activity_type == "Run"
    assert summary.distance == pytest.approx(5000.4)
    assert summary.moving_time == 1500
    assert summary.elapsed_time == 1560
    assert summary.total_elevation_gain == pytest.approx(48.2)
    assert summary.start_date == datetime(2026, 3, 20, 16, 30, tzinfo=timezone.utc)
    assert summary.raw_data["id"] == 12345


def test_activity_factory_creates_summary_list():
    summaries = StravaActivityFactory.create_many([RAW_ACTIVITY, {**RAW_ACTIVITY, "id": 67890, "name": "Evening Ride"}])

    assert len(summaries) == 2
    assert summaries[0].external_id == "12345"
    assert summaries[1].external_id == "67890"
    assert summaries[1].name == "Evening Ride"


@patch("data_integration.data.strava.urlopen")
def test_strava_fetcher_defaults_to_recent_30_activities(mock_urlopen):
    mock_response = Mock()
    mock_response.read.return_value = b'[{"id": 12345, "name": "Lunch Run"}]'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    fetcher = StravaActivityFetcher()
    activities = fetcher.get_all_activities(access_token="token-123")

    request = mock_urlopen.call_args.args[0]

    assert len(activities) == 1
    assert activities[0].external_id == "12345"
    assert "per_page=30" in request.full_url
    assert "page=1" in request.full_url
    assert request.headers["Authorization"] == "Bearer token-123"


@patch("data_integration.data.strava.urlopen")
def test_strava_fetcher_uses_date_filters_and_paginates(mock_urlopen):
    page_one = Mock()
    page_one.read.return_value = json_bytes([{**RAW_ACTIVITY, "id": 1} for _ in range(200)])

    page_two = Mock()
    page_two.read.return_value = json_bytes([{**RAW_ACTIVITY, "id": 2}])

    mock_urlopen.side_effect = [
        context_manager(page_one),
        context_manager(page_two),
    ]

    fetcher = StravaActivityFetcher()
    expected_after = fetcher._to_epoch(date(2026, 3, 1), end_of_day=False)
    expected_before = fetcher._to_epoch(date(2026, 3, 31), end_of_day=True)
    activities = fetcher.getAllActivities(
        accessToken="token-456",
        startDate=date(2026, 3, 1),
        endDate=date(2026, 3, 31),
    )

    first_request = mock_urlopen.call_args_list[0].args[0]
    second_request = mock_urlopen.call_args_list[1].args[0]

    assert len(activities) == 201
    assert "per_page=200" in first_request.full_url
    assert f"after={expected_after}" in first_request.full_url
    assert f"before={expected_before}" in first_request.full_url
    assert "page=1" in first_request.full_url
    assert "page=2" in second_request.full_url


def test_data_integration_service_delegates_to_strava_fetcher():
    fetcher = Mock()
    fetcher.get_all_activities.return_value = ["activity"]

    service = DataIntegrationService(strava_fetcher=fetcher)
    activities = service.get_strava_activities("token-789", "2026-03-01", "2026-03-31")

    assert activities == ["activity"]
    fetcher.get_all_activities.assert_called_once_with(
        access_token="token-789",
        start_date="2026-03-01",
        end_date="2026-03-31",
    )


def context_manager(response):
    manager = Mock()
    manager.__enter__ = Mock(return_value=response)
    manager.__exit__ = Mock(return_value=False)
    return manager


def json_bytes(payload):
    import json

    return json.dumps(payload).encode("utf-8")
