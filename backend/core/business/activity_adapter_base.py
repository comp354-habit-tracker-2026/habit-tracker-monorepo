from .interfaces import IActivityAdapter
from .models import ActivitySource

class ActivityAdapter(IActivityAdapter):

    def __init__(self, provider_name: ActivitySource):
        super().__init__()
        self._provider_name = provider_name
        self._parse_start_hooks = []
        self._parse_success_hooks = []
        self._parse_failure_hooks = []

    #get_provider_name() -> str
    #Return the provider name or ID.
    def get_provider_name(self):
        """Return name of provider"""
        return self._provider_name.value # This should probably just return the enum, but we defined the method to return a str
    
    #Register callback functions for monitoring parse events (start, success, failure).
    def register_hooks(self, hooks: tuple[list[function], list[function], list[function]]):
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

    def __run_hooks(self, hooks: list[function]):
        for hook in hooks:
            hook()