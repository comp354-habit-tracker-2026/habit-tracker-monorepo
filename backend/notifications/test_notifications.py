import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_view_notifications_success():
    client = APIClient()
    response = client.get('/api/v1/notifications/1/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_notifications_empty():
    client = APIClient()
    response = client.get('/api/v1/notifications/9999/')
    assert response.status_code == 200


def test_unauthorized_access():
    client = APIClient()
    response = client.get('/api/v1/notifications/1/')
    assert response.status_code in [401, 403]