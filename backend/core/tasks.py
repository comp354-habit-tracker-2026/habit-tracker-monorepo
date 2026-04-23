"""
core/tasks.py

Outbox worker: polls outbox_events for PENDING rows, dispatches them via
process_outbox_event(), and marks each row PUBLISHED or FAILED.

Runs on a schedule via Celery Beat (configured in settings.py).
"""

import logging
from datetime import datetime, timezone

from celery import shared_task

from core.backend.core.consumer import process_outbox_event
from core.models import OutboxEvent

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


@shared_task(name="core.tasks.process_pending_outbox_events")
def process_pending_outbox_events() -> None:
    """Poll outbox_events for PENDING rows and dispatch each one."""
    pending = OutboxEvent.objects.filter(status=OutboxEvent.Status.PENDING).order_by("created_at")

    if not pending.exists():
        logger.debug("No PENDING outbox events found.")
        return

    for event in pending:
        _dispatch_event(event)


def _dispatch_event(event: OutboxEvent) -> None:
    event.attempts += 1
    try:
        success = process_outbox_event(event)
        if not success:
            raise RuntimeError(f"process_outbox_event returned False for event_type={event.event_type}")
        event.status = OutboxEvent.Status.PUBLISHED
        event.published_at = datetime.now(tz=timezone.utc)
        event.last_error = None
        logger.info(
            "OutboxEvent published: id=%s event_type=%s attempts=%s",
            event.event_id, event.event_type, event.attempts,
        )
    except Exception as exc:  # noqa: BLE001
        event.last_error = str(exc)
        if event.attempts >= MAX_RETRIES:
            event.status = OutboxEvent.Status.FAILED
            logger.error(
                "OutboxEvent FAILED after %s attempts: id=%s event_type=%s error=%s",
                event.attempts, event.event_id, event.event_type, exc,
            )
        else:
            logger.warning(
                "OutboxEvent dispatch error (attempt %s/%s): id=%s event_type=%s error=%s",
                event.attempts, MAX_RETRIES, event.event_id, event.event_type, exc,
            )
    finally:
        event.save(update_fields=["status", "attempts", "last_error", "published_at"])
