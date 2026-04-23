# Group 11 – Sequence Diagrams (Checkpoint 2)

These are design-level sequence diagrams for Group 11 (Persistence & Data Access Layer).
All diagrams follow: User → Controller → Repository → Database.

---

## 1) Create User

```mermaid
sequenceDiagram
  autonumber
  actor User
  participant Controller
  participant Repo as UserRepository
  participant DB as PostgreSQL

  User->>Controller: POST /users {name, email}
  Controller->>Controller: validate(name, email format)
  Controller->>Repo: create_user(name, email)

  Repo->>DB: SELECT id FROM users WHERE email=?
  alt email exists
    DB-->>Repo: existing id
    Repo-->>Controller: ConflictError
    Controller-->>User: 409 Conflict
  else new email
    DB-->>Repo: none
    Repo->>DB: INSERT user RETURNING id
    DB-->>Repo: new id
    Repo-->>Controller: User{id, name, email}
    Controller-->>User: 201 Created + User
  end
```
## 2) Upsert Activity
```mermaid
sequenceDiagram
  autonumber
  actor User
  participant Controller
  participant Repo as ActivityRepository
  participant DB as PostgreSQL

  User->>Controller: POST /users/{user_id}/activities {provider, external_id, ...}
  Controller->>Controller: validate(user_id, provider, external_id, timestamps)
  Controller->>Repo: upsert_activity_by_source(user_id, provider, external_id, payload)

  Repo->>DB: SELECT id FROM activities WHERE provider=? AND external_id=?
  alt activity exists
    DB-->>Repo: existing activity id
    Repo->>DB: UPDATE activities SET ... WHERE id=? RETURNING *
    DB-->>Repo: updated row
    Repo-->>Controller: Activity
    Controller-->>User: 200 OK + Activity
  else new activity
    DB-->>Repo: none
    Repo->>DB: INSERT INTO activities (...) RETURNING *
    DB-->>Repo: inserted row
    Repo-->>Controller: Activity
    Controller-->>User: 201 Created + Activity
  end
```
## 3) List Activities (Pagination)
```mermaid
sequenceDiagram
  autonumber
  actor User
  participant Controller
  participant Repo as ActivityRepository
  participant DB as PostgreSQL

  User->>Controller: GET /users/{user_id}/activities?from&to&limit&offset
  Controller->>Controller: validate(limit<=200, offset>=0, from<=to)
  Controller->>Repo: list_activities(user_id, from_time, to_time, limit, offset)

  Repo->>DB: SELECT * FROM activities WHERE user_id=? AND time filters ORDER BY start_time DESC LIMIT ? OFFSET ?
  DB-->>Repo: rows (maybe empty)
  Repo-->>Controller: Page[Activity]{items, limit, offset}
  Controller-->>User: 200 OK + Page
```
## 4) Create Goal
```mermaid
sequenceDiagram
  autonumber
  actor User
  participant Controller
  participant Repo as GoalRepository
  participant DB as PostgreSQL

  User->>Controller: POST /users/{user_id}/goals {type, target_value, period_start}
  Controller->>Controller: validate(type, target_value>0, period_start)
  Controller->>Repo: create_goal(user_id, payload)

  Repo->>DB: INSERT INTO goals (...) RETURNING *
  alt invalid user_id (FK fails)
    DB-->>Repo: FK violation error
    Repo-->>Controller: NotFoundError or ValidationError
    Controller-->>User: 400/404
  else success
    DB-->>Repo: inserted row
    Repo-->>Controller: Goal
    Controller-->>User: 201 Created + Goal
  end


