from datetime import date, datetime, timezone
from unittest.mock import Mock, patch
from rest_framework.test import APIClient
from rest_framework import status

import pytest

from data_integration.business import (
    DataIntegrationService,
    StravaActivityFactory,
    StravaActivitySummary,
)
from data_integration.data import StravaActivityFetcher, StravaAuthService


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


@patch("data_integration.data.strava.urlopen")
def test_strava_fetcher_stops_after_first_full_page_without_date_filters(mock_urlopen):
    mock_response = Mock()
    mock_response.read.return_value = json_bytes([{**RAW_ACTIVITY, "id": idx} for idx in range(30)])
    mock_urlopen.return_value = context_manager(mock_response)

    fetcher = StravaActivityFetcher()
    activities = fetcher.get_all_activities(access_token="token-789")

    assert len(activities) == 30
    assert mock_urlopen.call_count == 1


@patch("data_integration.data.strava.urlopen")
def test_strava_fetcher_returns_empty_list_when_first_page_is_empty(mock_urlopen):
    mock_response = Mock()
    mock_response.read.return_value = b"[]"
    mock_urlopen.return_value = context_manager(mock_response)

    fetcher = StravaActivityFetcher()

    assert fetcher.get_all_activities(access_token="token-empty") == []


@patch("data_integration.data.strava.urlopen")
def test_strava_fetcher_raises_for_non_list_payload(mock_urlopen):
    mock_response = Mock()
    mock_response.read.return_value = json_bytes({"message": "not-a-list"})
    mock_urlopen.return_value = context_manager(mock_response)

    fetcher = StravaActivityFetcher()

    with pytest.raises(ValueError, match="Expected Strava activities response to be a list."):
        fetcher.get_all_activities(access_token="token-invalid")


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


def test_get_skiing_activities_filters_all_supported_ski_types():
    fetcher = StravaActivityFetcher()
    ski_activity = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 1, "sport_type": "AlpineSki"})
    backcountry_activity = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 2, "sport_type": "BackcountrySki"})
    nordic_activity = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 3, "sport_type": "NordicSki"})
    roller_activity = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 4, "sport_type": "RollerSki"})
    run_activity = StravaActivityFactory.create_activity_summary(RAW_ACTIVITY)

    activities = [
        ski_activity,
        backcountry_activity,
        nordic_activity,
        roller_activity,
        run_activity,
    ]
    filtered_activities = fetcher.get_skiing_activities(activities)

    assert [activity.external_id for activity in filtered_activities] == ["1", "2", "3", "4"]


def test_get_indoor_cycling_activities_filters_virtual_rides():
    fetcher = StravaActivityFetcher()
    virtual_ride = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 10, "type": "Ride", "sport_type": "VirtualRide"})
    outdoor_ride = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 11, "type": "Ride", "sport_type": "Ride"})

    activities = fetcher.getIndoorCyclingActivities([virtual_ride, outdoor_ride])

    assert [activity.external_id for activity in activities] == ["10"]

def test_get_running_activities_filters_all_supported_run_types():
    fetcher = StravaActivityFetcher()
    run_activity = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 1, "sport_type": "Run"})
    trail_run_activity = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 2, "sport_type": "TrailRun"})
    virtual_run_activity = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 3, "sport_type": "VirtualRun"})
    ski_activity = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 4, "sport_type": "AlpineSki"})
    activities = [run_activity, trail_run_activity, virtual_run_activity, ski_activity]
    filtered_activities = fetcher.get_running_activities(activities)
    assert [activity.external_id for activity in filtered_activities] == ["1", "2", "3"]


def test_get_running_activities_camel_case_wrapper_delegates_to_snake_case_method():
    fetcher = StravaActivityFetcher()
    activities = [StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 42, "sport_type": "Run"})]

    with patch.object(fetcher, "get_running_activities", return_value=activities) as mock_method:
        result = fetcher.getRunningActivities(activities)

    assert result == activities
    mock_method.assert_called_once_with(activities)


def test_get_cycling_activities_filters_outdoor_rides():
    fetcher = StravaActivityFetcher()
    ride_activity = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 10, "sport_type": "Ride"})
    mtb_activity = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 11, "sport_type": "MountainBikeRide"})
    gravel_activity = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 12, "sport_type": "GravelRide"})
    virtual_ride = StravaActivityFactory.create_activity_summary({**RAW_ACTIVITY, "id": 13, "sport_type": "VirtualRide"})
    activities = fetcher.getCyclingActivities([ride_activity, mtb_activity, gravel_activity, virtual_ride])
    assert [activity.external_id for activity in activities] == ["10", "11", "12"]


