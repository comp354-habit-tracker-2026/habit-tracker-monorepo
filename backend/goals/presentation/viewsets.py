from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
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
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/v1/goals/{id}/
        Deletes a goal belonging to the authenticated user.
        """
        pk = kwargs.get('pk')
        result = self.service.delete_goal(pk, request.user)

        if result == "deleted":
            return Response({"detail": "Goal deleted successfully."}, status=status.HTTP_200_OK)
        if result == "not_found":
            return Response({"detail": "Goal not found."}, status=status.HTTP_404_NOT_FOUND)
        if result == "forbidden":
            return Response({"detail": "You do not have permission to delete this goal."}, status=status.HTTP_403_FORBIDDEN)
        if result == "invalid_id":
            return Response({"detail": "Invalid goal ID format."}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        PUT /api/v1/goals/{id}/
        Updates a goal belonging to the authenticated user.
        """
        pk = kwargs.get("pk")
        result = self.service.update_goal(pk, request.user, request.data)
        if result == "not_found":
            return Response({"detail": "Goal not found."}, status=status.HTTP_404_NOT_FOUND)
        if result == "forbidden":
            return Response({"detail": "You do not have permission to update this goal."}, status=status.HTTP_403_FORBIDDEN)
        if result == "invalid_id":
            return Response({"detail": "Invalid goal ID format."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        POST /api/v1/goals/create/
        Create a new goal that belongs to the authenticated user.
        """
        result = self.service.create_goal(request.user, request.data)

        # Error response maker
        if isinstance(result, dict) and "error" in result:
            status_code = status.HTTP_400_BAD_REQUEST
            
            # Error Code Builder
            if result["error"] == "IntegrityError":
                status_code = status.HTTP_409_CONFLICT
            elif result["error"] == "DatabaseError":
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            return Response({"detail": result["msg"], "type": result["error"]}, status=status_code)
        
        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/v1/goals/{id}/
        Retrieves a specific goal belonging to the authenticated user.
        """
        pk = kwargs.get("pk")
        
        result = self.service.retrieve_goal(pk, request.user)

        if result == "not_found":
            return Response({"detail": "Goal not found."}, status=status.HTTP_404_NOT_FOUND)
        if result == "forbidden":
            return Response({"detail": "You do not have permission to view this goal."}, status=status.HTTP_403_FORBIDDEN)
        if result == "invalid_id":
            return Response({"detail": "Invalid goal ID format."}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)

