""" Name: Kabeya Ngoyi
    Student ID: 27214545
    File: weski_adapter.py
    
    Description: 
    This file contains the WeSki adapter. It converts raw WeSki activity
    into the unified Activity format used by the system. """

class WeSkiAdapter:
    def __init__(self):
        self.provider = "weski"

    def transform(self, raw_activity):
        """
            Conversion of raw WeSki data into Activity format
        """
        return {
            "activity_type": raw_activity.get("type", "unknown"),
            "duration": raw_activity.get("duration", 0), 
            "date": raw_activity.get("date"),
            "provider": self.provider, 
            "external_id": raw_activity.get("id"), 
            "raw_data": raw_activity, 
            "distance": raw_activity.get("distance"),
            "calories": raw_activity.get("calories"),
        }
    