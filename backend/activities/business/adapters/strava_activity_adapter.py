from .activity_adapter_base import ActivityAdapter
from .models import ActivitySource
from .config.config import AdapterConfig

class StravaActivityAdapter(ActivityAdapter):

    def __init__(self):
        super().__init__(ActivitySource.STRAVA, AdapterConfig.STRAVA_ADAPTER_SCHEMA_FILENAME)