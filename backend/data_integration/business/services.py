from core.business import BaseService
# business/services.py



class DataIntegrationService(BaseService):
    def __init__(self, strava_fetcher=None):
        from data_integration.data.strava import StravaActivityFetcher
        self.strava_fetcher = strava_fetcher or StravaActivityFetcher()

    @staticmethod
    def is_synced(last_synced_at):
        return bool(last_synced_at)

    def get_strava_activities(self, access_token, start_date=None, end_date=None):
        return self.strava_fetcher.get_all_activities(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
        )
