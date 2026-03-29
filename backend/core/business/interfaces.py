from abc import ABC, abstractmethod
from .models import Activity
# NOTE: This interface skeleton was generated with the help of ChatGPT (OpenAI)

class IActivityIngestor(ABC):
    @abstractmethod
    def ingest_activity(self, activity: Activity):
        """Ingest a single normalized Activity into the pipeline."""
        pass

    @abstractmethod
    def is_duplicate(self, activity: Activity) -> bool:
        """Check if the Activity is a duplicate."""
        pass

    @abstractmethod
    def publish_event(self, activity: Activity):
        """Publish an event for the Activity to EventHub or similar."""
        pass

    @abstractmethod
    def register_hooks(self, hooks):
        """Register logging and monitoring hooks for ingestion events."""
        pass

from abc import ABC, abstractmethod
from .models import Activity
# NOTE: This interface skeleton was generated with the help of ChatGPT (OpenAI)

#Interface for all fitness app adapters
class IActivityAdapter(ABC):

    #parse(raw_input_data: dict) -> Activity
    #Convert raw provider data into standardized Activity
    @abstractmethod
    def parse(self, raw_input_data):
        """Parse raw activity data into a standard Activity object."""
        pass

    #get_provider_name() -> str
    #Return the provider name or ID.
    @abstractmethod
    def get_provider_name(self):
        """Return name of provider"""
        pass
    
    #Register callback functions for monitoring parse events (start, success, failure).
    @abstractmethod
    def register_hooks(self, hooks):
        """Tell the adapter what to do when parsing starts, works, or fails."""
        pass

    #validate(raw_input_data) -> bool
    #Validate raw input data before parsing.
    @abstractmethod
    def validate(self, raw_input_data):
        """Validate raw data before parsing."""
        pass

    #mapToActivity(self, raw_input_data) -> Activity object
    #Convert raw input data into a standardized Activity object.
    @abstractmethod
    def mapToActivity(self, raw_input_data):
        """Convert raw input data into a standardized Activity object."""
        pass


