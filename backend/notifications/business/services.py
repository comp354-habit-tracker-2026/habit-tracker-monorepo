from core.business import BaseService
from notifications.data.repositories import NotificationRepository, UserPreferenceRepository


class NotificationService(BaseService):
    def __init__(self, repository=None, user_preferences_service=None):
        self.notification_repository = repository or NotificationRepository()
        self.user_preferences_service = user_preferences_service or UserPreferencesService()

    def notify(title, description, recipient_id, event_type):
        # TODO: validate user exists
        # get_user(recipient_id) is not None


        return
    
    def get_all(user_id):
        return

    def get(notification_id):
        return
    
    def delete(notification_id):
        return
    
    def mark_as_read(notification_id):
        return
    
    def mark_all_as_read(user_id):
        return
    
class UserPreferencesService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or UserPreferenceRepository()

    def update_user_preferences(user_id, **update_user_preferences):
        return
    
    def create_default_user_preferences(user_id):
        return
    
    def get_user_preferences(user_id):
        return
