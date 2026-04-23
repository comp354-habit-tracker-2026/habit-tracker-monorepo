import pytest
from rest_framework.test import APIClient

from mywhoosh_integration.models import SyncStatus
from mywhoosh_integration.services.sync_status_service import SyncStatusService


pytestmark = pytest.mark.django_db


def test_record_success_creates_sync_status():
    sync_status = SyncStatusService.record_success(
        user_id=101,
        sessions_imported=4,
        duplicates_skipped=1,
    )

    assert sync_status.user_id == 101
    assert sync_status.status == SyncStatus.STATUS_SUCCESS
    assert sync_status.sessions_imported == 4
    assert sync_status.duplicates_skipped == 1
    assert sync_status.error_message is None


def test_record_partial_creates_sync_status():
    sync_status = SyncStatusService.record_partial(
        user_id=202,
        sessions_imported=3,
        duplicates_skipped=0,
        error_message="Some metrics were missing.",
    )

    assert sync_status.user_id == 202
    assert sync_status.status == SyncStatus.STATUS_PARTIAL
    assert sync_status.sessions_imported == 3
    assert sync_status.duplicates_skipped == 0
    assert sync_status.error_message == "Some metrics were missing."


def test_record_failure_creates_sync_status():
    sync_status = SyncStatusService.record_failure(
        user_id=303,
        error_message="MyWhoosh API timeout",
    )

    assert sync_status.user_id == 303
    assert sync_status.status == SyncStatus.STATUS_FAILED
    assert sync_status.sessions_imported == 0
    assert sync_status.duplicates_skipped == 0
    assert sync_status.error_message == "MyWhoosh API timeout"


def test_get_latest_for_user_returns_most_recent():
    SyncStatusService.record_success(user_id=404, sessions_imported=1)
    latest = SyncStatusService.record_failure(
        user_id=404,
        error_message="Token expired",
    )

    fetched = SyncStatusService.get_latest_for_user(404)

    assert fetched is not None
    assert fetched.id == latest.id
    assert fetched.status == SyncStatus.STATUS_FAILED


def test_status_endpoint_returns_latest_sync_status():
    client = APIClient()

    SyncStatusService.record_success(
        user_id=505,
        sessions_imported=6,
        duplicates_skipped=2,
    )

    response = client.get("/mywhoosh/status", {"user_id": 505})

    assert response.status_code == 200
    assert response.data["user_id"] == 505
    assert response.data["status"] == SyncStatus.STATUS_SUCCESS
    assert response.data["sessions_imported"] == 6
    assert response.data["duplicates_skipped"] == 2


def test_status_endpoint_returns_400_if_user_id_missing():
    client = APIClient()

    response = client.get("/mywhoosh/status")

    assert response.status_code == 400
    assert "Missing required query parameter" in response.data["detail"]


def test_status_endpoint_returns_400_if_user_id_invalid():
    client = APIClient()

    response = client.get("/mywhoosh/status", {"user_id": "abc"})

    assert response.status_code == 400
    assert response.data["detail"] == "user_id must be an integer"


def test_status_endpoint_returns_404_if_no_status_exists():
    client = APIClient()

    response = client.get("/mywhoosh/status", {"user_id": 9999})

    assert response.status_code == 404
    assert response.data["detail"] == "No sync status found for this user"
