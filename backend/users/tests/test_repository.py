import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from users.data.repositories import UserRepository, VALID_PROVIDERS
from activities.models import Activity

import random
import string

import pytest

@pytest.mark.django_db
def test_delete_provider_data_valid_provider():
    User = get_user_model()
    user = User.objects.create_user(username='testuser', password='testpass')
    repo = UserRepository()
    provider = list(VALID_PROVIDERS)[0]
    # Create some activities for this user/provider
    for _ in range(3):
        Activity.objects.create(user=user, provider=provider)
    result = repo.delete_provider_data(user, provider)
    assert result['deleted_count'] == 3
    assert result['provider'] == provider
    assert Activity.objects.filter(user=user, provider=provider).count() == 0

@pytest.mark.django_db
def test_delete_provider_data_invalid_provider():
    User = get_user_model()
    user = User.objects.create_user(username='testuser2', password='testpass')
    repo = UserRepository()
    invalid_provider = 'notarealprovider'
    with pytest.raises(ValueError) as exc:
        repo.delete_provider_data(user, invalid_provider)
    assert 'Unknown or non-deletable provider' in str(exc.value)
