from core.business import BaseService
from users.data import UserRepository


class UserRegistrationService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def register_user(self, validated_data):
        validated_data.pop("password2", None)
        return self.repository.create_user(**validated_data)



import hashlib
import secrets
from datetime import timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from users.models import User, PasswordResetToken


class PasswordResetService(BaseService):
    TOKEN_EXPIRY_MINUTES = 30

    def _hash_token(self, token):
        return hashlib.sha256(token.encode()).hexdigest()

    def request_reset(self, email):
        user = User.objects.filter(email=email).first()

        if not user:
            return {"message": "If account exists, reset token generated"}

        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)

        PasswordResetToken.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(minutes=30)
        )

        return {
            "message": "Reset token generated",
            "reset_token": raw_token  # dev only
        }

    def confirm_reset(self, token, new_password):
        token_hash = self._hash_token(token)

        record = PasswordResetToken.objects.filter(
            token_hash=token_hash,
            used_at__isnull=True
        ).first()

        if not record:
            raise ValidationError({"token": "Invalid token"})

        if record.is_expired():
            raise ValidationError({"token": "Expired token"})

        user = record.user
        user.set_password(new_password)
        user.save()

        record.used_at = timezone.now()
        record.save()

        return {"message": "Password reset successful"}
