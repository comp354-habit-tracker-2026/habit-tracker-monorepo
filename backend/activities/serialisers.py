from activities.serializers import ActivitySerializer, ActivitySerialiser

__all__ = ["ActivitySerializer", "ActivitySerialiser"]

def validate_duration(self, value):
    if value <= 0:
        raise serializers.ValidationError("Duration must be greater than 0")
    return value

def validate_distance(self, value):
    if value is not None and float(value) < 0:
        raise serializers.ValidationError("Distance cannot be negative")
    return value