# ============================================================
# G13 - MMingQwQ - Unit Tests for Health Indicators API Router
# ============================================================
import unittest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from fastapi import HTTPException

from analytics.business.api_router import (
    HealthIndicatorsRequest,
    health_indicators_endpoint,
    fetch_activity_data,
    compute_inactivity,
    build_score_input,
    _check_pending_outbox,
)
from analytics.business.indicators import WorkoutSession, WorkoutType


class DummyVolumeResult:
    total_volume = 250.0


class DummyConsistencyResult:
    consistency_score = 75.0


class TestHealthIndicatorsAPIRouter(unittest.TestCase):
    @patch("analytics.business.api_router._check_pending_outbox", return_value=False)
    @patch("analytics.business.api_router.fetch_activity_data")
    def test_tc1_normal_request_success(self, mock_fetch_activity_data, _mock_outbox):
        mock_fetch_activity_data.return_value = [
            {
                "date": "2026-04-01T10:00:00",
                "duration_minutes": 45,
                "intensity": 1.2,
                "workout_type": "cardio",
                "user_id": "user123",
            },
            {
                "date": "2026-04-03T10:00:00",
                "duration_minutes": 60,
                "intensity": 1.5,
                "workout_type": "strength",
                "user_id": "user123",
            },
        ]

        request = HealthIndicatorsRequest(
            user_id="user123",
            from_date="2026-04-01T00:00:00",
            to_date="2026-04-07T23:59:59",
            window="weekly",
            target_workouts=3,
            alerts=[],
        )

        result = asyncio.run(health_indicators_endpoint(request))

        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        self.assertIn("indicators", result["data"])
        self.assertIn("health_score", result["data"])
        self.assertIn("inactivity", result["data"])
        self.assertFalse(result["data"]["inactivity"]["inactive"])
        self.assertTrue(len(result["data"]["messages"]) > 0)

    @patch("analytics.business.api_router.fetch_activity_data")
    def test_tc2_missing_user_id(self, mock_fetch_activity_data):
        with self.assertRaises(Exception):
            HealthIndicatorsRequest(
                from_date="2026-04-01T00:00:00",
                to_date="2026-04-07T23:59:59",
                window="weekly",
                target_workouts=3,
                alerts=[],
            )
        mock_fetch_activity_data.assert_not_called()

    @patch("analytics.business.api_router.fetch_activity_data")
    def test_tc3_invalid_date_range(self, mock_fetch_activity_data):
        request = HealthIndicatorsRequest(
            user_id="user123",
            from_date="2026-04-10T00:00:00",
            to_date="2026-04-07T23:59:59",
            window="weekly",
            target_workouts=3,
            alerts=[],
        )

        with self.assertRaises(HTTPException) as context:
            asyncio.run(health_indicators_endpoint(request))

        self.assertEqual(context.exception.status_code, 400)
        mock_fetch_activity_data.assert_not_called()

    @patch("analytics.business.api_router._check_pending_outbox", return_value=False)
    @patch("analytics.business.api_router.fetch_activity_data")
    def test_tc4_no_activity_data(self, mock_fetch_activity_data, _mock_outbox):
        mock_fetch_activity_data.return_value = []

        request = HealthIndicatorsRequest(
            user_id="user123",
            from_date="2026-04-01T00:00:00",
            to_date="2026-04-07T23:59:59",
            window="weekly",
            target_workouts=3,
            alerts=[],
        )

        result = asyncio.run(health_indicators_endpoint(request))

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["data"]["inactivity"]["inactive"])

        score = result["data"]["health_score"]["score"]
        self.assertTrue(score is None or score <= 40)

    @patch("analytics.business.api_router.fetch_activity_data")
    def test_tc5_data_storage_unavailable(self, mock_fetch_activity_data):
        mock_fetch_activity_data.side_effect = Exception("Activity data service unavailable")

        request = HealthIndicatorsRequest(
            user_id="user123",
            from_date="2026-04-01T00:00:00",
            to_date="2026-04-07T23:59:59",
            window="weekly",
            target_workouts=3,
            alerts=[],
        )

        with self.assertRaises(HTTPException) as context:
            asyncio.run(health_indicators_endpoint(request))

        self.assertEqual(context.exception.status_code, 503)

    @patch("activities.models.Activity.objects")
    def test_fetch_activity_data_returns_empty_when_no_results(self, mock_objects):
        mock_objects.filter.return_value.select_related.return_value = []
        result = fetch_activity_data(
            user_id="u1",
            from_date=datetime(2026, 4, 1),
            to_date=datetime(2026, 4, 7),
        )
        self.assertEqual(result, [])

    @patch("activities.models.Activity.objects")
    def test_fetch_activity_data_maps_activity_fields(self, mock_objects):
        mock_activity = MagicMock()
        mock_activity.date = datetime(2026, 4, 3).date()
        mock_activity.duration = 45
        mock_activity.activity_type = "cardio"
        mock_objects.filter.return_value.select_related.return_value = [mock_activity]
        result = fetch_activity_data(
            user_id="u1",
            from_date=datetime(2026, 4, 1),
            to_date=datetime(2026, 4, 7),
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["duration_minutes"], 45)
        self.assertEqual(result[0]["workout_type"], "cardio")
        self.assertEqual(result[0]["intensity"], 1.0)

    def test_compute_inactivity_no_workouts(self):
        result = compute_inactivity([], to_date=datetime(2026, 4, 7))
        self.assertTrue(result["inactive"])
        self.assertEqual(result["severity"], "severe")
        self.assertIsNone(result["days_since_last_activity"])

    def test_compute_inactivity_severe(self):
        workouts = [
            WorkoutSession(
                date=datetime(2026, 4, 1),
                duration_minutes=30,
                intensity=1.0,
                workout_type=WorkoutType.CARDIO,
                user_id="u1",
            )
        ]
        result = compute_inactivity(workouts, to_date=datetime(2026, 4, 10))
        self.assertTrue(result["inactive"])
        self.assertEqual(result["severity"], "severe")

    def test_compute_inactivity_mild(self):
        workouts = [
            WorkoutSession(
                date=datetime(2026, 4, 5),
                duration_minutes=30,
                intensity=1.0,
                workout_type=WorkoutType.CARDIO,
                user_id="u1",
            )
        ]
        result = compute_inactivity(workouts, to_date=datetime(2026, 4, 8))
        self.assertFalse(result["inactive"])
        self.assertEqual(result["severity"], "mild")

    def test_compute_inactivity_none(self):
        workouts = [
            WorkoutSession(
                date=datetime(2026, 4, 6),
                duration_minutes=30,
                intensity=1.0,
                workout_type=WorkoutType.CARDIO,
                user_id="u1",
            )
        ]
        result = compute_inactivity(workouts, to_date=datetime(2026, 4, 7))
        self.assertFalse(result["inactive"])
        self.assertEqual(result["severity"], "none")

    def test_build_score_input(self):
        inactivity_result = {"inactive": True}
        result = build_score_input(
            DummyVolumeResult(),
            DummyConsistencyResult(),
            inactivity_result,
        )
        self.assertEqual(result["volume"], 250.0)
        self.assertEqual(result["consistency"], 75.0)
        self.assertEqual(result["inactive"], 1)

    @patch("analytics.business.api_router.fetch_activity_data")
    def test_value_error_branch_returns_400(self, mock_fetch_activity_data):
        mock_fetch_activity_data.return_value = [
            {
                "date": "2026-04-01T10:00:00",
                "duration_minutes": 45,
                "intensity": 1.2,
                "workout_type": "bad_type",
                "user_id": "user123",
            }
        ]

        request = HealthIndicatorsRequest(
            user_id="user123",
            from_date="2026-04-01T00:00:00",
            to_date="2026-04-07T23:59:59",
            target_workouts=3,
        )

        with self.assertRaises(HTTPException) as context:
            asyncio.run(health_indicators_endpoint(request))

        self.assertEqual(context.exception.status_code, 400)

    @patch("analytics.business.api_router.ExplainabilityBuilder")
    @patch("analytics.business.api_router.fetch_activity_data")
    def test_generic_exception_branch_returns_500(self, mock_fetch_activity_data, mock_builder):
        mock_fetch_activity_data.return_value = [
            {
                "date": "2026-04-01T10:00:00",
                "duration_minutes": 45,
                "intensity": 1.2,
                "workout_type": "cardio",
                "user_id": "user123",
            }
        ]

        mock_builder.return_value.build_explanation.side_effect = Exception("boom")

        request = HealthIndicatorsRequest(
            user_id="user123",
            from_date="2026-04-01T00:00:00",
            to_date="2026-04-07T23:59:59",
            target_workouts=3,
        )

        with self.assertRaises(HTTPException) as context:
            asyncio.run(health_indicators_endpoint(request))

        self.assertEqual(context.exception.status_code, 500)

    # ============================================================
    # G15 - Ominous Observer Tests
    # ============================================================

    @patch("analytics.business.api_router._check_pending_outbox", return_value=True)
    @patch("analytics.business.api_router.fetch_activity_data")
    def test_ominous_message_injected_when_pending_outbox(self, mock_fetch, _mock_outbox):
        mock_fetch.return_value = [
            {
                "date": "2026-04-06T10:00:00",
                "duration_minutes": 30,
                "intensity": 1.0,
                "workout_type": "cardio",
                "user_id": "user123",
            }
        ]
        request = HealthIndicatorsRequest(
            user_id="user123",
            from_date="2026-04-01T00:00:00",
            to_date="2026-04-07T23:59:59",
            target_workouts=3,
        )
        result = asyncio.run(health_indicators_endpoint(request))
        self.assertEqual(result["status"], "success")
        self.assertIn(
            "I see your new movements in the shadows... Refresh.",
            result["data"]["messages"],
        )

    @patch("analytics.business.api_router._check_pending_outbox", return_value=False)
    @patch("analytics.business.api_router.fetch_activity_data")
    def test_no_ominous_message_when_no_pending_outbox(self, mock_fetch, _mock_outbox):
        mock_fetch.return_value = [
            {
                "date": "2026-04-06T10:00:00",
                "duration_minutes": 30,
                "intensity": 1.0,
                "workout_type": "cardio",
                "user_id": "user123",
            }
        ]
        request = HealthIndicatorsRequest(
            user_id="user123",
            from_date="2026-04-01T00:00:00",
            to_date="2026-04-07T23:59:59",
            target_workouts=3,
        )
        result = asyncio.run(health_indicators_endpoint(request))
        self.assertEqual(result["status"], "success")
        self.assertNotIn(
            "I see your new movements in the shadows... Refresh.",
            result["data"]["messages"],
        )

    @patch("core.models.OutboxEvent.objects")
    def test_check_pending_outbox_returns_true_when_pending(self, mock_objects):
        mock_objects.filter.return_value.exists.return_value = True
        result = _check_pending_outbox("user123")
        self.assertTrue(result)
        mock_objects.filter.assert_called_once_with(
            status="PENDING",
            payload__user_id="user123",
        )

    @patch("core.models.OutboxEvent.objects")
    def test_check_pending_outbox_returns_false_when_none(self, mock_objects):
        mock_objects.filter.return_value.exists.return_value = False
        result = _check_pending_outbox("user123")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()