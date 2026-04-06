Analytics API – Usage Documentation

Overview
--------
The Analytics API provides endpoints that allow the frontend to retrieve user-specific activity insights such as statistics, personal records, trends, and summaries.

This module acts as a presentation layer between the frontend and the analytics logic implemented by Team 12, Team 13, Team 14 and Team 15. It receives HTTP requests, ensures authentication, calls the appropriate service methods, and returns structured JSON responses.

---------------------------------------------------------------------

Authentication
--------------
All endpoints require authentication.

The API uses Django REST Framework’s permission system:

    permission_classes = [IsAuthenticated]

This ensures:
- Only authenticated users can access the endpoints
- Each request is tied to request.user
- Returned data is specific to the logged-in user

If authentication is missing or invalid, the API returns:

    401 Unauthorized

---------------------------------------------------------------------

Base URL
--------
/api/v1/analytics/

---------------------------------------------------------------------

Endpoints
---------

1. Analytics Overview
--------------------
GET /api/analytics/overview/

Description:
Returns a combined summary of analytics data. This endpoint is useful for dashboards where multiple insights are needed in a single request.

Example Response:
{
  "activity_statistics": { ... },
  "trend_analysis": { ... },
  "forecast": { ... }
}

---------------------------------------------------------------------

2. Activity Statistics
----------------------
GET /api/analytics/activity-statistics/

Description:
Returns general statistics about the user’s activities.

Example Response:
{
  "total_activities": 24,
  "total_distance": 112.5,
  "total_duration": 540
}

Service Method Used:
Team12AnalyticsService().activity_statistics(request.user)

---------------------------------------------------------------------

3. Personal Records
-------------------
GET /api/analytics/personal-records/

Description:
Returns the user’s personal best metrics.

Example Response:
{
  "longest_run_km": 12.4,
  "fastest_pace": "5:10/km"
}

Service Method Used:
Team12AnalyticsService().personal_records(request.user)

---------------------------------------------------------------------

4. Activity Type Breakdown
--------------------------
GET /api/analytics/activity-type-breakdown/

Description:
Returns the distribution of activities by type.

Example Response:
{
  "running": 12,
  "cycling": 7,
  "walking": 5
}

Service Method Used:
Team12AnalyticsService().activity_type_breakdown(request.user)

---------------------------------------------------------------------

5. Weekly Summary
-----------------
GET /api/analytics/weekly-summary/?from=YYYY-MM-DD&to=YYYY-MM-DD

Optional parameter:
activity_type=running

Description:
Returns summary data for a given date range.

Parameters:
- from (required): Start date
- to (required): End date
- activity_type (optional): Filter by activity type

Example Request:
/api/analytics/weekly-summary/?from=2026-04-01&to=2026-04-07

Example Response:
{
  "total_activities": 4,
  "total_distance": 21.8,
  "total_duration": 130
}

Service Method Used:
Team12AnalyticsService().weekly_summary(user, from_param, to_param, activity_type)

---------------------------------------------------------------------

6. Activity Streaks
-------------------
GET /api/analytics/activity-streaks/

Description:
Returns information about the user’s activity streaks.

Example Response:
{
  "current_streak": 5,
  "longest_streak": 14
}

Service Method Used:
Team12AnalyticsService().activity_streaks(request.user)

---------------------------------------------------------------------

Frontend Usage
--------------
These endpoints can be used by the frontend to display:
- Dashboard summaries
- Charts and graphs
- Progress tracking
- Weekly reports
- Activity breakdowns
- Streak indicators

All requests must include valid authentication credentials.

---------------------------------------------------------------------

Error Handling
--------------
401 Unauthorized:
{
  "detail": "Authentication credentials were not provided."
}

400 Bad Request (example):
{
  "error": "Missing required query parameters"
}

---------------------------------------------------------------------

Maintainers
-----------
Group 16 – Analytics API and Export

This module exposes analytics insights through authenticated API endpoints for frontend consumption.