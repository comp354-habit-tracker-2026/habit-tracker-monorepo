from rest_framework import serializers

from .models import FileRecord


class FileRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileRecord
        fields = ["id", "url_link", "file_name", "created_at"]
        read_only_fields = ["id", "created_at"]
