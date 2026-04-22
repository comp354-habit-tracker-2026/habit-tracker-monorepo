import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from users.business.services import UserRegistrationService, MAX_FAILED_ATTEMPTS, AccountLockedException


User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return _create_user

@pytest.mark.django_db
class TestAccountLockout:

    def test_successful_login_returns_200(self, api_client, create_user):
        """Valid credentials return tokens"""
        create_user()
        response = api_client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_failed_login_returns_401(self, api_client, create_user):
        """Wrong password returns 401"""
        create_user()
        response = api_client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_account_locks_after_5_attempts(self, api_client, create_user):
        """Account locks after 5 consecutive failed attempts"""
        create_user()
        for _ in range(5):
            api_client.post('/api/v1/auth/login/', {
                'username': 'testuser',
                'password': 'wrongpassword'
            }, format='json')

        # 6th attempt should return 423
        response = api_client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        }, format='json')
        assert response.status_code == status.HTTP_423_LOCKED

    def test_locked_account_cannot_login_with_correct_password(self, api_client, create_user):
        """Even correct password fails when account is locked"""
        user = create_user()
        user.failed_login_attempts = 5
        user.locked_until = timezone.now() + timedelta(minutes=30)
        user.save()

        response = api_client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        }, format='json')
        assert response.status_code == status.HTTP_423_LOCKED

    def test_successful_login_resets_failed_attempts(self, api_client, create_user):
        """Successful login clears the failed attempt counter"""
        user = create_user()
        user.failed_login_attempts = 3
        user.save()

        api_client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        }, format='json')

        user.refresh_from_db()
        assert user.failed_login_attempts == 0
        assert user.locked_until is None

    def test_lock_expires_after_30_minutes(self, api_client, create_user):
        """Account unlocks automatically after lockout duration"""
        user = create_user()
        user.failed_login_attempts = 5
        user.locked_until = timezone.now() - timedelta(minutes=31)  # lock expired
        user.save()

        response = api_client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        }, format='json')
        assert response.status_code == status.HTTP_200_OK