from .interfaces import IActivityAdapter
from .models import ActivitySource, Activity

from typing import Callable, Optional
import json
import jsonschema

class ActivityAdapter(IActivityAdapter):

    def __init__(self, provider_name: ActivitySource, activity_schema: dict, activity_class: type = Activity):
        super().__init__()
        self._provider_name = provider_name
        self._parse_start_hooks = []
        self._parse_success_hooks = []
        self._parse_failure_hooks = []
        self.activity_schema = activity_schema

        if not issubclass(activity_class, Activity):
            raise ValueError(f"Activity class must inheret from {Activity}. Received {activity_class}")
        
        self.activity_class = activity_class

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

    def parse(self, raw_input_data):
        """Parse raw activity data into a standard Activity object."""

        try:    
            self._start_parse()

            valid_input, error = self.validate(raw_input_data)
            if not valid_input:
                raise ValueError(f"Input data was not valid. Error: {error}")
            
            activity = Activity()
            input_data_dict = self._convert_raw_input_data_to_dict(raw_input_data)

            for attribute, value in input_data_dict.items():
                setattr(activity, attribute, value)

            self._succeed_parse()
            return activity
        except BaseException as e:
            self._fail_parse()
            raise e

    #validate(raw_input_data) -> bool
    #Validate raw input data before parsing.
    def validate(self, raw_input_data: str) -> tuple[bool, Optional[Exception]]:
        """Validate raw data before parsing."""
        input_data_dict = self._convert_raw_input_data_to_dict(raw_input_data)
        try:
            jsonschema.validate(schema=self.activity_schema, instance=input_data_dict, format_checker=jsonschema.FormatChecker())
            return True, None
        except jsonschema.ValidationError as e:
            return False, e
    
    # Can be overriden by child classes if data doesn't come in as json
    def _convert_raw_input_data_to_dict(self, input_data: str) -> dict:
        return json.loads(input_data)