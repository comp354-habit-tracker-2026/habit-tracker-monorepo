# Habit Tracker Backend

Django REST API for the Habit and Exercise Tracker Portal.

## Setup

# Clone and navigate to backend
```bash
git clone https://github.com/comp354-habit-tracker-2026/habit-tracker-monorepo.git
cd habit-tracker-monorepo/backend
```

# Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Run server
python manage.py runserver

# API Endpoints

## All endpoints require JWT authentication (except auth endpoints).

### Authentication

- Register new user
```
POST /api/v1/auth/register/
```

- Login (returns JWT tokens)
```
POST /api/v1/auth/login/
```

- Refresh access token
```
POST /api/v1/auth/refresh/
```

    

### Goals & Activities

- List/Create goals
```
GET/POST /api/v1/goals/
```
- Goal details
```
GET/PUT/PATCH/DELETE /api/v1/goals/{id}/
```
- List/Create activities
```
GET/POST /api/v1/activities/
```
- Activity details
```
GET/PUT/PATCH/DELETE /api/v1/activities/{id}/
```

# Quick Start Example

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Pass123!","password2":"Pass123!","email":"test@test.com"}'

# Login and get token
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Pass123!"}'

# Use token for protected endpoints
curl http://localhost:8000/api/v1/goals/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

# Testing

```bash
pytest -v  # Run all tests
```

# Key Models

User: Custom model with OAuth support (oauth_provider, oauth_provider_id)
Goal: title, description, target_value, current_value, goal_type, status, dates
Activity: activity_type, duration, date, provider, external_id, distance, calories

# Notes

Using SQLite (development) - will migrate to PostgreSQL
All endpoints use pagination (20 items/page)
User data isolation enforced - users can only see their own data
External provider support for activities (Strava, MapMyRun, etc.)
