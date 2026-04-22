
import logging
from .handlers import EVENT_HANDLERS

logger = logging.getLogger(__name__)


def process_outbox_event(event):
    handler = EVENT_HANDLERS.get(event.event_type)

    if not handler:
        logger.warning("No handler registered for event_type=%s", event.event_type)
        print(f"[WARNING] No handler registered for event type: {event.event_type}")
        return False

    try:
        handler(event.payload)
        logger.info("Successfully processed event_id=%s type=%s", event.id, event.event_type)
        print(f"[SUCCESS] Processed event_id={event.id} type={event.event_type}")
        return True
    except Exception as exc:
        logger.exception("Failed processing event_id=%s: %s", event.id, exc)
        print(f"[ERROR] Failed processing event_id={event.id}: {exc}")
        return False
