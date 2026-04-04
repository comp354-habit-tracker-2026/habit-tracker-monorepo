"""
emit_event.py  –  Group 10 / UC-G10-97
Author: Eryk Szczyglewski (Polak777)
Issue: https://github.com/comp354-habit-tracker-2026/habit-tracker-monorepo/issues/97

Called by the Activity Service (Group 8) after saving an activity.
Uses Django's transaction.on_commit so the OutboxEvent row is only
written after the DB transaction commits – never on rollback.
"""

from __future__ import annotations

import logging
from typing import Any

from django.db import IntegrityError, transaction

from core.models import OutboxEvent

logger = logging.getLogger(__name__)

REQUIRED_PAYLOAD_FIELDS: frozenset[str] = frozenset(
    {"activity_id", "user_id", "provider", "timestamp"}
)


def _validate_payload(payload: dict[str, Any], required: frozenset[str]) -> None:
    if not isinstance(payload, dict):
        raise ValueError(f"payload must be a dict, got {type(payload).__name__!r}.")
    missing = required - payload.keys()
    if missing:
        raise ValueError(
            f"payload is missing required fields: {sorted(missing)}. "
            f"Expected at minimum: {sorted(required)}."
        )


def emit_event(
    event_type: str,
    payload: dict[str, Any],
    idempotency_key: str,
) -> None:
    """
    Schedule creation of an OutboxEvent after the current transaction commits.

    Parameters
    ----------
    event_type:
        e.g. "activity.imported" or "activity.updated"
    payload:
        Must contain: activity_id, user_id, provider, timestamp
    idempotency_key:
        Unique string to prevent duplicate rows.
        Recommended format: "<event_type>:<activity_id>"

    Raises
    ------
    ValueError  – raised immediately (before on_commit) for bad arguments.
    """
    if not event_type or not isinstance(event_type, str):
        raise ValueError("event_type must be a non-empty string.")
    if not idempotency_key or not isinstance(idempotency_key, str):
        raise ValueError("idempotency_key must be a non-empty string.")
    _validate_payload(payload, REQUIRED_PAYLOAD_FIELDS)

    def _create_outbox_event() -> None:
        try:
            event, created = OutboxEvent.objects.get_or_create(
                idempotency_key=idempotency_key,
                defaults={
                    "event_type": event_type,
                    "payload": payload,
                    "status": OutboxEvent.Status.PENDING,
                },
            )
            if created:
                logger.info(
                    "OutboxEvent created: id=%s event_type=%s idempotency_key=%s",
                    event.event_id, event_type, idempotency_key,
                )
            else:
                logger.warning(
                    "Duplicate emit_event ignored: idempotency_key=%s existing_id=%s",
                    idempotency_key, event.event_id,
                )
        except IntegrityError as exc:
            logger.error(
                "IntegrityError creating OutboxEvent (idempotency_key=%s): %s",
                idempotency_key, exc,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Unexpected error creating OutboxEvent (idempotency_key=%s): %s",
                idempotency_key, exc,
            )

    transaction.on_commit(_create_outbox_event)
    logger.debug(
        "emit_event scheduled: event_type=%s idempotency_key=%s",
        event_type, idempotency_key,
    )