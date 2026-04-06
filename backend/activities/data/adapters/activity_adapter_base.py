from .interfaces import IActivityAdapter
from .models import ActivitySource

from typing import Callable
import json
import jsonschema

class ActivityAdapter(IActivityAdapter):

    def __init__(self, provider_name: ActivitySource, activity_schema_filename: str):
        super().__init__()
        self._provider_name = provider_name
        self._parse_start_hooks = []
        self._parse_success_hooks = []
        self._parse_failure_hooks = []
        self.activity_schema = self._load_activity_schema(activity_schema_filename)

    #get_provider_name() -> str
    #Return the provider name or ID.
    def get_provider_name(self):
        """Return name of provider"""
        return self._provider_name.value # This should probably just return the enum, but we defined the method to return a str
    
    #Register callback functions for monitoring parse events (start, success, failure).
    def register_hooks(self, hooks: tuple[list[Callable], list[Callable], list[Callable]]):
        """Tell the adapter what to do when parsing starts, works, or fails."""
        START_INDEX, SUCCESS_INDEX, FAILURE_INDEX = 0, 1, 2
        self._parse_start_hooks.extend(hooks[START_INDEX])
        self._parse_success_hooks.extend(hooks[SUCCESS_INDEX])
        self._parse_failure_hooks.extend(hooks[FAILURE_INDEX])

    def _start_parse(self):
        self.__run_hooks(self._parse_start_hooks)

    def _fail_parse(self):
        self.__run_hooks(self._parse_failure_hooks)

    def _succeed_parse(self):
        self.__run_hooks(self._parse_success_hooks)

    def __run_hooks(self, hooks: list[Callable]):
        for hook in hooks:
            hook()

    @staticmethod
    def _load_activity_schema(filename: str) -> dict[str, type]:
        # TODO: Add proper error handling
        with open(filename, 'r') as file:
            return json.load(file)

    def parse(self, raw_input_data):
        """Parse raw activity data into a standard Activity object."""
        raise NotImplementedError()

    #validate(raw_input_data) -> bool
    #Validate raw input data before parsing.
    def validate(self, raw_input_data: str) -> bool:
        """Validate raw data before parsing."""
        input_data_dict = self._convert_raw_input_data_to_dict(raw_input_data)
        try:
            jsonschema.validate(instance=input_data_dict, schema=self.activity_schema)
            return True
        except jsonschema.ValidationError:
            return False
                
    #mapToActivity(self, raw_input_data) -> Activity object
    #Convert raw input data into a standardized Activity object.
    def mapToActivity(self, raw_input_data):
        """Convert raw input data into a standardized Activity object."""
        raise NotImplementedError()
    
    # Can be overriden by child classes if data doesn't come in as json
    def _convert_raw_input_data_to_dict(self, input_data: str) -> dict:
        return json.loads(input_data)