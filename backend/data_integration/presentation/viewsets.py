<<<<<<< HEAD
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter

from data_integration.business import DataIntegrationService
from data_integration.models import DataConsent, FileRecord
from data_integration.serializers import FileRecordSerializer


# DataConsent API
class DataIntegrationSerializer(serializers.Serializer):
    """
    Minimal serializer for data integration objects.
    This implementation assumes that `DataIntegrationService` returns
    simple dict-like objects and passes them through unchanged.
    """
    def to_representation(self, instance):
        return instance


class DataIntegrationConsentSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=DataConsent.PROVIDER_CHOICES)
    consent_granted = serializers.BooleanField()


class DataIntegrationViewSet(viewsets.ViewSet):
    serializer_class = DataIntegrationSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = DataIntegrationService()

    def list(self, request):
        integrations = self.service.get_user_integrations(request.user, request.query_params)
        serializer = self.serializer_class(integrations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="consent")
    def consent(self, request):
        serializer = DataIntegrationConsentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        consent_granted = serializer.validated_data["consent_granted"]

        try:
            self.service.set_user_consent(request.user, provider, consent_granted)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        integrations = self.service.get_user_integrations(request.user, request.query_params)
        provider_data = next((item for item in integrations if item["provider"] == provider), None)
        return Response(provider_data, status=status.HTTP_200_OK)


# FileRecord API
class FileRecordViewSet(viewsets.ModelViewSet):
    queryset = FileRecord.objects.all()
    serializer_class = FileRecordSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["file_name", "url_link"]
    ordering_fields = ["created_at", "file_name"]
    ordering = ["-created_at"]
