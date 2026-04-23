from notifications.models import Notification


class NotificationRepository:
    LIST_FIELDS = (
        "id",
        "notification_type",
        "title",
        "message",
        "is_read",
        "created_at",
        "goal_id",
        "payload",
    )

    def create_notification(self, **kwargs):
        return Notification.objects.create(**kwargs)

    def list_recent(self, user):
        return list(
            Notification.objects.filter(user=user)
            .order_by("-created_at", "-id")
            .values(*self.LIST_FIELDS)
        )
