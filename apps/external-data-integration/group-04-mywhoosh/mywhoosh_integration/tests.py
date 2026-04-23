# ChatGPT was used to generate some of the following code.
# TO-DO: Create SessionRecord model and implement it.
from django.test import TestCase
from datetime import datetime, timezone

from mywhoosh_integration.session_persistence_service import SessionPersistenceService


class DummyMetrics:
    def __init__(self):
        self.distance_meters = 10000
        self.calories = 300
        self.average_power_watts = 150
        self.average_cadence_rpm = 80
        self.average_heart_rate = 120


class DummyDataQuality:
    def __init__(self):
        self.status = "complete"


class DummySession:
    def __init__(self, external_session_id=None, started_at=None):
        self.user_id = 1
        self.provider = "mywhoosh"
        self.external_session_id = external_session_id
        self.started_at = started_at or datetime.now(timezone.utc)
        self.duration_seconds = 1800
        self.title = "Test Ride"
        self.session_type = "cycling"
        self.metrics = DummyMetrics()
        self.data_quality = DummyDataQuality()


class SessionPersistenceTests(TestCase):

    def test_import_new_session(self):
        session = DummySession(external_session_id="abc123")

        result = SessionPersistenceService.import_sessions(1, [session])

        self.assertEqual(result["sessions_imported"], 1)
        self.assertEqual(result["duplicates_skipped"], 0)

    def test_skip_duplicate_by_external_id(self):
        session = DummySession(external_session_id="dup123")

        # first insert
        SessionPersistenceService.import_sessions(1, [session])

        # duplicate insert
        result = SessionPersistenceService.import_sessions(1, [session])

        self.assertEqual(result["sessions_imported"], 0)
        self.assertEqual(result["duplicates_skipped"], 1)

    def test_mixed_batch(self):
        s1 = DummySession(external_session_id="id1")
        s2 = DummySession(external_session_id="id2")

        # insert first session
        SessionPersistenceService.import_sessions(1, [s1])

        # run with duplicate + new
        result = SessionPersistenceService.import_sessions(1, [s1, s2])

        self.assertEqual(result["sessions_imported"], 1)
        self.assertEqual(result["duplicates_skipped"], 1)