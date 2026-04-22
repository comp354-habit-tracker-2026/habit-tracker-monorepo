from rest_framework.permissions import BasePermission


class IsAdminOrOwner(BasePermission):
    """
    Allow full access to admins; non-admin users can only access their own objects.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True

        owner_id = getattr(obj, "user_id", None)
        return owner_id == request.user.id
