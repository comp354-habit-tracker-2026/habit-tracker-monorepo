"""Name: Kabeya Ngoyi
    Student ID: 27214545
    File: mywhoosh_adapter.py
    
    Description: 
    This file contains the MyWhoosh adapter. It converts raw MyWhoosh
    activity into the unified Activity format used by the system."""

class MyWhooshAdapter:
    def __init__(self):
        self.provider = "mywhoosh"

    def transform(self, raw_activity):
        """
        Converting raw MyWhoosh data into Activity format
        """

        return {
            "activity_type": raw_activity.get("type", "unknwon"),
            "duration": raw_activity.get("duration", 0), 
            "date": raw_activity.get("date"), 
            "provider": self.provider, 
            "external_id": raw_activity.get("id"), 
            "raw_data": raw_activity, 
            "distance": raw_activity.get("distance"), 
            "calories": raw_activity.get("calories")
        }