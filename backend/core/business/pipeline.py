""" Name: Kabeya Ngoyi
    Student ID: 27214545
    File: pipeline.py
    
    Description: 
    This file contains part of the pipeline orchestration. It
    connects the adapter, normalizer, deduplication, logging and event publisher steps
    for activity ingestion """

#from normalizer import ActivityNormalizer
from deduplication import ActivityDeduplicator
from event_publisher import EventPublisher
from hooks import LoggingHook

class ActivityPipeline:
    def __init__(self):
        #self.normalizer = ActivityNormalizer()
        self.deduplicator = ActivityDeduplicator()
        self.publisher = EventPublisher()
        self.hooks = LoggingHook()

    def process(self, adapter, raw_activity, existing_activities):
        adapted = adapter.transform(raw_activity) #transform
        #normalized = self.normalizer.normalize(adapted) #normalize

        results = self.deduplicator.process(adapted, existing_activities)

        # Logging:
        self.hooks.log_details(results['status'], results['changed_fields'], results['activity'])

        # Publishing:
        if results['status'] in ['NEW', 'UPDATE']:
            self.publisher.publish_event(results['activity'], results['status'])

        return results

