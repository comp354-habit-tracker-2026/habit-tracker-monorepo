from django.db import transaction
from activities.emit_event import emit_event

class UserScopedCreateMixin:
    """Automatically assign the authenticated user on object creation."""

    def perform_create(self, serializer):
        activity = serializer.save(user=self.request.user)
        emit_event(
            event_type="activity.created",
            payload={
                "activity_id": str(activity.id),
                "user_id":     str(self.request.user.id),
                "provider":    activity.provider,
                "timestamp":   activity.created_at.isoformat(),
            },
            idempotency_key=f"activity.created:{activity.id}",
        )
