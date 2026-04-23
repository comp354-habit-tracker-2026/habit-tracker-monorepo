from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.business import DomainValidationError
from core.presentation import UserScopedCreateMixin
from core.presentation.permissions import IsAdminOrOwner
from goals.business import GoalService
from goals.serializers import GoalSerializer
from goals.pagination import GoalPagination


class GoalViewSet(UserScopedCreateMixin, viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    pagination_class = GoalPagination
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

    @action(detail=False, methods=["get"], url_path="status")
    def status_summary(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        goals = page if page is not None else queryset
        
        payloads = []
        for goal in goals:
            try:
                payload = self.service.get_status_summary(goal)
                payloads.append(payload)
            except DomainValidationError:
                payloads.append({
                    "goalId": goal.id,
                    "errorCode": "GOAL_INVALID",
                    "message": "Goal is invalid."
                })
            except Exception:
                payloads.append({
                    "goalId": goal.id,
                    "errorCode": "GOAL_STATUS_UNAVAILABLE",
                    "message": "Unable to compute goal status at this time.",
                })

        if page is not None:
            return self.get_paginated_response(payloads)

        return Response(payloads, status=status.HTTP_200_OK)
