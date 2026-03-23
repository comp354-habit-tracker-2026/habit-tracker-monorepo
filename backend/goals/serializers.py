from rest_framework import serializers

from goals.business import GoalService
from goals.models import Goal


class GoalSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Goal
        fields = [
            "id",
            "title",
            "description",
            "target_value",
            "current_value",
            "goal_type",
            "status",
            "start_date",
            "end_date",
            "progress_percentage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "progress_percentage"]

    def get_progress_percentage(self, obj):
        return GoalService.progress_percentage(obj.current_value, obj.target_value)


# Backwards-compatible naming alias.
GoalSerialiser = GoalSerializer
