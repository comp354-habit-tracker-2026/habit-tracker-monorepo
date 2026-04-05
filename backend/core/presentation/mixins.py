from django.utils import timezone
from activities.emit_event import emit_event

class UserScopedCreateMixin:
    """Automatically assign the authenticated user on object creation."""

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