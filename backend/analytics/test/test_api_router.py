# ============================================================
# G13 - MMingQwQ - Unit Tests for Health Indicators API Router
# ============================================================

import unittest
import asyncio
from unittest.mock import patch
from fastapi import HTTPException
from analytics.business.api_router import (
    HealthIndicatorsRequest,
    health_indicators_endpoint,
)


class TestHealthIndicatorsAPIRouter(unittest.TestCase):
    """Unit tests for health_indicators_endpoint."""

    # ------------------------------------------------------------
    # TC1 Normal request (success)
    # ------------------------------------------------------------
    @patch("analytics.business.api_router.fetch_activity_data")
    def test_tc1_normal_request_success(self, mock_fetch_activity_data):
        """Returns success response with indicators, score, inactivity false, and explanations."""
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
        self.assertIn("volume", result["data"]["indicators"])
        self.assertIn("consistency", result["data"]["indicators"])
        self.assertIn("health_score", result["data"])
        self.assertIn("inactivity", result["data"])
        self.assertFalse(result["data"]["inactivity"]["inactive"])
        self.assertTrue(len(result["data"]["messages"]) > 0)

        mock_fetch_activity_data.assert_called_once()

    # ------------------------------------------------------------
    # TC2 Invalid parameters (missing userId)
    # ------------------------------------------------------------
    @patch("analytics.business.api_router.fetch_activity_data")
    def test_tc2_missing_user_id(self, mock_fetch_activity_data):
        """Request creation should fail if user_id is missing."""
        with self.assertRaises(Exception):
            HealthIndicatorsRequest(
                from_date="2026-04-01T00:00:00",
                to_date="2026-04-07T23:59:59",
                window="weekly",
                target_workouts=3,
                alerts=[],
            )

        mock_fetch_activity_data.assert_not_called()

    # ------------------------------------------------------------
    # TC3 Invalid parameters (date range invalid)
    # ------------------------------------------------------------
    @patch("analytics.business.api_router.fetch_activity_data")
    def test_tc3_invalid_date_range(self, mock_fetch_activity_data):
        """Returns HTTP 400 when from_date is later than to_date."""
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

    # ------------------------------------------------------------
    # TC4 No activity data in range
    # ------------------------------------------------------------
    @patch("analytics.business.api_router.fetch_activity_data")
    def test_tc4_no_activity_data(self, mock_fetch_activity_data):
        """Returns success with default indicators and inactivity true."""
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

        joined_messages = " ".join(result["data"]["messages"]).lower()
        self.assertTrue("no activity" in joined_messages or "missing data" in joined_messages)

        mock_fetch_activity_data.assert_called_once()

    # ------------------------------------------------------------
    # TC5 Data storage unavailable
    # ------------------------------------------------------------
    @patch("analytics.business.api_router.fetch_activity_data")
    def test_tc5_data_storage_unavailable(self, mock_fetch_activity_data):
        """Returns HTTP 503 when activity data service fails."""
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
        mock_fetch_activity_data.assert_called_once()


if __name__ == "__main__":
    unittest.main()
