from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.presentation import UserScopedCreateMixin
from goals.business import GoalService
from goals.serializers import GoalSerializer
from goals.models import Goal


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

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/v1/goals/{id}/
        Deletes a goal belonging to the authenticated user.
        Returns 204 No Content on success, 404 if not found.
        """
        pk = kwargs.get('pk')
        goal = Goal.objects.filter(id=pk, user=request.user).first() # pylint: disable=no-member
        if goal is None:
            return Response(
                {"detail": "Goal not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        goal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
