from rest_framework import serializers

from activities.business import ActivityService
from activities.models import Activity, ConnectedAccount
from core.business import DomainValidationError


class ActivitySerializer(serializers.ModelSerializer):
    # Links the activity to one of the user's connected accounts (e.g. their Strava).
    # The list of valid accounts is filtered in __init__ so a user can only
    # assign activities to their own accounts, not someone else's.
    account = serializers.PrimaryKeyRelatedField(
        queryset=ConnectedAccount.objects.all()
    )
    raw_data = serializers.JSONField(required=False)

    class Meta:
        model = Activity
        fields = [
            "id",
            "account",
            "activity_type",
            "duration",
            "date",
            "external_id",
            "distance",
            "calories",
            "raw_data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["account"].queryset = ConnectedAccount.objects.filter(
                user=request.user
            )

    def validate(self, data):
        service = ActivityService()
        account = data.get("account")
        external_id = data.get("external_id")

        if self.instance is not None:
            account = account if account is not None else self.instance.account
            external_id = external_id if external_id is not None else self.instance.external_id

        try:
            service.validate_external_activity_uniqueness(
                {"account": account, "external_id": external_id},
                instance=self.instance,
            )
        except DomainValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return data


class ConnectedAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for ConnectedAccount model.
    
    Displays provider info and linked account details.
    Sensitive tokens are never exposed in responses.
    """
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = ConnectedAccount
        fields = [
            "id",
            "provider",
            "provider_display",
            "external_user_id",
            "connected_at",
        ]
        read_only_fields = [
            "id",
            "provider",
            "provider_display",
            "external_user_id",
            "connected_at",
        ]


# Backwards-compatible naming alias.
ActivitySerialiser = ActivitySerializer
