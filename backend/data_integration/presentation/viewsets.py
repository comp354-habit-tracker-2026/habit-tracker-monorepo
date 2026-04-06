from rest_framework import status, viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from data_integration.business import DataIntegrationService


class DataIntegrationSerializer(serializers.Serializer):
    """
    Minimal serializer for data integration objects.

    This implementation assumes that `DataIntegrationService` returns
    simple dict-like objects and passes them through unchanged.
    """

    def to_representation(self, instance):
        return instance
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
