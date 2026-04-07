from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from data_integration.models import FileRecord


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        suffix = uuid4().hex[:8]
        defaults = {
            "username": f"user_{suffix}",
            "email": f"user_{suffix}@example.com",
            "password": "TestPass123!",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    api_client.user = user
    return api_client


@pytest.fixture
def admin_client(api_client, create_user):
    admin = create_user(is_staff=True, is_superuser=True)
    refresh = RefreshToken.for_user(admin)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    api_client.user = admin
    return api_client


@pytest.fixture
def create_file_record():
    def _create_file_record(**kwargs):
        defaults = {
            "url_link": "https://example.com/default.csv",
            "file_name": "default.csv",
        }
        defaults.update(kwargs)
        return FileRecord.objects.create(**defaults)

    return _create_file_record


@pytest.mark.django_db
class TestFileRecordCrudApi:
    base_url = "/api/v1/data-integrations/files/"

    def test_requires_authentication(self, api_client):
        response = api_client.get(self.base_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_admin_user_is_forbidden(self, authenticated_client):
        response = authenticated_client.get(self.base_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_create_file_record(self, admin_client):
        payload = {
            "url_link": "https://example.com/report.csv",
            "file_name": "report.csv",
        }

        response = admin_client.post(self.base_url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert FileRecord.objects.filter(file_name="report.csv").exists()
        assert response.data["url_link"] == payload["url_link"]

    def test_admin_can_list_file_records(self, admin_client, create_file_record):
        create_file_record(file_name="alpha.csv", url_link="https://example.com/alpha.csv")
        create_file_record(file_name="beta.csv", url_link="https://example.com/beta.csv")

        response = admin_client.get(self.base_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert len(response.data["results"]) == 2

    def test_admin_can_retrieve_file_record(self, admin_client, create_file_record):
        file_record = create_file_record(file_name="retrieve.csv")

        response = admin_client.get(f"{self.base_url}{file_record.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == file_record.id
        assert response.data["file_name"] == "retrieve.csv"

    def test_admin_can_update_file_record(self, admin_client, create_file_record):
        file_record = create_file_record(file_name="old.csv")

        response = admin_client.patch(
            f"{self.base_url}{file_record.id}/",
            {"file_name": "new.csv"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["file_name"] == "new.csv"

        file_record.refresh_from_db()
        assert file_record.file_name == "new.csv"

    def test_admin_can_delete_file_record(self, admin_client, create_file_record):
        file_record = create_file_record(file_name="delete.csv")

        response = admin_client.delete(f"{self.base_url}{file_record.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not FileRecord.objects.filter(id=file_record.id).exists()

    def test_admin_can_search_file_records(self, admin_client, create_file_record):
        create_file_record(file_name="report-final.csv", url_link="https://example.com/reports/final")
        create_file_record(file_name="invoice.csv", url_link="https://example.com/invoices/1")

        response = admin_client.get(f"{self.base_url}?search=report")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["file_name"] == "report-final.csv"

    def test_admin_can_order_file_records(self, admin_client, create_file_record):
        create_file_record(file_name="z-last.csv", url_link="https://example.com/z")
        create_file_record(file_name="a-first.csv", url_link="https://example.com/a")

        asc_response = admin_client.get(f"{self.base_url}?ordering=file_name")
        desc_response = admin_client.get(f"{self.base_url}?ordering=-file_name")

        assert asc_response.status_code == status.HTTP_200_OK
        assert desc_response.status_code == status.HTTP_200_OK
        assert asc_response.data["results"][0]["file_name"] == "a-first.csv"
        assert desc_response.data["results"][0]["file_name"] == "z-last.csv"
