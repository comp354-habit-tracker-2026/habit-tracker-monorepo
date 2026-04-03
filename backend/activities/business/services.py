from core.business import BaseService, DomainValidationError
from activities.data import ActivityRepository
from rest_framework.exceptions import NotFound, PermissionDenied

class ActivityService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or ActivityRepository()

    def get_user_queryset(self, user, params):
        queryset = self.repository.for_user(user)
        return self.repository.apply_filters(queryset, params)

    def validate_external_activity_uniqueness(self, data, instance=None):
        provider = data.get("provider")
        external_id = data.get("external_id")

        if not external_id or provider == "manual":
            return

        exclude_pk = instance.pk if instance else None
        if self.repository.has_duplicate_external_activity(provider, external_id, exclude_pk):
            raise DomainValidationError(
                "Activity with this external ID already exists for this provider.",
                code="duplicate_external_activity",
            )


    def delete_activity(self, activity_id, user):
            """
            Business logic for deleting an activity.
            In the future, this could trigger goal re-calculations or
            notification cleanups.
            """
            activity = self.repository.get_by_id(activity_id)

            if activity is None:
                raise NotFound("Activity not found.")

            if activity.user != user:
                raise PermissionDenied("You do not have permission to delete this activity.")

            self.repository.delete(activity)  

    def test_delete_nonexistent_activity_returns_404(self, authenticated_client):
        response = authenticated_client.delete('/api/v1/activities/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

