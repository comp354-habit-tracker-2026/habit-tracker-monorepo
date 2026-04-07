from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from gamification.business import GamificationService
from gamification.models import Badge, Milestone
from gamification.serializers import (
    BadgeSerializer,
    UserBadgeSerializer,
    StreakSerializer,
    MilestoneSerializer,
    UserMilestoneSerializer,
    GamificationSummarySerializer,
    BadgeProgressSerializer,
    MilestoneProgressSerializer,
    EvaluateResponseSerializer,
)


class BadgeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """List all available badges, or the current user's earned badges."""
    serializer_class = BadgeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Badge.objects.all()

    @action(detail=False, methods=['get'], url_path='earned')
    def earned(self, request):
        """GET /api/v1/gamification/badges/earned/ -- badges this user has earned."""
        service = GamificationService()
        earned = service.badge_repo.get_earned_badges(request.user)
        serializer = UserBadgeSerializer(earned, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='progress')
    def progress(self, request):
        """GET /api/v1/gamification/badges/progress/ -- progress towards all badges."""
        service = GamificationService()
        progress = service.get_badge_progress(request.user)
        serializer = BadgeProgressSerializer(progress, many=True)
        return Response(serializer.data)


class MilestoneViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """List all milestones, or the current user's reached milestones."""
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Milestone.objects.all()

    @action(detail=False, methods=['get'], url_path='reached')
    def reached(self, request):
        """GET /api/v1/gamification/milestones/reached/ -- milestones this user reached."""
        service = GamificationService()
        reached = service.milestone_repo.get_reached_milestones(request.user)
        serializer = UserMilestoneSerializer(reached, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='progress')
    def progress(self, request):
        """GET /api/v1/gamification/milestones/progress/ -- progress towards all milestones."""
        service = GamificationService()
        progress = service.get_milestone_progress(request.user)
        serializer = MilestoneProgressSerializer(progress, many=True)
        return Response(serializer.data)


class StreakViewSet(viewsets.ViewSet):
    """Get the current user's streak info."""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/v1/gamification/streaks/"""
        service = GamificationService()
        streak = service.get_streak(request.user)
        serializer = StreakSerializer(streak)
        return Response(serializer.data)


class SummaryViewSet(viewsets.ViewSet):
    """Single endpoint that returns all gamification data for the current user."""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/v1/gamification/summary/"""
        service = GamificationService()
        summary = service.get_user_summary(request.user)
        serializer = GamificationSummarySerializer(summary)
        return Response(serializer.data)


class EvaluateViewSet(viewsets.ViewSet):
    """Manually trigger achievement evaluation for the current user.

    This lets Group 9 (Activity Service) or other groups explicitly
    trigger a re-evaluation after bulk imports or data corrections,
    rather than relying solely on the post_save signal.
    """
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """POST /api/v1/gamification/evaluate/

        Request body (optional):
        {
            "activity_id": 123  // specific activity to evaluate against
        }
        """
        from activities.models import Activity

        service = GamificationService()
        user = request.user
        activity_id = request.data.get('activity_id')

        if activity_id:
            try:
                activity = Activity.objects.get(pk=activity_id, user=user)
            except Activity.DoesNotExist:
                return Response(
                    {'error': 'Activity not found'},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            activity = Activity.objects.filter(user=user).order_by('-date').first()
            if not activity:
                return Response(
                    {'error': 'No activities found for user'},
                    status=status.HTTP_404_NOT_FOUND,
                )

        streak = service.update_streak(user, activity.date)
        new_badges = service.evaluate_badges(user, activity)
        new_milestones = service.evaluate_milestones(user)

        serializer = EvaluateResponseSerializer({
            'new_badges': new_badges,
            'new_milestones': new_milestones,
            'streak': streak,
        })
        return Response(serializer.data, status=status.HTTP_200_OK)
