class UserScopedCreateMixin:
    """Automatically assign the authenticated user on object creation."""

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        transaction.on_commit(lambda: emit_event(
            event_type="activity.created",
            payload={
            "activity_id": activity.id,
            "user_id": self.request.user.id,
            "activity_type": activity.activity_type,
            },
            idempotency_key=f"activity.created:{activity.id}",
        )   
    )
