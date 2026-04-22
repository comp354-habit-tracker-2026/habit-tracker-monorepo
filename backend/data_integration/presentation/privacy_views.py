import logging

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import UntypedToken

from data_integration.models import PrivacyAuditLog, PrivacyStatus

logger = logging.getLogger(__name__)
User = get_user_model()


class PrivacyVerifySerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    providerId = serializers.CharField(max_length=64)
    scope = serializers.CharField(max_length=128)


class PrivacyUpdateSerializer(PrivacyVerifySerializer):
    privacyEnabled = serializers.BooleanField()


class PrivacyHistoryQuerySerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    providerId = serializers.CharField(max_length=64, required=False)
    scope = serializers.CharField(max_length=128, required=False)


class PrivacyAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyAuditLog
        fields = [
            "caller_service",
            "requested_user_id",
            "provider_id",
            "scope",
            "decision",
            "reason",
            "action",
            "created_at",
        ]


class ServiceJwtAuthMixin:
    permission_classes = [AllowAny]
    authentication_classes = []

    @staticmethod
    def authenticate_service(request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None, Response({"detail": "Missing Bearer token."}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = UntypedToken(token).payload
        except TokenError:
            return None, Response({"detail": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)

        caller_service = payload.get("service_name") or payload.get("caller_service") or payload.get("sub")
        if not caller_service:
            return None, Response(
                {"detail": "Service token is missing service identity claim."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return caller_service, None


class PrivacyVerifyView(ServiceJwtAuthMixin, APIView):
    def post(self, request):
        caller_service, auth_error = self.authenticate_service(request)
        if auth_error is not None:
            return auth_error

        serializer = PrivacyVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["userId"]
        provider_id = serializer.validated_data["providerId"]
        scope = serializer.validated_data["scope"]

        try:
            record = PrivacyStatus.objects.filter(
                user_id=user_id,
                provider_id=provider_id,
                scope=scope,
            ).first()

            if record is None:
                allowed = False
                reason = "PRIVACY_RECORD_NOT_FOUND"
                decision = PrivacyAuditLog.Decision.DENY
            elif record.is_enabled:
                allowed = False
                reason = "PRIVACY_ENABLED"
                decision = PrivacyAuditLog.Decision.DENY
            else:
                allowed = True
                reason = "PRIVACY_DISABLED"
                decision = PrivacyAuditLog.Decision.ALLOW

            PrivacyAuditLog.objects.create(
                caller_service=caller_service,
                requested_user_id=user_id,
                provider_id=provider_id,
                scope=scope,
                decision=decision,
                reason=reason,
                action=PrivacyAuditLog.Action.VERIFY,
            )

            history = PrivacyAuditLog.objects.filter(
                requested_user_id=user_id,
                provider_id=provider_id,
                scope=scope,
            )
            history_payload = PrivacyAuditLogSerializer(history, many=True).data

            return Response(
                {
                    "allowed": allowed,
                    "reason": reason,
                    "history": history_payload,
                },
                status=status.HTTP_200_OK,
            )
        except DatabaseError:
            logger.exception("Database failure while verifying privacy decision.")
            return Response({"detail": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PrivacyUpdateView(ServiceJwtAuthMixin, APIView):
    def post(self, request):
        caller_service, auth_error = self.authenticate_service(request)
        if auth_error is not None:
            return auth_error

        serializer = PrivacyUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["userId"]
        provider_id = serializer.validated_data["providerId"]
        scope = serializer.validated_data["scope"]
        privacy_enabled = serializer.validated_data["privacyEnabled"]

        try:
            if not User.objects.filter(id=user_id).exists():
                return Response({"detail": "Unknown userId."}, status=status.HTTP_400_BAD_REQUEST)

            PrivacyStatus.objects.update_or_create(
                user_id=user_id,
                provider_id=provider_id,
                scope=scope,
                defaults={"is_enabled": privacy_enabled},
            )

            decision = (
                PrivacyAuditLog.Decision.DENY
                if privacy_enabled
                else PrivacyAuditLog.Decision.ALLOW
            )
            reason = "PRIVACY_ENABLED" if privacy_enabled else "PRIVACY_DISABLED"

            PrivacyAuditLog.objects.create(
                caller_service=caller_service,
                requested_user_id=user_id,
                provider_id=provider_id,
                scope=scope,
                decision=decision,
                reason=reason,
                action=PrivacyAuditLog.Action.UPDATE,
            )

            return Response(
                {
                    "userId": user_id,
                    "providerId": provider_id,
                    "scope": scope,
                    "privacyEnabled": privacy_enabled,
                },
                status=status.HTTP_200_OK,
            )
        except DatabaseError:
            logger.exception("Database failure while updating privacy status.")
            return Response({"detail": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PrivacyHistoryView(ServiceJwtAuthMixin, APIView):
    def get(self, request):
        caller_service, auth_error = self.authenticate_service(request)
        if auth_error is not None:
            return auth_error

        serializer = PrivacyHistoryQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["userId"]
        provider_id = serializer.validated_data.get("providerId")
        scope = serializer.validated_data.get("scope")

        try:
            query = PrivacyAuditLog.objects.filter(requested_user_id=user_id)
            if provider_id:
                query = query.filter(provider_id=provider_id)
            if scope:
                query = query.filter(scope=scope)

            PrivacyAuditLog.objects.create(
                caller_service=caller_service,
                requested_user_id=user_id,
                provider_id=provider_id or "*",
                scope=scope or "*",
                decision=PrivacyAuditLog.Decision.INFO,
                reason="HISTORY_RETRIEVED",
                action=PrivacyAuditLog.Action.HISTORY,
            )

            return Response(PrivacyAuditLogSerializer(query, many=True).data, status=status.HTTP_200_OK)
        except DatabaseError:
            logger.exception("Database failure while retrieving privacy history.")
            return Response({"detail": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
