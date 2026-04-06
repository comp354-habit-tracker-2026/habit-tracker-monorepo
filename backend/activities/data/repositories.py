from activities.models import Activity
from core.data import BaseRepository


class ActivityRepository(BaseRepository):
    def __init__(self):
        super().__init__(Activity)

    def for_user(self, user):
        return self.model.objects.filter(user=user).order_by("-date", "-created_at")

    def apply_filters(self, queryset, params):
        provider = params.get("provider")
        date_from = params.get("date_from")
        date_to = params.get("date_to")

        if provider:
            queryset = queryset.filter(provider=provider)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset

    def has_duplicate_external_activity(self, provider, external_id, exclude_pk=None):
        queryset = self.model.objects.filter(provider=provider, external_id=external_id)
        if exclude_pk is not None:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset.exists()
