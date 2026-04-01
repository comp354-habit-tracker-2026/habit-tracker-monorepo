from core.business import BaseService
from data_integration.data import StravaActivityFetcher


class DataIntegrationService(BaseService):
    def __init__(self, strava_fetcher=None):
        self.strava_fetcher = strava_fetcher or StravaActivityFetcher()

    def get_user_integrations(self, user, params):
        provider = params.get("provider")
        status = params.get("status")

        integrations = [
            {
                "id": "fitbit-primary",
                "name": "Fitbit Primary",
                "provider": "fitbit",
                "external_id": f"fitbit-{user.id}",
                "status": "active",
                "metadata": {"source": "third_party_api"},
                "last_synced_at": "2026-03-23T00:00:00Z",
            },
            {
                "id": "google-fit-backup",
                "name": "Google Fit Backup",
                "provider": "google_fit",
                "external_id": f"googlefit-{user.id}",
                "status": "paused",
                "metadata": {"source": "third_party_api"},
                "last_synced_at": None,
            },
        ]

        # Derive is_synced from last_synced_at using the helper
        for integration in integrations:
            integration["is_synced"] = self.is_synced(integration["last_synced_at"])

        if provider:
            integrations = [item for item in integrations if item["provider"] == provider]
        if status:
            integrations = [item for item in integrations if item["status"] == status]

        return integrations

    @staticmethod
    def is_synced(last_synced_at):
        return bool(last_synced_at)

    def get_strava_activities(self, access_token, start_date=None, end_date=None):
        return self.strava_fetcher.get_all_activities(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
        )
