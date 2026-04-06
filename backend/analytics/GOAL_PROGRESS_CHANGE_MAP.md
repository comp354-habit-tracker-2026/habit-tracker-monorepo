# Goal Progress Change Map

## Purpose

This feature computes a Group 15 goal progress health indicator from the goal data already stored in the database.

The synchronous v1 flow does four things:

1. reads a goal's stored values and dates
2. computes `ON_TRACK`, `AT_RISK`, `ACHIEVED`, or `MISSED`
3. persists the latest state on the goal
4. creates an in-app notification row when the new state is notifiable

This milestone does not use Celery, Redis, an outbox worker, or scheduled jobs.

## High-Level Flow

```text
Goal record from database
        |
        v
AnalyticsService.evaluate_goal_progress(...)
        |
        v
GoalProgressService.evaluate_goal(...)
        |
        +--> _compute_state(...)
        |       reads target/current values and dates
        |
        +--> updates goals_goal
        |
        +--> NotificationService.create_goal_progress_notification(...)
                |
                v
          notifications_notification
                |
                v
          GET /api/v1/notifications/
```

## File Roles

### `backend/analytics/business/services.py`

This file keeps the public entry point small:

- `AnalyticsService.evaluate_goal_progress(goal, computed_at=None)`

Future callers can use this method without needing to know how the lower-level calculation works.

### `backend/analytics/business/goal_progress.py`

This file owns the health-indicator workflow.

It:

- normalizes the timestamp for the check
- computes the next goal state
- compares it with the stored state
- persists `progress_state` and `progress_state_changed_at`
- creates an in-app notification when the state changes into `ACHIEVED`, `AT_RISK`, or `MISSED`

### `backend/goals/models.py`

This file stores the goal data used by the indicator, especially:

- `target_value`
- `current_value`
- `start_date`
- `end_date`
- `progress_state`
- `progress_state_changed_at`

The `goals_goal` table remains the source of truth for the latest computed indicator state.

### `backend/notifications/business/services.py`

This file owns the synchronous handoff from goal-state evaluation into an in-app notification.

`NotificationService.create_goal_progress_notification(...)`:

- receives the transition details
- builds the notification title and message
- stores a `Notification` row with a small payload for the frontend to read later

### `backend/notifications/models.py`

This file defines the `Notification` model stored in `notifications_notification`.

For this milestone, the important fields are:

- `user`
- `goal`
- `notification_type`
- `title`
- `message`
- `is_read`
- `payload`
- `created_at`

### `backend/notifications/presentation/views.py`

This file exposes the lightweight DRF endpoints for the synchronous version:

- `GET /api/v1/notifications/`
- `GET /api/v1/notifications/health/`

The list endpoint returns the current user's notification rows in a JSON-ready format. The health endpoint keeps the existing route working and returns the same data under `recent_notifications`.

### `backend/analytics/tests/test_goal_progress.py`

This file verifies both the state-transition behavior and the minimal list API.

It proves that:

- `ACHIEVED` creates one notification
- `AT_RISK` does not duplicate notifications on repeated checks
- `MISSED` creates the expected notification payload
- `ON_TRACK` updates the goal without creating a notification
- the notifications list returns only the authenticated user's rows
- the notifications list returns newest first

## Database Usage

### `goals_goal`

The flow reads a goal's stored values from this table and writes back:

- `progress_state`
- `progress_state_changed_at`

### `notifications_notification`

The flow writes to this table only when the new indicator state is notifiable.

The notification payload stores:

- `goalId`
- `goalTitle`
- `previousState`
- `newState`
- `computedAt`
- `progressSummary`

## What Is Next

Later milestones can add:

- scheduled checks
- async delivery
- an outbox worker
- email, push, or websocket channels

Those are intentionally out of scope for this synchronous v1.
