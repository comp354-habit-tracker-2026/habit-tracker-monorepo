from rest_framework import serializers

from goals.business import GoalService
from goals.models import Goal


MAX_DISTANCE_TARGET = 1000


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

    def validate(self, attrs):
        target_value = attrs.get("target_value", getattr(self.instance, "target_value", None))
        goal_type = attrs.get("goal_type", getattr(self.instance, "goal_type", None))

        if target_value is not None and target_value <= 0:
            raise serializers.ValidationError(
                {"target_value": "Target value must be greater than 0."}
            )

        if (
            target_value is not None
            and goal_type == "distance"
            and target_value > MAX_DISTANCE_TARGET
        ):
            raise serializers.ValidationError(
                {
                    "target_value": (
                        "Distance goals must be realistic. "
                        f"Please use a value up to {MAX_DISTANCE_TARGET}."
                    )
                }
            )

        return attrs


# Backwards-compatible naming alias.
GoalSerialiser = GoalSerializer
