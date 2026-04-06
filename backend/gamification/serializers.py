from rest_framework import serializers

from gamification.models import Badge, UserBadge, Streak, Milestone, UserMilestone


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = [
            'id', 'name', 'description', 'icon',
            'badge_type', 'activity_type',
            'threshold', 'metric', 'points',
        ]


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = ['id', 'badge', 'earned_at']


class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = ['current_count', 'longest_count', 'last_activity_date', 'updated_at']


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = [
            'id', 'name', 'description', 'icon',
            'metric', 'threshold', 'activity_type', 'points',
        ]


class UserMilestoneSerializer(serializers.ModelSerializer):
    milestone = MilestoneSerializer(read_only=True)

    class Meta:
        model = UserMilestone
        fields = ['id', 'milestone', 'reached_at']


class BadgeProgressSerializer(serializers.Serializer):
    badge = BadgeSerializer()
    earned = serializers.BooleanField()
    current_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    target_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    progress_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)


class MilestoneProgressSerializer(serializers.Serializer):
    milestone = MilestoneSerializer()
    reached = serializers.BooleanField()
    current_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    target_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    progress_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)


class GamificationSummarySerializer(serializers.Serializer):
    streak = StreakSerializer()
    earned_badges = UserBadgeSerializer(many=True)
    reached_milestones = UserMilestoneSerializer(many=True)
    total_badges = serializers.IntegerField()
    total_milestones = serializers.IntegerField()
    total_points = serializers.IntegerField()


class EvaluateResponseSerializer(serializers.Serializer):
    new_badges = BadgeSerializer(many=True)
    new_milestones = MilestoneSerializer(many=True)
    streak = StreakSerializer()