def context_manager(response):
    manager = Mock()
    manager.__enter__ = Mock(return_value=response)
    manager.__exit__ = Mock(return_value=False)
    return manager


def json_bytes(payload):
    import json

    return json.dumps(payload).encode("utf-8")

#==================================================================
#Auth tests

@patch("data_integration.data.strava.urlopen")
def test_strava_auth_connect_success(mock_urlopen):
    """Tests successful exchange of code for tokens (Covers try block)"""
    client = APIClient()
    
    # Setup Mock Response
    mock_response = Mock()
    mock_response.read.return_value = json_bytes({
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token"
    })
    mock_urlopen.return_value = context_manager(mock_response)

    url = "/api/v1/data-integrations/strava/connect/"
    response = client.post(url, {"code": "strava_code_123"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["access_token"] == "mock_access_token"


def test_strava_auth_connect_missing_code():
    """Tests the validation 'if not code' (Covers 400 error branch)"""
    client = APIClient()
    url = "/api/v1/data-integrations/strava/connect/"
    
    # Sending empty payload
    response = client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Code is required" in response.data["error"]


@patch("data_integration.data.strava.urlopen")
def test_strava_auth_refresh_success(mock_urlopen):
    """Tests successful token refresh (Covers Refresh method)"""
    client = APIClient()
    
    mock_response = Mock()
    mock_response.read.return_value = json_bytes({"access_token": "new_token"})
    mock_urlopen.return_value = context_manager(mock_response)

    url = "/api/v1/data-integrations/strava/refresh/"
    response = client.post(url, {"refresh_token": "old_token"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["access_token"] == "new_token"


@patch("data_integration.data.strava.urlopen")
def test_strava_auth_server_error(mock_urlopen):
    """Tests when Strava or network fails (Covers 'except' block)"""
    client = APIClient()
    
    # Force an exception when urlopen is called
    mock_urlopen.side_effect = Exception("Connection Timeout")

    url = "/api/v1/data-integrations/strava/refresh/"
    response = client.post(url, {"refresh_token": "any_token"}, format="json")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "internal error" in response.data["error"]


def test_strava_service_camel_case_wrapper():
    """
    Specifically tests the 'authenticateUser' camelCase wrapper 
    to ensure 100% coverage on the Service class lines.
    """
    
    service = StravaAuthService(client_id="123", client_secret="abc")
    
    # Mock the internal snake_case method so we don't actually trigger network
    with patch.object(service, 'authenticate_user', return_value={"status": "ok"}) as mock_method:
        result = service.authenticateUser("some_code")
        
        assert result["status"] == "ok"
        mock_method.assert_called_once_with("some_code")


def test_to_epoch_returns_none_for_none_input():
    assert StravaActivityFetcher._to_epoch(None, end_of_day=False) is None


def test_coerce_datetime_accepts_datetime_with_timezone():
    original = datetime(2025, 9, 27, 0, 30, 50, tzinfo=timezone.utc)

    parsed = StravaActivityFetcher._coerce_datetime(original, end_of_day=False)

    assert parsed == original


def test_coerce_datetime_accepts_naive_date_values():
    parsed = StravaActivityFetcher._coerce_datetime(date(2025, 8, 27), end_of_day=True)

    assert parsed == datetime(2025, 8, 27, 23, 59, 59, tzinfo=timezone.utc)


def test_coerce_datetime_accepts_iso_datetime_string_with_offset():
    parsed = StravaActivityFetcher._coerce_datetime("2025-09-27T00:30:50-04:00", end_of_day=False)

    assert parsed == datetime(2025, 9, 27, 4, 30, 50, tzinfo=timezone.utc)


def test_coerce_datetime_accepts_date_only_string():
    parsed = StravaActivityFetcher._coerce_datetime("2025-08-27", end_of_day=False)

    assert parsed == datetime(2025, 8, 27, 0, 0, 0, tzinfo=timezone.utc)


def test_coerce_datetime_rejects_unsupported_types():
    with pytest.raises(TypeError, match="Date values must be date, datetime, ISO 8601 string, or None."):
        StravaActivityFetcher._coerce_datetime(123, end_of_day=False)
