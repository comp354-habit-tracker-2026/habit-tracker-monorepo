from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from data_integration.models import FileRecord
from data_integration.serializers import FileRecordSerializer

class FileRecordViewSet(viewsets.ModelViewSet):
    queryset = FileRecord.objects.all()
    serializer_class = FileRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["file_name", "url_link"]
    ordering_fields = ["created_at", "file_name"]
    ordering = ["-created_at"]
