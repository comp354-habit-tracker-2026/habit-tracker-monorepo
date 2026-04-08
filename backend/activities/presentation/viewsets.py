from django.utils import timezone
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from activities.business import ActivityService
from activities.emit_event import emit_event
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
        # Account ownership is already validated by the serializer's filtered queryset.
        # Provider is now on the connected account, not directly on the activity.
        activity = serializer.save()

        # Publish an outbox event so analytics teams are notified of the new activity.
        emit_event(
            event_type="activity.imported",
            payload={
                "activity_id": str(activity.id),
                "user_id": str(self.request.user.id),
                "provider": activity.account.provider if activity.account_id else None,
                "timestamp": timezone.now().isoformat(),
            },
            idempotency_key=f"activity.imported:{activity.id}",
        )
