from django.contrib.auth import get_user_model
from core.data import BaseRepository
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def create_user(self, **user_data):
        return self.model.objects.create_user(**user_data)

    def update_user(self, user_id, **user_data):
        """
        Update a user's profile: name, height, weight, avatar.
        Validates inputs before saving.
        """
        user = self.model.objects.filter(id=user_id).first()
        if not user:
            raise ValidationError(f"User with id {user_id} does not exist.")

        # Update name if provided
        name = user_data.get("name")
        if name:
            user.name = name

        # Update height if provided (must be positive)
        height = user_data.get("height")
        if height is not None:
            if height <= 0:
                raise ValidationError("Height must be positive.")
            user.height = height

        # Update weight if provided (must be positive)
        weight = user_data.get("weight")
        if weight is not None:
            if weight <= 0:
                raise ValidationError("Weight must be positive.")
            user.weight = weight

        # Update avatar if provided
        avatar = user_data.get("avatar")
        if avatar:
            user.avatar = avatar

        user.save()
        return user
