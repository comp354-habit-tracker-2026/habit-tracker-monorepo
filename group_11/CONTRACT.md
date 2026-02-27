# Group 11 Data Access Contract (Checkpoint 1)

## Purpose
Group 11 provides the persistence and data access layer.
We define repository interfaces, data conventions, and dedup rules.
We do not implement UI, business logic, or external API integrations.

## Data Conventions
- Time format: ISO 8601 string (e.g. 2026-02-26T21:15:00Z)
- Duration unit: seconds
- Distance unit: meters

## Dedup and Upsert Rule (Activities)
An activity is uniquely identified by:
- provider + externalId
If the same provider and externalId appear again, update the existing record instead of creating a duplicate.

## Pagination
listActivities uses limit and offset.
- default limit: 50
- max limit: 200

## Error Behavior
Repository methods may raise:
- NotFoundError: entity not found
- ValidationError: invalid input
- ConflictError: unique constraint violation

## Repositories

### UserRepository
- create_user(user) -> User
- get_user_by_id(user_id) -> User | None
- get_user_by_email(email) -> User | None

### ActivityRepository
- upsert_activity_by_source(user_id, provider, external_id, payload) -> Activity
- list_activities(user_id, from_time, to_time, limit, offset) -> Page[Activity]
- get_activity_by_id(activity_id) -> Activity | None

### GoalRepository
- create_goal(user_id, payload) -> Goal
- list_goals(user_id) -> list[Goal]
- get_goal_by_id(goal_id) -> Goal | None

## Example JSON

### Upsert Activity payload
{
  "provider": "strava",
  "externalId": "123456789",
  "type": "run",
  "startTime": "2026-02-26T21:15:00Z",
  "durationSeconds": 1800,
  "distanceMeters": 5200,
  "calories": 350
}

### Create Goal payload
{
  "type": "weekly_distance",
  "targetValue": 20000,
  "periodStart": "2026-02-24"
}
