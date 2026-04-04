from .interfaces import IActivityAdapter

class ActivityAdapter(IActivityAdapter):

    def __init__(self, provider_name: str):
        super().__init__()
        self._provider_name = provider_name
        self._parse_start_hooks = []
        self._parse_success_hooks = []
        self._parse_failure_hooks = []

    #get_provider_name() -> str
    #Return the provider name or ID.
    def get_provider_name(self):
        """Return name of provider"""
        return self._provider_name
    
    #Register callback functions for monitoring parse events (start, success, failure).
    def register_hooks(self, hooks: tuple[list[function], list[function], list[function]]):
        """Tell the adapter what to do when parsing starts, works, or fails."""
        self._parse_start_hooks, self._parse_success_hooks, self._parse_failure_hooks = hooks
