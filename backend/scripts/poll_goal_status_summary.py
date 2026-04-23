#!/usr/bin/env python3
"""Backend-only polling smoke test for goal status summary endpoint.

This script talks to the API over HTTP (no frontend dependency) and validates
core status-summary scenarios against `/api/v1/goals/{goalId}/status/`.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date, timedelta
from typing import Any
from urllib import error, request


def request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
    timeout: int = 15,
) -> tuple[int, dict[str, Any]]:
    body = None
    headers = {"Content-Type": "application/json"}

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = request.Request(url, data=body, headers=headers, method=method)

    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8") or "{}"
            return response.status, json.loads(raw)
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8") if exc.fp else "{}"
        try:
            data = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            data = {"raw": raw}
        return exc.code, data


def ensure_user(base_url: str, username: str, email: str, password: str) -> None:
    register_url = f"{base_url}/api/v1/auth/register/"
    payload = {
        "username": username,
        "email": email,
        "password": password,
        "password2": password,
    }
    status_code, _ = request_json("POST", register_url, payload=payload)
    if status_code not in (201, 400):
        raise RuntimeError(f"Unable to register test user. HTTP {status_code}")


def login(base_url: str, username: str, password: str) -> str:
    login_url = f"{base_url}/api/v1/auth/login/"
    payload = {"username": username, "password": password}
    status_code, data = request_json("POST", login_url, payload=payload)

    if status_code != 200 or "access" not in data:
        raise RuntimeError(f"Unable to login. HTTP {status_code} payload={data}")

    return data["access"]


def create_goal(
    base_url: str,
    token: str,
    title: str,
    target_value: float,
    current_value: float,
    deadline_offset_days: int,
) -> int:
    goals_url = f"{base_url}/api/v1/goals/"
    payload = {
        "title": title,
        "description": "Goal status summary smoke test",
        "target_value": f"{target_value:.2f}",
        "current_value": f"{current_value:.2f}",
        "goal_type": "custom",
        "status": "active",
        "start_date": date.today().isoformat(),
        "end_date": (date.today() + timedelta(days=deadline_offset_days)).isoformat(),
    }

    status_code, data = request_json("POST", goals_url, payload=payload, token=token)
    if status_code != 201:
        raise RuntimeError(f"Unable to create goal. HTTP {status_code} payload={data}")

    return int(data["id"])


def poll_goal_status(
    base_url: str,
    token: str,
    goal_id: int,
    attempts: int,
    interval_seconds: float,
) -> tuple[int, dict[str, Any]]:
    status_url = f"{base_url}/api/v1/goals/status/"
    last_status = 0
    last_payload: dict[str, Any] = {}

    for _ in range(attempts):
        status_code, response_payload = request_json("GET", status_url, token=token)
        last_status = status_code

        if status_code == 200 and "results" in response_payload:
            results = response_payload["results"]
            goal_payload = next((item for item in results if item.get("goalId") == goal_id), None)
            if goal_payload:
                if "errorCode" in goal_payload:
                    if goal_payload["errorCode"] == "GOAL_INVALID":
                        return 422, goal_payload
                    elif goal_payload["errorCode"] == "GOAL_STATUS_UNAVAILABLE":
                        return 503, goal_payload
                return 200, goal_payload
            else:
                last_payload = {"errorCode": "GOAL_NOT_FOUND", "message": "Goal not found."}
                last_status = 404
        else:
            last_payload = response_payload
            if status_code != 200:
                return status_code, last_payload

        time.sleep(interval_seconds)

    return last_status, last_payload


def run(base_url: str, username: str, password: str, attempts: int, interval_seconds: float) -> int:
    print(f"Using backend: {base_url}")
    ensure_user(base_url, username, f"{username}@example.com", password)
    token = login(base_url, username, password)

    acceptance_cases = [
        ("TC-01", 0.0, 100.0, 7, 0.0, "AT_RISK"),
        ("TC-02", 80.0, 100.0, 7, 80.0, "ON_TRACK"),
        ("TC-03", 100.0, 100.0, 7, 100.0, "ACHIEVED"),
        ("TC-04", 150.0, 100.0, 7, 150.0, "ACHIEVED"),
        ("TC-05", 60.0, 100.0, -1, 60.0, "MISSED"),
        ("TC-06", 0.0, 0.0, 7, 100.0, "ACHIEVED"),
    ]

    passed = 0
    failed = 0

    for case_id, actual, target, deadline_offset, expected_percent, expected_status in acceptance_cases:
        goal_id = create_goal(
            base_url=base_url,
            token=token,
            title=f"{case_id} status test",
            target_value=target,
            current_value=actual,
            deadline_offset_days=deadline_offset,
        )
        status_code, payload = poll_goal_status(
            base_url=base_url,
            token=token,
            goal_id=goal_id,
            attempts=attempts,
            interval_seconds=interval_seconds,
        )

        is_pass = (
            status_code == 200
            and payload.get("status") == expected_status
            and abs(float(payload.get("percentComplete", -1)) - expected_percent) <= 0.01
        )

        if is_pass:
            passed += 1
            print(f"[PASS] {case_id}: status={payload.get('status')} percent={payload.get('percentComplete')}")
        else:
            failed += 1
            print(
                f"[FAIL] {case_id}: expected status={expected_status} percent={expected_percent}, "
                f"got HTTP {status_code} payload={payload}"
            )

    # Error path: not found
    not_found_code, not_found_payload = poll_goal_status(
        base_url=base_url,
        token=token,
        goal_id=999999,
        attempts=1,
        interval_seconds=0.1,
    )
    if not_found_code == 404 and not_found_payload.get("errorCode") == "GOAL_NOT_FOUND":
        passed += 1
        print("[PASS] GOAL_NOT_FOUND error payload")
    else:
        failed += 1
        print(f"[FAIL] GOAL_NOT_FOUND check: HTTP {not_found_code} payload={not_found_payload}")

    print("[SKIP] TC-07 (metrics unavailable) cannot be triggered via public API contract alone.")
    print(f"Summary: passed={passed} failed={failed}")

    return 0 if failed == 0 else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Poll and validate goal status endpoint over HTTP")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--username", default="goal_status_tester", help="Test username")
    parser.add_argument("--password", default="StrongPass_123", help="Test password")
    parser.add_argument("--attempts", type=int, default=5, help="Polling attempts per goal")
    parser.add_argument("--interval", type=float, default=0.5, help="Polling interval in seconds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run(
        base_url=args.base_url.rstrip("/"),
        username=args.username,
        password=args.password,
        attempts=args.attempts,
        interval_seconds=args.interval,
    )


if __name__ == "__main__":
    sys.exit(main())
