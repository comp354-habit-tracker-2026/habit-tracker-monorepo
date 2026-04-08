""" Name: Kabeya Ngoyi
    Student ID: 27214545
    File: normalizer.py
    
    Description: 
    This file contains the activity normalizer. It Standardizes activity
    data by formatting fields such as activity type, duration and date 
    before further processing. """

from datetime import datetime

class ActivityNormalizer:
    def normalize(self, activity_data):
        date_str = activity_data.get("date")
        return {
            "activity_type": activity_data.get("activity_type", "").capitalize(), 
            "duration": int(activity_data.get("duration", 0)), 
            "date": datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None, 
            "provider": activity_data.get("provider"),
            "external_id": activity_data.get("external_id"),
            "raw_data": activity_data.get("raw_data"),
            "distance": activity_data.get("distance"), 
            "calories": activity_data.get("calories")
        }
    