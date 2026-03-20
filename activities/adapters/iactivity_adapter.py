from abc import ABC, abstractmethod
# NOTE: This interface skeleton was generated with the help of ChatGPT (OpenAI)

class IActivityAdapter(ABC):
    """
    Interface / abstract class for all fitness app adapters.

    
    - parse(raw_input_data: dict) -> Activity
        Convert raw provider data into standardized Activity.
    - get_provider_name() -> str
        Return the provider name or ID.
    - validate(raw_input_data) -> bool
        Validate raw input data before parsing.
    -mapToActivity(self, raw_input_data) -> Activity object
        Convert raw input data into a standardized Activity object.
    - Optional method for hooks:
      register_hooks(hooks: dict)
        Register callback functions for monitoring parse events (start, success, failure).
        Example hooks dictionary:
            {
                "on_start": callback_function,
                "on_success": callback_function,
                "on_failure": callback_function
            }
        
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
    def validate(self, raw_input_data):
        """Validate raw data before parsing."""
        pass

    @abstractmethod
    def mapToActivity(self, raw_input_data):
        """Convert raw input data into a standardized Activity object."""
        pass

