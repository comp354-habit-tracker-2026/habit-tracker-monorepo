from rest_framework import serializers

from activities.business import ActivityService
from activities.models import Activity
from core.business import DomainValidationError


class ActivitySerializer(serializers.ModelSerializer):
    raw_data = serializers.JSONField(required=False)

    class Meta:
        model = Activity
        fields = [
            "id",
            "activity_type",
            "duration",
            "date",
            "provider",
            "external_id",
            "distance",
            "calories",
            "raw_data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        service = ActivityService()
        provider = data.get("provider")
        external_id = data.get("external_id")

        if self.instance is not None:
            provider = provider if provider is not None else self.instance.provider
            external_id = external_id if external_id is not None else self.instance.external_id

        candidate = {
            "provider": provider,
            "external_id": external_id,
        }
        try:
            service.validate_external_activity_uniqueness(candidate, instance=self.instance)
        except DomainValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return data
    
    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0")
        return value

    def validate_distance(self, value):
        if value is not None and float(value) < 0:
            raise serializers.ValidationError("Distance cannot be negative")
        return value


# Backwards-compatible naming alias.
ActivitySerialiser = ActivitySerializer

