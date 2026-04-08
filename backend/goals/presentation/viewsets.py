from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from core.presentation import UserScopedCreateMixin
from core.presentation.permissions import IsAdminOrOwner
from goals.business import GoalService
from goals.serializers import GoalSerializer


class GoalViewSet(UserScopedCreateMixin, viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "description", "goal_type", "status"]
    ordering_fields = ["created_at", "updated_at", "target_value", "current_value", "start_date", "end_date"]
    ordering = ["-created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = GoalService()

    def get_queryset(self):
        return self.service.get_user_queryset(self.request.user, self.request.query_params)
