from unittest.mock import MagicMock, patch
from datetime import timedelta
from django.utils import timezone
import pytest
from rest_framework.exceptions import AuthenticationFailed
from users.business.services import UserService, MAX_FAILED_ATTEMPTS, AccountLockedException


def test_check_lockout_user_not_found():
    """User doesn't exist — should do nothing, let SimpleJWT handle it"""
    mock_repo = MagicMock()
    mock_repo.get_by_username.return_value = None
    service = UserService(repository=mock_repo)

    # should not raise anything
    service.check_lockout("nonexistent")


def test_check_lockout_account_is_locked():
    """Account is locked — should raise AuthenticationFailed"""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.locked_until = timezone.now() + timedelta(minutes=10)
    mock_repo.get_by_username.return_value = mock_user
    service = UserService(repository=mock_repo)

    with pytest.raises(AccountLockedException):
        service.check_lockout("lockeduser")


def test_check_lockout_lock_expired():
    """Lock has expired — should do nothing"""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.locked_until = timezone.now() - timedelta(minutes=10)
    mock_repo.get_by_username.return_value = mock_user
    service = UserService(repository=mock_repo)

    # should not raise anything
    service.check_lockout("expireduser")


def test_record_failed_attempt_increments():
    """Failed attempt should call increment on repository"""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.failed_login_attempts = 1  # set as integer
    mock_repo.get_by_username.return_value = mock_user
    service = UserService(repository=mock_repo)

    service.record_failed_attempt("testuser")

    mock_repo.increment_failed_attempts.assert_called_once_with(mock_user)


def test_record_failed_attempt_user_not_found():
    """User doesn't exist — should do nothing"""
    mock_repo = MagicMock()
    mock_repo.get_by_username.return_value = None
    service = UserService(repository=mock_repo)

    # should not raise anything
    service.record_failed_attempt("nonexistent")


def test_record_successful_login_resets_attempts():
    """Successful login should reset failed attempts"""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_repo.get_by_username.return_value = mock_user
    service = UserService(repository=mock_repo)

    service.record_successful_login("testuser")

    mock_repo.reset_failed_attempts.assert_called_once_with(mock_user)