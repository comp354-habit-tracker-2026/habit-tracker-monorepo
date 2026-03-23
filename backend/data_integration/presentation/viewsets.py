from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from data_integration.business import DataIntegrationService
from data_integration.serializers import DataIntegrationSerializer


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
