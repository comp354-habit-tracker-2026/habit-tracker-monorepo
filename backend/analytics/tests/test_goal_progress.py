from datetime import datetime
from decimal import Decimal
import json

import pytest
from activities.models import Activity, ConnectedAccount
from django.contrib.auth import get_user_model
from goals.serializers import GoalSerializer
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from analytics.business import GoalProgressService
from goals.models import Goal
from notifications.models import Notification

User = get_user_model()

GOAL_INPUT = {
    "title": "Run 50km",
    "description": "Monthly running goal",
    "target_value": "50.00",
    "goal_type": "distance",
    "start_date": "2026-01-01",
    "end_date": "2026-01-31",
}

MANUAL_ACTIVITY_INPUT = {
    "activity_type": "Running",
    "duration": 45,
    "date": "2026-01-15",
    "distance": "7.5",
    "calories": 450,
}

EXTERNAL_ACTIVITY_INPUT = {
    "activity_type": "Cycling",
    "duration": 60,
    "date": "2026-01-15",
    "provider": "strava",
    "external_id": "strava_12345",
    "distance": "25.0",
    "raw_data": {"original": "strava data"},
}


def _dt(year, month, day):
    return timezone.make_aware(datetime(year, month, day, 12, 0, 0))


def _auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


def _create_goal_from_payload(user, **overrides):
    serializer = GoalSerializer(data={**GOAL_INPUT, **overrides})
    assert serializer.is_valid(), serializer.errors
    return serializer.save(user=user)


def _create_activity_from_payload(user, payload, **overrides):
    data = {**payload, **overrides}
    provider = data.pop("provider", None)
    account = None
    if provider:
        account, _ = ConnectedAccount.objects.get_or_create(
            user=user,
            provider=provider,
            defaults={"external_user_id": f"test_{provider}_{user.id}"},
        )
    return Activity.objects.create(account=account, **data)


def _sync_goal_distance(goal, *activities):
    # Goal progress still reads Goal.current_value directly in this milestone.
    goal.current_value = sum(
        ((activity.distance or Decimal("0")) for activity in activities),
        Decimal("0"),
    )
    goal.save(update_fields=["current_value", "updated_at"])


def _json_ready(value):
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


def _trace_case(name, *, input_data, output_data):
    print(f"\n=== {name} ===")
    print("INPUT:")
    print(json.dumps(input_data, indent=2, default=_json_ready))
    print("OUTPUT:")
    print(json.dumps(output_data, indent=2, default=_json_ready))


@pytest.mark.django_db
class TestGoalProgressService:
    def setup_method(self):
        self.user = User.objects.create_user(
            username="goal-progress-user",
            email="goal-progress@example.com",
            password="TestPass123!",
        )
        self.service = GoalProgressService()

    def test_manual_and_external_payloads_can_create_achieved_notification(self):
        goal = _create_goal_from_payload(self.user, target_value="30.00")
        manual_activity = _create_activity_from_payload(self.user, MANUAL_ACTIVITY_INPUT)
        external_activity = _create_activity_from_payload(self.user, EXTERNAL_ACTIVITY_INPUT)
        _sync_goal_distance(goal, manual_activity, external_activity)

        result = self.service.evaluate_goal(goal, computed_at=_dt(2026, 1, 15))

        goal.refresh_from_db()
        notification = Notification.objects.get()
        _trace_case(
            "achieved notification",
            input_data={
                "goal": {**GOAL_INPUT, "target_value": "30.00"},
                "activities": [MANUAL_ACTIVITY_INPUT, EXTERNAL_ACTIVITY_INPUT],
                "computed_at": "2026-01-15T12:00:00Z",
            },
            output_data={
                "result": result,
                "notification": notification.payload,
            },
        )
        assert result["state"] == Goal.ProgressState.ACHIEVED
        assert result["notification_created"] is True
        assert goal.progress_state == Goal.ProgressState.ACHIEVED
        assert notification.notification_type == Notification.NotificationType.GOAL_ACHIEVED
        assert notification.payload["previousState"] == Goal.ProgressState.ON_TRACK
        assert notification.payload["newState"] == Goal.ProgressState.ACHIEVED
        assert notification.payload["goalTitle"] == GOAL_INPUT["title"]
        assert notification.payload["progressSummary"]["actual"] == 32.5

    def test_manual_activity_payload_creates_at_risk_notification_once(self):
        goal = _create_goal_from_payload(self.user)
        manual_activity = _create_activity_from_payload(self.user, MANUAL_ACTIVITY_INPUT)
        _sync_goal_distance(goal, manual_activity)

        first = self.service.evaluate_goal(goal, computed_at=_dt(2026, 1, 15))
        second = self.service.evaluate_goal(goal, computed_at=_dt(2026, 1, 15))

        goal.refresh_from_db()
        assert first["state"] == Goal.ProgressState.AT_RISK
        assert second["notification_created"] is False
        assert goal.progress_state == Goal.ProgressState.AT_RISK
        assert Notification.objects.count() == 1
        notification = Notification.objects.get()
        _trace_case(
            "at risk notification",
            input_data={
                "goal": GOAL_INPUT,
                "activities": [MANUAL_ACTIVITY_INPUT],
                "computed_at": "2026-01-15T12:00:00Z",
            },
            output_data={
                "first_result": first,
                "second_result": second,
                "notification": notification.payload,
            },
        )
        assert notification.notification_type == Notification.NotificationType.GOAL_AT_RISK
        assert notification.payload["progressSummary"]["actual"] == 7.5

    def test_external_activity_payload_creates_missed_notification_after_deadline(self):
        goal = _create_goal_from_payload(self.user)
        external_activity = _create_activity_from_payload(self.user, EXTERNAL_ACTIVITY_INPUT)
        _sync_goal_distance(goal, external_activity)

        result = self.service.evaluate_goal(goal, computed_at=_dt(2026, 2, 1))

        notification = Notification.objects.get()
        _trace_case(
            "missed notification",
            input_data={
                "goal": GOAL_INPUT,
                "activities": [EXTERNAL_ACTIVITY_INPUT],
                "computed_at": "2026-02-01T12:00:00Z",
            },
            output_data={
                "result": result,
                "notification": notification.payload,
            },
        )
        assert result["state"] == Goal.ProgressState.MISSED
        assert notification.notification_type == Notification.NotificationType.GOAL_MISSED
        assert notification.payload["previousState"] == Goal.ProgressState.ON_TRACK
        assert notification.payload["newState"] == Goal.ProgressState.MISSED

    def test_manual_and_external_payloads_can_move_goal_back_to_on_track_without_notification(self):
        goal = _create_goal_from_payload(self.user)
        manual_activity = _create_activity_from_payload(self.user, MANUAL_ACTIVITY_INPUT)
        external_activity = _create_activity_from_payload(
            self.user,
            EXTERNAL_ACTIVITY_INPUT,
            external_id="strava_98765",
        )
        _sync_goal_distance(goal, manual_activity, external_activity)
        goal.progress_state = Goal.ProgressState.AT_RISK
        goal.progress_state_changed_at = timezone.now()
        goal.save(update_fields=["current_value", "progress_state", "progress_state_changed_at", "updated_at"])

        result = self.service.evaluate_goal(goal, computed_at=_dt(2026, 1, 15))

        goal.refresh_from_db()
        _trace_case(
            "on track transition",
            input_data={
                "goal": GOAL_INPUT,
                "activities": [
                    MANUAL_ACTIVITY_INPUT,
                    {**EXTERNAL_ACTIVITY_INPUT, "external_id": "strava_98765"},
                ],
                "computed_at": "2026-01-15T12:00:00Z",
                "previous_state": Goal.ProgressState.AT_RISK,
            },
            output_data={
                "result": result,
                "notification_count": Notification.objects.count(),
            },
        )
        assert result["state"] == Goal.ProgressState.ON_TRACK
        assert result["notification_created"] is False
        assert goal.progress_state == Goal.ProgressState.ON_TRACK
        assert goal.progress_state_changed_at is not None
        assert Notification.objects.count() == 0


