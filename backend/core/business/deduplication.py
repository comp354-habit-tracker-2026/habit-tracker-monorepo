""" Name: Kabeya Ngoyi (27214545), Shiyuan Zhang (40228185)
    File: deduplication.py
    Issue: #13

    Description: 
    This file contains the activity deduplication logic. It checks
    whether an activity already exists by comparing provider and 
    external_id values. 
    
    If an activity has no duplicates -> NEW + normalization
    If an activity has a duplicate and and it differs from the existing one -> UPDATE + normalization
    If an activity has a duplicate and it is identical to the existing one -> SKIP
   
    Returns a decision outcome (NEW, UPDATE, SKIP) that can be used by logging & monitoring
    
    """

from normalizer import ActivityNormalizer

class ActivityDeduplicator:
    def __init__(self): 
        self.normalizer = ActivityNormalizer()       
        self.compare_fields = [
            'activity_type',
            'duration',
            'date',
            'provider',
            'external_id',
            'raw_data',
            'distance',
            'calories'
        ]

    def find_existing_activity(self, activity_data, existing_activities):
        '''
        Check if there's an existing activity
        return activity or None
        '''
        for activity in existing_activities:
            if (
                activity.get("provider") == activity_data.get("provider")
                and activity.get("external_id") == activity_data.get("external_id")
            ):
                return activity  # Find duplicated data
        return None
    
    # def is_duplicate(self, activity_data, existing_activities):
    #     existing_activity = self.find_existing_activity(activity_data, existing_activities)
    #     return existing_activity is not None
    
    def has_changes(self, activity_data, existing_activities):  # For UPDATE
        '''
        Check if there's a difference between the incoming data and the existing data (for UPDATE status)
        return True -> there's a difference, False -> no differences + changed fields
        '''
        changed_fields = []
        for field in self.compare_fields:
            if activity_data.get(field) != existing_activities.get(field):
                changed_fields.append(field)

        return len(changed_fields) > 0, changed_fields
    
    def get_status(self, activity_data, existing_activities):
        '''
        return status and changed_fields for logging purpose
        '''
        existing_activity = self.find_existing_activity(activity_data, existing_activities)
        if existing_activity is None:  # NEW case
            return 'NEW', []
        
        has_changed, changed_fields = self.has_changes(activity_data, existing_activity)

        if has_changed: # UPDATE case
            return 'UPDATE', changed_fields
        else: # SKIP case
            return 'SKIP', []
        
    def process(self, activity_data, existing_activities):
        normalized_data = self.normalizer.normalize(activity_data)
        status, changed_fields = self.get_status(normalized_data, existing_activities)
        return {
            'status': status,
            'changed_fields': changed_fields,
            'activity': normalized_data
        }

    
    

   