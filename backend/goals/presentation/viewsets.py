from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.business import DomainValidationError
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

    @action(detail=True, methods=["get"], url_path="status")
    def status_summary(self, request, pk=None):
        goal = self.service.get_user_goal(request.user, pk)
        if goal is None:
            return Response(
                {"errorCode": "GOAL_NOT_FOUND", "message": "Goal not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            payload = self.service.get_status_summary(goal)
        except DomainValidationError as exc:
            return Response(
                {"errorCode": "GOAL_INVALID", "message": str(exc)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception:
            return Response(
                {
                    "errorCode": "GOAL_STATUS_UNAVAILABLE",
                    "message": "Unable to compute goal status at this time.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(payload, status=status.HTTP_200_OK)
