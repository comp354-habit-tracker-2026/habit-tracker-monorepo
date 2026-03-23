class UserScopedCreateMixin:
    """Automatically assign the authenticated user on object creation."""

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
