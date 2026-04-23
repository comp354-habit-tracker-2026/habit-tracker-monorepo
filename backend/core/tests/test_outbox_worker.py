from unittest.mock import patch

import pytest

from core.models import OutboxEvent
from core.tasks import MAX_RETRIES, process_pending_outbox_events

DUMMY_PAYLOAD = {
    "activity_id": 1,
    "user_id": 1,
    "provider": "strava",
    "timestamp": "2026-04-20T00:00:00Z",
}


def make_event(**kwargs):
    defaults = dict(
        event_type="activity.imported",
        payload=DUMMY_PAYLOAD,
        status=OutboxEvent.Status.PENDING,
    )
    defaults.update(kwargs)
    return OutboxEvent.objects.create(**defaults)


@pytest.mark.django_db
class TestProcessPendingOutboxEvents:

    def test_no_pending_events_does_nothing(self):
        """Task runs without error when there are no PENDING rows."""
        with patch("core.tasks.process_outbox_event") as mock_process:
            process_pending_outbox_events()
            mock_process.assert_not_called()

    def test_published_and_failed_events_are_skipped(self):
        """Only PENDING rows are picked up; other statuses are ignored."""
        make_event(status=OutboxEvent.Status.PUBLISHED)
        make_event(status=OutboxEvent.Status.FAILED)

        with patch("core.tasks.process_outbox_event") as mock_process:
            process_pending_outbox_events()
            mock_process.assert_not_called()

    def test_successful_event_marked_published(self):
        """A PENDING event that dispatches successfully is marked PUBLISHED."""
        event = make_event()

        with patch("core.tasks.process_outbox_event", return_value=True):
            process_pending_outbox_events()

        event.refresh_from_db()
        assert event.status == OutboxEvent.Status.PUBLISHED
        assert event.attempts == 1
        assert event.published_at is not None
        assert event.last_error is None

    def test_failed_event_below_max_retries_stays_pending(self):
        """A dispatch failure below MAX_RETRIES leaves the event PENDING for retry."""
        event = make_event()

        with patch("core.tasks.process_outbox_event", return_value=False):
            process_pending_outbox_events()

        event.refresh_from_db()
        assert event.status == OutboxEvent.Status.PENDING
        assert event.attempts == 1
        assert event.last_error is not None

    def test_event_marked_failed_after_max_retries(self):
        """An event that has already failed MAX_RETRIES-1 times is marked FAILED on next failure."""
        event = make_event(attempts=MAX_RETRIES - 1)

        with patch("core.tasks.process_outbox_event", return_value=False):
            process_pending_outbox_events()

        event.refresh_from_db()
        assert event.status == OutboxEvent.Status.FAILED
        assert event.attempts == MAX_RETRIES

    def test_exception_from_handler_treated_as_failure(self):
        """An exception raised inside process_outbox_event is caught and counted as a failure."""
        event = make_event()

        with patch("core.tasks.process_outbox_event", side_effect=RuntimeError("boom")):
            process_pending_outbox_events()

        event.refresh_from_db()
        assert event.status == OutboxEvent.Status.PENDING
        assert event.attempts == 1
        assert "boom" in event.last_error

    def test_multiple_pending_events_all_processed(self):
        """All PENDING rows are dispatched in a single task run."""
        events = [make_event() for _ in range(3)]

        with patch("core.tasks.process_outbox_event", return_value=True):
            process_pending_outbox_events()

        for event in events:
            event.refresh_from_db()
            assert event.status == OutboxEvent.Status.PUBLISHED

    def test_one_failure_does_not_block_others(self):
        """A failure on one event does not prevent subsequent events from being processed."""
        failing = make_event(event_type="activity.imported")
        succeeding = make_event(event_type="activity.updated")

        def side_effect(event):
            if event.pk == failing.pk:
                return False
            return True

        with patch("core.tasks.process_outbox_event", side_effect=side_effect):
            process_pending_outbox_events()

        failing.refresh_from_db()
        succeeding.refresh_from_db()
        assert failing.status == OutboxEvent.Status.PENDING
        assert succeeding.status == OutboxEvent.Status.PUBLISHED
