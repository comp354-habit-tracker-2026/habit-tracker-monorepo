""" Name: Kabeya Ngoyi
    Student ID: 27214545
    File: deduplication.py

    Description: 
    This file contains the activity deduplication logic. It checks
    whether an activity already exists by comparing provider and 
    external_id values. """

class ActivityDeduplicator:
    def is_duplicate(self, activity_data, existing_activities):
        for activity in existing_activities:
            if (
                activity.get("provider") == activity_data.get("provider")
                and activity.get("external_id") == activity_data.get("external_id")
            ):
                return True
        return False