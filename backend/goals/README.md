# Goals API 

Documentation for Goals API endpoints.
All endpoints require authentication and are prefixed with /api/v1/goals/.
Users may only access and alter their own goals.

## Endpoints

GET    /api/v1/goals/                list all goals for authenticated user
POST   /api/v1/goals/                create new goal
GET    /api/v1/goals/{id}/           get single goal
PUT    /api/v1/goals/{id}/           update goal
DELETE /api/v1/goals/{id}/           delete goal
GET    /api/v1/goals/{id}/progress/  get progress summary for goal

## Writeable Fields

title         required, string
target_value  required, decimal
start_date    required, YYYY-MM-DD
end_date      required, YYYY-MM-DD
description   optional, string
current_value optional, decimal, defaults to 0
goal_type     optional, choices: distance / duration / frequency / calories / custom
status        optional, choices: active / completed / paused / failed


**Progress endpoint response**
percent_complete, on_track (bool), days_remaining, summary (string)

## Goal Object

All endpoints returning a goal use this format:

```json
{
  "id": 1,
  "title": "Run a 5K",
  "description": "Train and complete a 5K race",
  "target_value": "5.00",
  "current_value": "2.50",
  "goal_type": "distance",
  "status": "active",
  "progress_state": "ON_TRACK",
  "progress_state_changed_at": "2026-03-01T10:00:00Z",
  "start_date": "2024-01-01",
  "end_date": "2024-06-01",
  "progress_percentage": 50.0,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-10T00:00:00Z"
}
```

## Errors

400  invalid ID format or bad request body
403  goal belongs to a different user
404  goal not found
409  integrity error on create
500  database error on create

## Notes

All endpoints need authentication
Users only see their own goals
progress_state and progress_percentage are read-only
start_date and end_date are required even on update

---

## Examples
### Create Goal
**Request**

`POST /api/v1/goals/` creates a new goal for user

```json
{
  "title": "Run a 5K",
  "goal_type": "distance",
  "target_value": 5.0,
  "start_date": "2026-01-01",
  "end_date": "2026-06-01",
  "description": "optional",
  "current_value": 0
}
```

**Response** : 201 Created
```json
{
  "id": 1,
  "title": "Run a 5K",
  "goal_type": "distance",
  "target_value": "5.00",
  "current_value": "0.00",
  "status": "active",
  "progress_percentage": 0.0,
  "progress_state": "ON_TRACK",
  "start_date": "2026-01-01",
  "end_date": "2026-06-01",
  "created_at": "2026-01-01T00:00:00Z"
}
```
**Errors**: 400 invalid fields , 409 duplicate entry , 500 database error

### List Goals
**Request**

`GET /api/v1/goals/` returns all goals of the user

**Parameters**
search    : filters by title, description, goal_type, or status
ordering  : sort by field, prefix with - for descending e.g. -created_at

**Response** : 200 OK
```json
{
  "id": 1,
  "title": "Run a 5K",
  "goal_type": "distance",
  "target_value": "5.00",
  "current_value": "2.50",
  "status": "active",
  "progress_percentage": 50.0,
  "progress_state": "ON_TRACK",
  "start_date": "2026-01-01",
  "end_date": "2026-06-01",
  "created_at": "2026-01-01T00:00:00Z"
}
```
**Errors**: 401 not authenticated

### Retrieve Goal
**Request**

`GET /api/v1/goals/{id}/` returns a single goal by ID

**Response** : 200 OK
```json
{
  "id": 1,
  "title": "Run a 5K",
  "goal_type": "distance",
  "target_value": "5.00",
  "current_value": "2.50",
  "status": "active",
  "progress_percentage": 50.0,
  "progress_state": "ON_TRACK",
  "start_date": "2026-01-01",
  "end_date": "2026-06-01",
  "created_at": "2026-01-01T00:00:00Z"
}
```
**Errors**: 403 goal belongs to another user, 404 goal not found

### Update goal
**Request**

`PUT /api/v1/goals/{id}/` updates a goal, required fields mandatory.

**Request**
```json
{
  "id": 1,
  "title": "Run a 5K",
  "goal_type": "distance",
  "target_value": "5.00",
  "current_value": "2.50",
  "status": "active",
  "progress_percentage": 50.0,
  "progress_state": "ON_TRACK",
  "start_date": "2026-01-01",
  "end_date": "2026-06-01",
  "created_at": "2026-01-01T00:00:00Z"
}
```

**Response**: 200 OK
```json
{
  "id": 1,
  "title": "Run a 5K",
  "goal_type": "distance",
  "target_value": "5.00",
  "current_value": "2.50",
  "status": "active",
  "progress_percentage": 50.0,
  "progress_state": "ON_TRACK",
  "start_date": "2026-01-01",
  "end_date": "2026-06-01",
  "created_at": "2026-01-01T00:00:00Z"
}
```
**Errors**:400 invalid ID, 403 goal belongs to a different user, 404 goal not found

### Delete Goal
**Request**

`DELETE /api/v1/goals/{id}/` deletes a goal.

**Response**: 200 OK
```json
{
  "detail": "Goal deleted successfully."
}
```
**Errors**:400 invalid ID, 403 goal belongs to a different user, 404 goal not found

### Goal Progress
**At this time get_goal_progress() is not implemented thus this feature is not complete or functional**

**Request**

`GET /api/v1/goals/{id}/progress/` returns the progress summary of a goal.

**Response**: 200 OK
```json
{
  "current_value": "3.00",
  "target_value": "5.00",
  "percent_complete": 60.0,
  "on_track": true,
  "days_remaining": 90,
  "summary": "On track — 60.0% done with 90 days remaining."
}
```
**Errors**:400 invalid ID, 403 goal belongs to a different user, 404 goal not found