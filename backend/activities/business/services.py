from core.business import BaseService, DomainValidationError
from activities.data import ActivityRepository


class ActivityService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or ActivityRepository()

    def get_user_queryset(self, user, params):
        if user.is_staff or user.is_superuser:
            queryset = self.repository.model.objects.all().order_by("-date", "-created_at")
        else:
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
