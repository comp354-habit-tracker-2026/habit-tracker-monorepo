# Backend Architecture

## App Ownership

- `users`: Group 7 (Authentication and Authorization), Group 8 (User Management)
- `activities`: Group 9 (Activity and Workout Service)
- `goals`: Group 22 (Goal Definition Engine), Group 23 (Achievement Detection)
- `notifications`: Group 24 (Notification Delivery)
- `analytics`: Group 12 (Activity Statistics), Group 13 (Trend Analysis), Group 14 (Forecasting Engine), Group 15 (Health Indicators), Group 16 (Reporting and Insights)
- `core`: Group 10 (API Gateway and Versioning), Group 11 (Persistence and shared data access patterns)

## Layer Contract

Each app should keep this structure at a minimum:

- `presentation/`: HTTP concerns only (DRF views/viewsets, serializers)
- `business/`: Domain rules and orchestration
- `data/`: ORM queries, repositories, and persistence adapters

Compatibility files (`views.py`, `serializers.py`, `serialisers.py`) may re-export layer modules.

## Dependency Rules

- `presentation` can depend on `business` and serializers.
- `business` can depend on `data` and `core.business`.
- `data` can depend on ORM models and `core.data`.
- Feature apps must not import another app's `presentation` layer.
- Cross-app collaboration should use `business` service contracts, not direct view calls.

## API Boundaries

Current namespaces:

- `/api/v1/auth/`
- `/api/v1/activities/`
- `/api/v1/goals/`
- `/api/v1/analytics/`
- `/api/v1/notifications/`

## Team Integration Guidance

- Analytics team should implement pandas/numpy/scikit-learn logic in `analytics/business/` with repositories in `analytics/data/`.
- Goal achievement checks should live in `goals/business/` and notify through `notifications/business/` contracts.
- Notification channels (email/push/in-app) should be adapter-driven under `notifications/data/`.
- Shared API concerns (error shape, pagination conventions, auth policies) should be centralized under `core/`.

## Suggested Next Work

- Add Celery for scheduled goal checks and async notification delivery.
- Add `analytics` response serializers for stable frontend contracts.
- Add per-app unit tests for business/data layers and integration tests for cross-app workflows.

## Database Indexes

Recent performance work adds indexes for frequent reads in goals and gamification.

- Goals: composite indexes on `user` with `status`, `goal_type`, and `progress_state`, plus single-column indexes on `end_date` and `updated_at`.
- Progress logs: single-column indexes on `goal` and `activity` (in addition to the unique composite constraint).
- Gamification: composite indexes for badge/milestone lookup and user history ordering.
