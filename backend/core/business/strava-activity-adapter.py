from .activity_adapter_base import ActivityAdapter
from .models import ActivitySource

class StravaActivityAdapter(ActivityAdapter):

    def __init__(self):
        super().__init__(ActivitySource.STRAVA)

    def parse(self, raw_input_data):
        """Parse raw activity data into a standard Activity object."""
        raise NotImplementedError()

    #validate(raw_input_data) -> bool
    #Validate raw input data before parsing.
    def validate(self, raw_input_data):
        """Validate raw data before parsing."""
        raise NotImplementedError()

    #mapToActivity(self, raw_input_data) -> Activity object
    #Convert raw input data into a standardized Activity object.
    def mapToActivity(self, raw_input_data):
        """Convert raw input data into a standardized Activity object."""
        raise NotImplementedError()