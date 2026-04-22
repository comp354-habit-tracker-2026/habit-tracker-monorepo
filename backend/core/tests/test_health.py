import builtins

import pytest
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

from core.health_service import HealthCheckService


@pytest.fixture
def api_client():
    return APIClient()


class _DummyCursor:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql):
        self.last_sql = sql

    def fetchone(self):
        return (1,)


class _DummyConnection:
    def cursor(self):
        return _DummyCursor()


@pytest.mark.django_db
class TestHealthCheckService:
    def test_check_database_healthy(self, monkeypatch):
        monkeypatch.setattr("core.health_service.connection", _DummyConnection())

        result = HealthCheckService.check_database()

        assert result["status"] == "healthy"
        assert result["message"] == "Database is responding"
        assert "timestamp" in result

    def test_check_database_unhealthy(self, monkeypatch):
        class _FailingConnection:
            def cursor(self):
                raise RuntimeError("db down")

        monkeypatch.setattr("core.health_service.connection", _FailingConnection())

        result = HealthCheckService.check_database()

        assert result["status"] == "unhealthy"
        assert result["message"] == "Database check failed"
        assert "timestamp" in result

    def test_check_migrations_healthy(self):
        with patch("django.core.management.call_command") as call_command:
            result = HealthCheckService.check_migrations()

        call_command.assert_called_once()
        assert result["status"] == "healthy"
        assert result["message"] == "All migrations applied"

    def test_check_migrations_unhealthy(self):
        with patch("django.core.management.call_command", side_effect=Exception("boom")):
            result = HealthCheckService.check_migrations()

        assert result["status"] == "unhealthy"
        assert result["message"] == "Migration check failed"

    def test_check_user_model_healthy(self):
        result = HealthCheckService.check_user_model()

        assert result["status"] == "healthy"
        assert "User model accessible" in result["message"]

    def test_check_user_model_unhealthy(self):
        with patch("core.health_service.User.objects.count", side_effect=Exception("boom")):
            result = HealthCheckService.check_user_model()

        assert result["status"] == "unhealthy"
        assert result["message"] == "User model check failed"

    def test_check_installed_apps_healthy(self):
        with override_settings(
            INSTALLED_APPS=[
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "rest_framework",
                "users",
                "activities",
                "goals",
                "analytics",
            ]
        ):
            result = HealthCheckService.check_installed_apps()

        assert result["status"] == "healthy"
        assert "All required apps installed" in result["message"]

    def test_check_installed_apps_unhealthy(self):
        with override_settings(
            INSTALLED_APPS=[
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "rest_framework",
            ]
        ):
            result = HealthCheckService.check_installed_apps()

        assert result["status"] == "unhealthy"
        assert "Missing apps:" in result["message"]

    def test_check_rest_framework_healthy(self):
        result = HealthCheckService.check_rest_framework()

        assert result["status"] == "healthy"
        assert result["message"] == "Django REST Framework installed"

    def test_check_rest_framework_unhealthy(self):
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "rest_framework":
                raise ImportError("missing")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            result = HealthCheckService.check_rest_framework()

        assert result["status"] == "unhealthy"
        assert result["message"] == "Django REST Framework not installed"

    def test_check_jwt_auth_healthy(self):
        result = HealthCheckService.check_jwt_auth()

        assert result["status"] == "healthy"
        assert result["message"] == "JWT authentication installed"

    def test_check_jwt_auth_unhealthy(self):
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "rest_framework_simplejwt.tokens":
                raise ImportError("missing")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            result = HealthCheckService.check_jwt_auth()

        assert result["status"] == "unhealthy"
        assert result["message"] == "JWT authentication not installed"

    def test_get_full_status_healthy(self):
        with patch("core.health_service.HealthCheckService.check_database", return_value={"status": "healthy"}), patch(
            "core.health_service.HealthCheckService.check_migrations", return_value={"status": "healthy"}
        ), patch("core.health_service.HealthCheckService.check_user_model", return_value={"status": "healthy"}), patch(
            "core.health_service.HealthCheckService.check_installed_apps", return_value={"status": "healthy"}
        ), patch("core.health_service.HealthCheckService.check_rest_framework", return_value={"status": "healthy"}), patch(
            "core.health_service.HealthCheckService.check_jwt_auth", return_value={"status": "healthy"}
        ):
            result = HealthCheckService.get_full_status()

        assert result["status"] == "healthy"
        assert result["summary"]["total"] == 6
        assert result["summary"]["healthy"] == 6
        assert result["summary"]["unhealthy"] == 0

    def test_get_full_status_unhealthy(self):
        with patch("core.health_service.HealthCheckService.check_database", return_value={"status": "unhealthy"}), patch(
            "core.health_service.HealthCheckService.check_migrations", return_value={"status": "healthy"}
        ), patch("core.health_service.HealthCheckService.check_user_model", return_value={"status": "healthy"}), patch(
            "core.health_service.HealthCheckService.check_installed_apps", return_value={"status": "healthy"}
        ), patch("core.health_service.HealthCheckService.check_rest_framework", return_value={"status": "healthy"}), patch(
            "core.health_service.HealthCheckService.check_jwt_auth", return_value={"status": "healthy"}
        ):
            result = HealthCheckService.get_full_status()

        assert result["status"] == "unhealthy"
        assert result["summary"]["total"] == 6
        assert result["summary"]["healthy"] == 5
        assert result["summary"]["unhealthy"] == 1


@pytest.mark.django_db
class TestHealthViews:
    def test_health_status_view_returns_200_when_healthy(self, api_client):
        with patch("core.health_views.HealthCheckService.get_full_status", return_value={"status": "healthy"}):
            response = api_client.get("/api/v1/health/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "healthy"

    def test_health_status_view_returns_503_when_unhealthy(self, api_client):
        with patch("core.health_views.HealthCheckService.get_full_status", return_value={"status": "unhealthy"}):
            response = api_client.get("/api/v1/health/")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data["status"] == "unhealthy"

    def test_health_ready_view_returns_200(self, api_client):
        with patch("django.db.connection", _DummyConnection()):
            response = api_client.get("/api/v1/health/ready/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "ready"

    def test_health_ready_view_returns_503_on_error(self, api_client):
        class _FailingConnection:
            def cursor(self):
                raise RuntimeError("db down")

        with patch("django.db.connection", _FailingConnection()):
            response = api_client.get("/api/v1/health/ready/")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data["status"] == "not_ready"
        assert response.data["error"] == "Readiness check failed"

    def test_health_live_view_returns_200(self, api_client):
        response = api_client.get("/api/v1/health/live/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "alive"
