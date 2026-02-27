# Group 11 Data Access Contract (Checkpoint 1)

## Purpose
Group 11 provides the persistence and data access layer. We define repository interfaces, data conventions, and dedup rules. We do not implement UI, business logic, or external API integrations.

## Data Conventions
- Time format: ISO 8601 string (e.g. 2026-02-26T21:15:00Z)
- Duration unit: seconds
- Distance unit: meters

## Naming Conventions
- Repository interfaces and persistence models use snake_case in Python:
  external_id, start_time, duration_seconds, distance_meters, target_value, period_start
- API layer may use camelCase, and conversion (if needed) is handled outside Group 11.

## Dedup and Upsert Rule (Activities)
An activity is uniquely identified by:
- provider + external_id

If the same provider and external_id appear again, update the existing record instead of creating a duplicate.

## Pagination
list_activities uses limit and offset.
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
- list_activities(user_id, from_time=None, to_time=None, limit=50, offset=0) -> Page[Activity]
- get_activity_by_id(activity_id) -> Activity | None

### GoalRepository
- create_goal(user_id, payload) -> Goal
- list_goals(user_id) -> list[Goal]
- get_goal_by_id(goal_id) -> Goal | None

## Example JSON

### Upsert Activity payload
```json
{
  "provider": "strava",
  "external_id": "123456789",
  "type": "run",
  "start_time": "2026-02-26T21:15:00Z",
  "duration_seconds": 1800,
  "distance_meters": 5200,
  "calories": 350
}

### Create Goal payload
{
  "type": "weekly_distance",
  "targetValue": 20000,
  "periodStart": "2026-02-24"
}
