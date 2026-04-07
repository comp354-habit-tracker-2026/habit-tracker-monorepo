from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from core.presentation import UserScopedCreateMixin
from goals.business import GoalService
from goals.serializers import GoalSerializer


class GoalViewSet(UserScopedCreateMixin, viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "description", "goal_type", "status"]
    ordering_fields = ["created_at", "updated_at", "target_value", "current_value", "start_date", "end_date"]
    ordering = ["-created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = GoalService()

    def get_queryset(self):
        return self.service.get_user_queryset(self.request.user, self.request.query_params)

    @action(detail=True, methods=['get'], url_path='progress')
    def progress(self, request, pk=None):
        result = self.service.get_goal_progress(pk, request.user)

        if result == "not_found":
            return Response({"detail": "Goal not found."}, status=status.HTTP_404_NOT_FOUND)
        if result == "forbidden":
            return Response({"detail": "You do not have permission to view this goal."}, status=status.HTTP_403_FORBIDDEN)
        if result == "invalid_id":
            return Response({"detail": "Invalid goal ID."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)
