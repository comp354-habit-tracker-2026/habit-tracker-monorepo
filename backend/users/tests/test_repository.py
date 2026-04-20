import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from users.data.repositories import UserRepository, VALID_PROVIDERS
from activities.models import Activity, ConnectedAccount

import random
import string

import pytest

@pytest.mark.django_db
def test_delete_provider_data_valid_provider():
    User = get_user_model()
    user = User.objects.create_user(username='testuser', password='testpass')
    repo = UserRepository()
    provider = list(VALID_PROVIDERS)[0]
    # Create a connected account for this user/provider
    account = ConnectedAccount.objects.create(user=user, provider=provider, external_user_id="dummyid")
    # Create some activities for this account
    for _ in range(3):
        Activity.objects.create(
            account=account,
            activity_type="run",
            duration=30,
            date="2024-01-01"
        )
    result = repo.delete_provider_data(user, provider)
    assert result['deleted_count'] == 3
    assert result['provider'] == provider
    # All activities for this account should be deleted
    assert Activity.objects.filter(account=account).count() == 0

@pytest.mark.django_db
def test_delete_provider_data_invalid_provider():
    User = get_user_model()
    user = User.objects.create_user(username='testuser2', password='testpass')
    repo = UserRepository()
    invalid_provider = 'notarealprovider'
    with pytest.raises(ValueError) as exc:
        repo.delete_provider_data(user, invalid_provider)
    assert 'Unknown or non-deletable provider' in str(exc.value)
