from .activity_adapter_base import ActivityAdapter

class StravaActivityAdapter(ActivityAdapter):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def parse(self, raw_input_data):
        """Parse raw activity data into a standard Activity object."""
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