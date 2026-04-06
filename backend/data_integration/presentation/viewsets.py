from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.business.exceptions import DomainValidationError

from data_integration.business import DataIntegrationService, WeSkiGpxImportService


class DataIntegrationSerializer(serializers.Serializer):
    """
    Minimal serializer for data integration objects.

    This implementation assumes that `DataIntegrationService` returns
    simple dict-like objects and passes them through unchanged.
    """

    def to_representation(self, instance):
        return instance


class WeSkiGpxUploadSerializer(serializers.Serializer):
    """Validate a multipart GPX upload request used to trigger fixture-backed ingestion."""

    file = serializers.FileField(help_text="GPX file exported from the We Ski app.")


class WeSkiGpxUploadResponseSerializer(serializers.Serializer):
    """Pass through a normalized We Ski payload derived from local fixture data."""

    def to_representation(self, instance):
        return instance


class DataIntegrationViewSet(viewsets.ViewSet):
    serializer_class = DataIntegrationSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = DataIntegrationService()
        self.we_ski_service = WeSkiGpxImportService()

    def get_serializer_class(self):
        if getattr(self, "action", None) == "upload_we_ski_gpx":
            return WeSkiGpxUploadSerializer
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        return {"request": self.request, "view": self}

    def list(self, request):
        integrations = self.service.get_user_integrations(request.user, request.query_params)
        serializer = self.serializer_class(integrations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post"],
        url_path="we-ski/gpx-upload",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_we_ski_gpx(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        upload = serializer.validated_data["file"]

        try:
            payload = self.we_ski_service.import_gpx(upload.read(), filename=upload.name)
        except DomainValidationError as exc:
            raise serializers.ValidationError({"file": [exc.message]}) from exc

        response_serializer = WeSkiGpxUploadResponseSerializer(payload)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
