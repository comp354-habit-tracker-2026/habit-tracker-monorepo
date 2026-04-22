from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.exceptions import APIException
import logging
import requests
from urllib.parse import urlencode
from django.conf import settings

from core.business import BaseService
from users.data import UserRepository

logger = logging.getLogger(__name__)


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 30

class UserRegistrationService(BaseService):
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
      
class AccountDeletionService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def delete_account(self, user, password):
        if not user.check_password(password):
            raise ValueError("Invalid password")
        logger.info(
            "Account deletion initiated: user_id=%s, username=%s",
            user.id,
            user.username,
        )
        self.repository.delete_user(user)
        logger.info(
            "Account deleted successfully: user_id=%s, username=%s",
            user.id,
            user.username,
        )

class OAuthService(BaseService):
    """Handles Google OAuth login flow: auth URL generation + callback handling."""

    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def get_google_auth_url(self):
        """Build the URL that redirects users to Google's sign-in page."""
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{self.GOOGLE_AUTH_URL}?{urlencode(params)}"

    def handle_google_callback(self, code):
        """
        Exchange the authorization code for user info,
        then create or link a user account.
        Returns the User object.
        """
        if not code:
            raise ValueError("Missing authorization code")

        token_data = self._exchange_code(code)
        access_token = token_data.get("access_token")
        if not access_token:
            raise ValueError("Invalid or expired authorization code")

        user_info = self._get_user_info(access_token)

        user = self.repository.get_or_create_oauth_user(
            provider="google",
            provider_id=user_info["id"],
            email=user_info["email"],
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
        )
        logger.info("OAuth login successful: user_id=%s, email=%s", user.id, user.email)
        return user

    def _exchange_code(self, code):
        """Exchange the authorization code for an access token from Google."""
        response = requests.post(
            self.GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        if response.status_code != 200:
            raise ValueError("Invalid or expired authorization code")
        return response.json()

    def _get_user_info(self, access_token):
        """Fetch the user's Google profile information using the access token."""
        response = requests.get(
            self.GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        if response.status_code != 200:
            raise ValueError("Failed to retrieve user information")
        return response.json()