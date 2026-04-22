from django.contrib.auth import get_user_model

from core.data import BaseRepository

User = get_user_model()


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def create_user(self, **user_data):
        return self.model.objects.create_user(**user_data)
    
    def delete_user(self, user_id):
        return self.model.objects.filter(id=user_id).delete()
