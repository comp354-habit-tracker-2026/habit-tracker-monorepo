from .activity_adapter_base import ActivityAdapter
from .models import ActivitySource, MapMyRunActivity
from .config.config import AdapterConfig

class MapMyRunActivityAdapter(ActivityAdapter):

    def __init__(self):
        super().__init__(
            ActivitySource.MAP_MY_RUN, 
            AdapterConfig.get_activity_schema(AdapterConfig.MAP_MY_RUN_ADAPTER_SCHEMA_FILENAME), 
            MapMyRunActivity
            )