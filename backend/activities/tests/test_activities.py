import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from activities.models import Activity, ConnectedAccount
from datetime import date

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


@pytest.fixture
def create_connected_account():
    """Creates a connected account (e.g. a user's linked Strava profile)."""
    def _create(user, provider='strava', external_user_id='ext_123', **kwargs):
        return ConnectedAccount.objects.create(
            user=user,
            provider=provider,
            external_user_id=external_user_id,
            **kwargs,
        )
    return _create


@pytest.fixture
def authenticated_client(api_client, create_user, create_connected_account):
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    api_client.user = user
    # Give the test user a default connected account to create activities with
    api_client.account = create_connected_account(user)
    return api_client


@pytest.fixture
def create_activity():
    def _create_activity(account, **kwargs):
        defaults = {
            'activity_type': 'Running',
            'duration': 30,
            'date': date.today(),
        }
        defaults.update(kwargs)
        return Activity.objects.create(account=account, **defaults)
    return _create_activity


@pytest.mark.django_db
class TestActivities:
    def test_create_activity(self, authenticated_client):
        """Test creating an activity linked to a connected account"""
        data = {
            'account': authenticated_client.account.pk,
            'activity_type': 'Running',
            'duration': 45,
            'date': date.today().isoformat(),
            'distance': '10.5',
            'calories': 450,
        }
        response = authenticated_client.post('/api/v1/activities/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        activity = Activity.objects.get(activity_type='Running')
        assert activity.account == authenticated_client.account
        assert float(activity.distance) == 10.5
        assert activity.calories == 450

    def test_create_activity_with_external_id(self, authenticated_client):
        """Test creating an activity that came from an external provider"""
        raw_strava_data = {
            'id': 12345,
            'name': 'Morning Run',
            'distance': 5000,
            'moving_time': 1800,
            'total_elevation_gain': 50,
        }
        data = {
            'account': authenticated_client.account.pk,
            'activity_type': 'Running',
            'duration': 30,
            'date': date.today().isoformat(),
            'external_id': '12345',
            'distance': '5.0',
            'raw_data': raw_strava_data,
        }
        response = authenticated_client.post('/api/v1/activities/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        activity = Activity.objects.get(external_id='12345')
        assert activity.account.provider == 'strava'
        assert activity.raw_data['id'] == 12345

    def test_prevent_duplicate_external_activity(self, authenticated_client):
        """Test that the same external activity cannot be imported twice"""
        data = {
            'account': authenticated_client.account.pk,
            'activity_type': 'Running',
            'duration': 30,
            'date': date.today().isoformat(),
            'external_id': '12345',
        }
        response1 = authenticated_client.post('/api/v1/activities/', data, format='json')
        assert response1.status_code == status.HTTP_201_CREATED

        response2 = authenticated_client.post('/api/v1/activities/', data, format='json')
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_activities_with_pagination(self, authenticated_client, create_activity):
        """Test that the activity list is paginated"""
        for i in range(25):
            create_activity(
                authenticated_client.account,
                activity_type=f'Activity {i}',
                date=date.today(),
            )
        response = authenticated_client.get('/api/v1/activities/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert 'next' in response.data
        assert len(response.data['results']) == 20  # Default page size

    def test_list_activities_only_own(self, authenticated_client, create_user,
                                      create_connected_account, create_activity):
        """Test that a user can only see their own activities, not other users'"""
        other_user = create_user(username='otheruser', email='other@example.com')
        other_account = create_connected_account(other_user, external_user_id='other_ext')

        create_activity(other_account, activity_type='Swimming')
        create_activity(authenticated_client.account, activity_type='Running')

        response = authenticated_client.get('/api/v1/activities/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['activity_type'] == 'Running'

    def test_filter_activities_by_provider(self, authenticated_client,
                                            create_user, create_connected_account,
                                            create_activity):
        """Test filtering activities by provider (resolved through the connected account)"""
        user = authenticated_client.user
        strava_account = authenticated_client.account  # provider='strava'
        mapmyrun_account = create_connected_account(
            user, provider='mapmyrun', external_user_id='mmr_ext'
        )

        create_activity(strava_account)
        create_activity(mapmyrun_account)

        response = authenticated_client.get('/api/v1/activities/?provider=strava')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_activity_date_filtering(self, authenticated_client, create_activity):
        """Test filtering activities by date range"""
        from datetime import timedelta
        today = date.today()
        create_activity(authenticated_client.account, date=today - timedelta(days=7))
        create_activity(authenticated_client.account, date=today)
        create_activity(authenticated_client.account, date=today + timedelta(days=7))

        response = authenticated_client.get('/api/v1/activities/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3

    def test_connected_account_str(self, authenticated_client):
        """Test the string representation of a ConnectedAccount"""
        account = authenticated_client.account
        assert str(account) == f"{account.user} via {account.provider}"

    def test_activity_str(self, authenticated_client, create_activity):
        """Test the string representation of an Activity"""
        activity = create_activity(authenticated_client.account)
        expected = f"{activity.activity_type} - {activity.date} ({authenticated_client.account.provider})"
        assert str(activity) == expected
