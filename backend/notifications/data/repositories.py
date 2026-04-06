from notifications.models import Notification, UserNotificationPreference
from core.data import BaseRepository


class NotificationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Notification)

    
class UserPreferenceRepository(BaseRepository):
    def __init__(self):
        super().__init__(UserNotificationPreference)

    def update_user_prefernces(self, user_id, **update_user_prefernces):
        return True
