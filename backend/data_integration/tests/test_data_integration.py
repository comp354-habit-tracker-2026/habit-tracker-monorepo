import pytest
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from data_integration.business.we_ski.domain import ParsedSession, TrackPoint
from data_integration.business.we_ski.validator import WeSkiGpxValidator

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def _create_user(**kwargs):
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    user = create_user(
        username="integrationuser",
        email="integration@test.com",
        password="TestPass123!",
    )
    api_client.user = user
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.mark.django_db
def test_list_data_integrations_returns_business_data(authenticated_client):
    response = authenticated_client.get("/api/v1/data-integrations/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert len(response.data) >= 1
    assert "provider" in response.data[0]
    assert "is_synced" in response.data[0]


@pytest.mark.django_db
def test_upload_we_ski_gpx_returns_normalized_session(authenticated_client):
    sample_gpx = b"not-used-because-we-ski-is-fixture-backed"
    upload = SimpleUploadedFile(
        "morning-ridge-laps.gpx",
        sample_gpx,
        content_type="application/gpx+xml",
    )

    response = authenticated_client.post(
        "/api/v1/data-integrations/we-ski/gpx-upload/",
        {"file": upload},
        format="multipart",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["provider"] == "we_ski"
    assert response.data["status"] == "accepted"
    assert response.data["source"] == "local_fixture"
    assert response.data["request_file_name"] == "morning-ridge-laps.gpx"
    assert response.data["source_file_name"] == "2026-02-07 10-25 AM We Ski Session.gpx"
    assert len(response.data["available_source_files"]) == 3
    assert len(response.data["available_sessions"]) == 3
    assert response.data["session"]["activity_type"] == "ski"
    assert response.data["session"]["name"] == "Sommet Saint-Sauveur"
    assert response.data["session"]["summary"]["point_count"] > 3
    assert response.data["session"]["summary"]["duration_seconds"] is not None
    assert response.data["session"]["summary"]["total_distance_m"] > 0


@pytest.mark.django_db
def test_upload_we_ski_gpx_ignores_uploaded_content_and_uses_fixture_data(authenticated_client):
    upload = SimpleUploadedFile(
        "invalid.gpx",
        b"<gpx><trk></trk>",
        content_type="application/gpx+xml",
    )

    response = authenticated_client.post(
        "/api/v1/data-integrations/we-ski/gpx-upload/",
        {"file": upload},
        format="multipart",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["source_file_name"] == "2026-02-07 10-25 AM We Ski Session.gpx"
    assert response.data["session"]["name"] == "Sommet Saint-Sauveur"


@pytest.mark.django_db
def test_upload_we_ski_gpx_requires_file_field(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/data-integrations/we-ski/gpx-upload/",
        {},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "file" in response.data


def test_we_ski_validator_repairs_missing_coordinates_and_filters_bad_points():
    validator = WeSkiGpxValidator()
    base_time = datetime(2026, 2, 7, 15, 25, 40)
    session = ParsedSession(
        start_time=None,
        end_time=None,
        track_name="Validation Example",
        bounds=None,
        points=[
            TrackPoint(time=base_time, lat=45.0, lon=-74.0, ele=100.0),
            TrackPoint(time=base_time + timedelta(seconds=10), lat=None, lon=None, ele=101.0),
            TrackPoint(time=base_time + timedelta(seconds=20), lat=45.0002, lon=-74.0002, ele=102.0),
            TrackPoint(time=base_time + timedelta(seconds=30), lat=999.0, lon=0.0, ele=103.0),
        ],
    )

    cleaned_session = validator.validate(session, max_gap_seconds=30)

    assert len(cleaned_session.points) == 3
    assert cleaned_session.start_time == base_time
    assert cleaned_session.end_time == base_time + timedelta(seconds=20)
    assert cleaned_session.bounds is not None
    assert cleaned_session.points[1].lat is not None
    assert cleaned_session.points[1].lon is not None
    assert cleaned_session.points[1].lat == pytest.approx(45.0001)
    assert cleaned_session.points[1].lon == pytest.approx(-74.0001)

