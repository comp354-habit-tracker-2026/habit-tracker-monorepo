from abc import ABC, abstractmethod
# NOTE: This interface skeleton was generated with the help of ChatGPT (OpenAI)

class IActivityAdapter(ABC):
    """
    Interface / abstract class for all fitness app adapters.

    Required methods:
    - parse(raw_input_data: dict) -> Activity
        Convert raw provider data into standardized Activity.
    - get_provider_name() -> str
        Return the provider name or ID.

    Optional methods:
    - Optional method for hooks:
      register_hooks(hooks: dict)
        Register callback functions for monitoring parse events (start, success, failure).
        Example hooks dictionary:
            {
                "on_start": callback_function,
                "on_success": callback_function,
                "on_failure": callback_function
            }
        - validate_raw_data(raw_input_data) -> bool
        Validate raw input data before parsing.
    """

    @abstractmethod
    def parse(self, raw_input_data):
        """Parse raw activity data into a standard Activity object."""
        pass
    
    @abstractmethod
    def get_provider_name(self):
        """Return name of provider"""
        pass

    @abstractmethod
    def register_hooks(self, hooks):
        """Tell the adapter what to do when parsing starts, works, or fails."""
        pass

    @abstractmethod
    def validate_raw_data(self, raw_input_data):
        """Validate raw data before parsing."""
        pass

