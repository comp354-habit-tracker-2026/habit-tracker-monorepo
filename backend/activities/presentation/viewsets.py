from rest_framework import viewsets, status  
from rest_framework.response import Response 
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from activities.business import ActivityService
from activities.serializers import ActivitySerializer
from core.presentation import UserScopedCreateMixin


class ActivityViewSet(UserScopedCreateMixin, viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["activity_type", "provider", "external_id"]
    ordering_fields = ["date", "created_at", "duration", "calories", "distance"]
    ordering = ["-date", "-created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ActivityService()

    def get_queryset(self):
        return self.service.get_user_queryset(self.request.user, self.request.query_params)
    
    # viewsets.py  ← only HTTP concerns here
    def destroy(self, request, *args, **kwargs):
        self.service.delete_activity(activity_id=kwargs['pk'], user=request.user)
        return Response({"message": "Activity successfully deleted"}, status=status.HTTP_200_OK)

