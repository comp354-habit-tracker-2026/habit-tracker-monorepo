from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from activities.business import ActivityService
from activities.serializers import ActivitySerializer


class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    # Provider is now on ConnectedAccount, so we search through account__provider
    search_fields = ["activity_type", "account__provider", "external_id"]
    ordering_fields = ["date", "created_at", "duration", "calories", "distance"]
    ordering = ["-date", "-created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ActivityService()

    def get_queryset(self):
        return self.service.get_user_queryset(self.request.user, self.request.query_params)

    def perform_create(self, serializer):
        # Account ownership is already validated by the serializer's filtered queryset
        serializer.save()