@pytest.mark.django_db
class TestNotificationsAPI:
    def test_notifications_list_returns_only_authenticated_users_rows(self):
        user = User.objects.create_user(
            username="notifications-user",
            email="notifications@example.com",
            password="TestPass123!",
        )
        other_user = User.objects.create_user(
            username="other-notifications-user",
            email="other-notifications@example.com",
            password="TestPass123!",
        )
        own_goal = _create_goal_from_payload(user)
        own_manual_activity = _create_activity_from_payload(user, MANUAL_ACTIVITY_INPUT)
        _sync_goal_distance(own_goal, own_manual_activity)
        GoalProgressService().evaluate_goal(own_goal, computed_at=_dt(2026, 1, 15))

        other_goal = _create_goal_from_payload(other_user, title="Cycle 50km")
        other_external_activity = _create_activity_from_payload(
            other_user,
            EXTERNAL_ACTIVITY_INPUT,
            external_id="strava_other_12345",
        )
        _sync_goal_distance(other_goal, other_external_activity)
        GoalProgressService().evaluate_goal(other_goal, computed_at=_dt(2026, 2, 1))

        response = _auth_client(user).get("/api/v1/notifications/")

        _trace_case(
            "notifications list for one user",
            input_data={
                "request": "GET /api/v1/notifications/",
                "authenticated_user": user.email,
            },
            output_data={
                "status_code": response.status_code,
                "response": response.data,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Goal at risk: Run 50km"
        assert response.data[0]["notification_type"] == Notification.NotificationType.GOAL_AT_RISK

    def test_notifications_list_orders_newest_first(self):
        user = User.objects.create_user(
            username="ordering-user",
            email="ordering@example.com",
            password="TestPass123!",
        )
        older_goal = _create_goal_from_payload(user)
        older_manual_activity = _create_activity_from_payload(user, MANUAL_ACTIVITY_INPUT)
        _sync_goal_distance(older_goal, older_manual_activity)
        GoalProgressService().evaluate_goal(older_goal, computed_at=_dt(2026, 1, 15))

        newer_goal = _create_goal_from_payload(user, title="Cycle 30km", target_value="30.00")
        newer_manual_activity = _create_activity_from_payload(
            user,
            MANUAL_ACTIVITY_INPUT,
            date="2026-01-16",
        )
        newer_external_activity = _create_activity_from_payload(
            user,
            EXTERNAL_ACTIVITY_INPUT,
            date="2026-01-16",
            external_id="strava_ordering_12345",
        )
        _sync_goal_distance(newer_goal, newer_manual_activity, newer_external_activity)
        GoalProgressService().evaluate_goal(newer_goal, computed_at=_dt(2026, 1, 16))

        response = _auth_client(user).get("/api/v1/notifications/")

        _trace_case(
            "notifications list newest first",
            input_data={
                "request": "GET /api/v1/notifications/",
                "authenticated_user": user.email,
            },
            output_data={
                "status_code": response.status_code,
                "response": response.data,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["title"] == "Goal achieved: Cycle 30km"
        assert response.data[1]["title"] == "Goal at risk: Run 50km"
