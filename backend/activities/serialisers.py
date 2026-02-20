from rest_framework import serializers
from .models import Activity

class ActivitySerialiser(serializers.ModelSerializer):
    raw_data = serializers.JSONField(required=False)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'activity_type', 'duration', 'date', 'provider',
            'external_id', 'distance', 'calories', 'raw_data',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def validate(self, data):
        # Prevent duplicate external activities
        if data.get('external_id') and data.get('provider') != 'manual':
            existing = Activity.objects.filter(
                provider=data['provider'],
                external_id=data['external_id']
            )
            # Exclude current instance when updating
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError(
                    "Activity with this external ID already exists for this provider."
                )
        return data
