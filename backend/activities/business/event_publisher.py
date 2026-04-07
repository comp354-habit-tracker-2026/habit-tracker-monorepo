'''
Name: Shiyuan Zhang (40228185)
File: event_publisher.py
Issue: #149

Goal: 
Publish an event to the Eventhub when Activity data is preprocessed and ready for downstream tasks
Log success/failure

adapter -> normalizer -> deduplication -> create event message -> publish

'''
class EventPublisher:
    # Builds msg
    def publish_event(self, activity, status):
        event = {
            'event_type': 'ActivityCreatedEvent',
            'status': status,
            'provider': activity.get('provider'),
            'external_id': activity.get('external_id'),
            'payload': activity
        }
        print('Publishing event:', event) # Temporary prints out results, need to be replaced with the connection of the EventHub