from django.utils import timezone
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from activities.business import ActivityService
from activities.serializers import ActivitySerializer
from activities.emit_event import emit_event
from core.presentation import UserScopedCreateMixin
from core.presentation.permissions import IsAdminOrOwner


class ActivityViewSet(UserScopedCreateMixin, viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["activity_type", "provider", "external_id"]
    ordering_fields = ["date", "created_at", "duration", "calories", "distance"]
    ordering = ["-date", "-created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ActivityService()

    def get_queryset(self):
        return self.service.get_user_queryset(self.request.user, self.request.query_params)

    def perform_create(self, serializer):
        activity = serializer.save(user=self.request.user)

        # populate the OutboxEvent table;
        # dispatcher reads the table
        # and publishes to the queue to update the Analytics teams;
        emit_event(
            event_type="activity.imported",
            payload={
                "activity_id": str(activity.id),
                "user_id": str(self.request.user.id),
                "provider": activity.provider,
                "timestamp": timezone.now().isoformat(),
            },
            idempotency_key=f"activity.imported:{activity.id}",
        )
