from rest_framework import serializers
from .models import Goal

class GoalSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'title', 'description', 'target_value', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
