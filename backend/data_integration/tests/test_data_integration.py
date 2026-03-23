import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
	return APIClient()


@pytest.fixture
def authenticated_client(api_client):
	user = User.objects.create_user(
		username="integrationuser",
		email="integration@test.com",
		password="TestPass123!",
	)
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

