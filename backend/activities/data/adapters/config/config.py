from pathlib import Path
from os.path import join
import json

_STRAVA_FILENAME = "strava_activity_schema.json"
_MY_WHOOSH_FILENAME = "my_whoosh_activity_schema.json"
_WE_SKI_FILENAME = "we_ski_activity_schema.json"
_MAP_MY_RUN_FILENAME = "my_run_activity_schema.json"

class AdapterConfig:
    STRAVA_ADAPTER_SCHEMA_FILENAME = join(Path(__file__).parent.resolve(), 
                                  _STRAVA_FILENAME)
    MY_WHOOSH_ADAPTER_SCHEMA_FILENAME = join(Path(__file__).parent.resolve(), 
                                  _MY_WHOOSH_FILENAME)
    WE_SKI_ADAPTER_SCHEMA_FILENAME = join(Path(__file__).parent.resolve(), 
                                  _WE_SKI_FILENAME)
    MAP_MY_RUN_ADAPTER_SCHEMA_FILENAME = join(Path(__file__).parent.resolve(), 
                                  _MAP_MY_RUN_FILENAME)
    
    @staticmethod
    def get_activity_schema(schema_filename) -> dict:
        try:
            with open(schema_filename, "r") as file:
                schema_data = file.read()
        except BaseException as e:
            raise IOError(f"Could not read file {schema_filename}. Error: {e}")

        # Just let this error bubble up if the schema data is not valid json
        return json.loads(schema_data)
