from pathlib import Path
from os.path import join

_STRAVA_FILENAME = "strava_activity_schema.json"

class AdapterConfig:
    STRAVA_ADAPTER_SCHEMA_FILENAME = join(Path(__file__).parent.resolve(), 
                                  _STRAVA_FILENAME)