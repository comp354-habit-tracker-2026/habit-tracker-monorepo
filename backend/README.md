# Habit Tracker Backend

Django REST API for the Habit and Exercise Tracker Portal.

## Architecture

The backend is organized by feature apps plus shared `core` primitives.

```text
backend/
  config/                # Django project config (settings, root urls, wsgi/asgi)
  core/                  # Shared presentation/business/data base primitives
  users/                 # Auth and user management
  activities/            # Activity and workout domain
  goals/                 # Goal definition and tracking domain
  analytics/             # Metrics, trends, forecasting API surface
  notifications/         # Notification delivery API surface
```

Each feature app follows layered modules:

```text
<app>/
  presentation/          # views/viewsets + HTTP orchestration
  business/              # Domain services and business logic
  data/                  # Repositories and query access
```

Compatibility files like `views.py` and `serialisers.py` may re-export from the layered modules.

For team ownership and dependency rules, see `backend/ARCHITECTURE.md`.

## Requirements

- Python 3.12+
- PostgreSQL 16+
- Docker + Docker Compose (recommended)

## Environment

Create `.env` directly (copy/paste):

```bash
cat > .env <<'EOF'
APP_ENV=development

DJANGO_SECRET_KEY=django-insecure-dev-only-change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

API_PORT=8000
GUNICORN_WORKERS=3
API_CONTAINER_NAME=habit-api

POSTGRES_DB=habit_tracker_db
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_IMAGE=postgres:16
POSTGRES_RESTART_POLICY=always
POSTGRES_CONTAINER_NAME=habit-postgres
EOF
```

Key variables used by Django/PostgreSQL:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `API_PORT`
- `GUNICORN_WORKERS`
- `API_CONTAINER_NAME`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_IMAGE`
- `POSTGRES_RESTART_POLICY`
- `POSTGRES_CONTAINER_NAME`

## Run With Docker Compose

Build and start services:

```bash
docker compose up --build -d
```

Services:

- API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

Container behavior:

- `api` waits for `postgres` healthcheck (`service_healthy`)
- Migrations run automatically on container startup
- API is served with Gunicorn (`config.wsgi:application`)
- PostgreSQL data is stored in a standard Docker named volume (`postgres_data`)
- Service/runtime values are loaded directly from `.env` via Compose `env_file`

Useful commands:

```bash
docker compose ps
docker compose logs -f api
docker compose down
```

## API Namespaces

All endpoints are under `/api/v1/`.

- Auth: `/api/v1/auth/`
- Activities: `/api/v1/activities/`
- Goals: `/api/v1/goals/`
- Analytics: `/api/v1/analytics/`
- Notifications: `/api/v1/notifications/`

All protected endpoints require JWT (`Authorization: Bearer <token>`).

Important: keep trailing slashes in endpoint URLs for POST/PUT/PATCH/DELETE, e.g. `/api/v1/activities/`.

## Quick API Test

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo1","email":"demo1@test.com","password":"StrongPass_123","password2":"StrongPass_123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo1","password":"StrongPass_123"}'
```

## Admin user
Load the .env into your shell and run: 

```bash
POSTGRES_HOST=127.0.0.1 \
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@example.com \
DJANGO_SUPERUSER_PASSWORD=StrongPass_123 \
python3.12 manage.py createsuperuser --noinput
```

## Database Seeding

Seed sample users, goals, and activities using the Django management command.

Local run:

```bash
python manage.py seed_db --users 10 --habits-per-user 3 --activities-per-user 12
```

Docker Compose run:

```bash
docker compose exec api python manage.py seed_db --users 10 --habits-per-user 3 --activities-per-user 12
```

Optional flags:

- `--clear` deletes activities, goals, and non-superuser accounts before seeding
- `--seed <int>` makes the data deterministic

## Testing

```bash
python -m pytest -q
```

## Notes

- PostgreSQL is the configured database backend.
- API is JSON-only and paginated by default (`PAGE_SIZE=20`).
- User data isolation is enforced by user-scoped querysets.
