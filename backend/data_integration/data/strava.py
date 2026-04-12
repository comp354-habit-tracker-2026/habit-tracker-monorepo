from __future__ import annotations

import json
from datetime import date, datetime, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from data_integration.business.strava_activity_factory import StravaActivityFactory
from data_integration.business.strava_activity_summary import StravaActivitySummary

class StravaAuthService:
    TOKEN_URL = "https://www.strava.com/oauth/token"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def authenticate_user(self, auth_code: str) -> dict[str, Any]:
        """Exchanges the temporary code for access and refresh tokens."""
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
        }
        return self._send_request(payload)

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Uses a refresh token to get a new access token."""
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        return self._send_request(payload)

    def _send_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Internal helper to handle the urllib POST and JSON parsing."""
        data = urlencode(payload).encode("utf-8")
        request = Request(self.TOKEN_URL, data=data, method="POST")
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))

    # Compatibility wrapper for the specific camelCase requirement
    def authenticateUser(self, authCode: str) -> dict[str, Any]:
        return self.authenticate_user(authCode)

class StravaActivityFetcher:
    """Adapter for fetching summary activities from the Strava API."""

    base_url = "https://www.strava.com/api/v3"
    default_page_size = 30
    max_page_size = 200
    skiing_sport_types = frozenset({"AlpineSki", "BackcountrySki", "NordicSki", "RollerSki"})

    def get_all_activities(
        self,
        access_token: str,
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
    ) -> list[StravaActivitySummary]:
        params = self._build_query_params(start_date=start_date, end_date=end_date)

        raw_activities: list[dict[str, Any]] = []
        page = 1

        while True:
            page_params = dict(params)
            page_params["page"] = page
            activities_page = self._request_activities(access_token, page_params)

            if not activities_page:
                break

            raw_activities.extend(activities_page)

            requested_page_size = int(page_params["per_page"])
            if len(activities_page) < requested_page_size:
                break

            if start_date is None and end_date is None:
                break

            page += 1

        return StravaActivityFactory.create_many(raw_activities)

    def getAllActivities(
        self,
        accessToken: str,
        startDate: date | datetime | str | None = None,
        endDate: date | datetime | str | None = None,
    ) -> list[StravaActivitySummary]:
        """Compatibility wrapper for the requested camelCase method name."""

        return self.get_all_activities(
            access_token=accessToken,
            start_date=startDate,
            end_date=endDate,
        )

    def get_skiing_activities(
        self,
        activities: list[StravaActivitySummary],
    ) -> list[StravaActivitySummary]:
        """Filters an extracted activity list down to skiing activities only."""
        return [
            activity
            for activity in activities
            if activity.sport_type in self.skiing_sport_types
        ]

    def getSkiingActivities(
        self,
        activities: list[StravaActivitySummary],
    ) -> list[StravaActivitySummary]:
        """Compatibility wrapper for the camelCase method name."""
        return self.get_skiing_activities(activities)

    def get_indoor_cycling_activities(
        self,
        activities: list[StravaActivitySummary],
    ) -> list[StravaActivitySummary]:
        """Filters an extracted activity list down to indoor cycling activities only."""
        return [
            activity
            for activity in activities
            if activity.sport_type == "VirtualRide"
        ]

    def getIndoorCyclingActivities(
        self,
        activities: list[StravaActivitySummary],
    ) -> list[StravaActivitySummary]:
        """Compatibility wrapper for the camelCase method name."""
        return self.get_indoor_cycling_activities(activities)

    def _build_query_params(
        self,
        start_date: date | datetime | str | None,
        end_date: date | datetime | str | None,
    ) -> dict[str, int]:
        params: dict[str, int] = {
            "per_page": self.default_page_size if start_date is None and end_date is None else self.max_page_size,
        }

        after = self._to_epoch(start_date, end_of_day=False)
        before = self._to_epoch(end_date, end_of_day=True)

        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before

        return params

    def _request_activities(
        self,
        access_token: str,
        params: dict[str, int],
    ) -> list[dict[str, Any]]:
        request = Request(
            url=f"{self.base_url}/athlete/activities?{urlencode(params)}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            method="GET",
        )

        with urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))

        if not isinstance(payload, list):
            raise ValueError("Expected Strava activities response to be a list.")

        return [activity for activity in payload if isinstance(activity, dict)]

    @staticmethod
    def _to_epoch(
        value: date | datetime | str | None,
        *,
        end_of_day: bool,
    ) -> int | None:
        if value is None:
            return None

        parsed = StravaActivityFetcher._coerce_datetime(value, end_of_day=end_of_day)
        return int(parsed.timestamp())

    @staticmethod
    def _coerce_datetime(
        value: date | datetime | str,
        *,
        end_of_day: bool,
    ) -> datetime:
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, date):
            if end_of_day:
                parsed = datetime(value.year, value.month, value.day, 23, 59, 59)
            else:
                parsed = datetime(value.year, value.month, value.day)
        elif isinstance(value, str):
            normalized = value.strip().replace("Z", "+00:00")
            try:
                parsed = datetime.fromisoformat(normalized)
            except ValueError:
                parsed_date = date.fromisoformat(value.strip())
                if end_of_day:
                    parsed = datetime(parsed_date.year, parsed_date.month, parsed_date.day, 23, 59, 59)
                else:
                    parsed = datetime(parsed_date.year, parsed_date.month, parsed_date.day)
        else:
            raise TypeError("Date values must be date, datetime, ISO 8601 string, or None.")

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
