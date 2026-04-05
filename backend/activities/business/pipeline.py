""" Name: Kabeya Ngoyi
    Student ID: 27214545
    File: pipeline.py
    
    Description: 
    This file contains part of the pipeline orchestration. It
    connects the adapter, normalizer, and deduplication steps
    for activity ingestion """

from normalizer import ActivityNormalizer
from deduplication import ActivityDeduplicator

class ActivityPipeline:
    def __init__(self):
        self.normalizer = ActivityNormalizer()
        self.deduplicator = ActivityDeduplicator()

    def process(self, adapter, raw_activity, existing_activities):
        adapted = adapter.transform(raw_activity) #transform
        normalized = self.normalizer.normalize(adapted) #normalize
        is_duplicate = self.deduplicator.is_duplicate(normalized, existing_activities)
        if is_duplicate:
            print("Duplicate activity found. Skipping.")
            return None
        
        print("New activity processed.")
        return normalized

