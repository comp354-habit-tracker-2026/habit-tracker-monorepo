from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.exceptions import APIException

from core.business import BaseService
from users.data import UserRepository


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 30

class UserService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def register_user(self, validated_data):
        validated_data.pop("password2", None)
        return self.repository.create_user(**validated_data)


    def check_lockout(self, username):
        """
        Checks if account is locked.
        Raises 423 if locked, does nothing if not locked.
        """
        user = self.repository.get_by_username(username)

        if user is None:
            return  # user doesn't exist, let SimpleJWT handle the 401

        if user.locked_until and user.locked_until > timezone.now():
            raise AccountLockedException()

    def record_failed_attempt(self, username):
        user = self.repository.get_by_username(username)

        if user is None:
            return

        self.repository.increment_failed_attempts(user)
        user.refresh_from_db()  # get updated count from database

        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            self.repository.lock_account(user)  # separate method just for locking

    def record_successful_login(self, username):
        """
        Resets failed attempts after successful login.
        """
        user = self.repository.get_by_username(username)

        if user is None:
            return

        self.repository.reset_failed_attempts(user)


class AccountLockedException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = "Account temporarily locked due to too many failed attempts. Try again in 30 minutes."
    default_code = "account_locked"
      
