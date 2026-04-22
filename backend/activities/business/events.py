from .hooks import LoggingHook

class Subscriber():
    def __init__(self):
        self.logging_hook = LoggingHook()

    def notify(self, event_type: str, message: object):
        print(f"Subscriber received event: {event_type}, message: {message}")

class EventHub:

    def __init__(self):
        self.subscribers: dict[str, list[Subscriber]] = {}
        self.logging_hook = LoggingHook()

    def subscribe(self, event_type: str, subscriber: Subscriber) -> None:
        event_subscribers = self.subscribers.get(event_type, [])
        if subscriber not in event_subscribers:
            event_subscribers.append(subscriber)
        self.subscribers[event_type] = event_subscribers

    def publish(self, event_type: str, message: object) -> tuple[bool, Exception]:
        try:
            for subscriber in self.subscribers.get(event_type, []):
                subscriber.notify(event_type, message)
        except BaseException as e:
            return False, e
        
        return True, None

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

    def __init__(self, event_hub: EventHub):
        self.event_hub = event_hub
        self.logging_hook = LoggingHook()

    # Builds msg
    def publish_event(self, activity, status):
        event = {
            'event_type': 'ActivityCreatedEvent',
            'status': status,
            'provider': activity.get('provider'),
            'external_id': activity.get('external_id'),
            'payload': activity
        }
        self.event_hub.publish('ActivityCreatedEvent', event)