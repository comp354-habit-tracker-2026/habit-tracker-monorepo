# Generated with assistance from ChatGPT (OpenAI), adapted for project needs.

from rest_framework import serializers

from mywhoosh_integration.models import SyncStatus


class SyncStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncStatus
        fields = [
            "user_id",
            "timestamp",
            "status",
            "sessions_imported",
            "duplicates_skipped",
            "error_message",
        ]
