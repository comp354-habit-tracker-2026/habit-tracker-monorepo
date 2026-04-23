# Group 11 Database Schema Refinement (Checkpoint 2)

This document refines the Group 11 PostgreSQL schema from Checkpoint 1.

This schema is aligned with:
- group_11/CONTRACT.md
- Repository interfaces: UserRepository, ActivityRepository, GoalRepository
- Snake_case naming convention
- PostgreSQL as the selected database

Checkpoint 2 focus:
- refine the schema so it clearly supports repository methods
- make constraints explicit
- clarify indexing strategy
- document how the schema supports deduplication, pagination, and retrieval

NOTE:
This is still a design-level schema document for Sprint #2. It is intended to prepare the persistence layer for future implementation.

---

## Design Goals

The schema is designed to support the following repository requirements:

### UserRepository
- create_user(user)
- get_user_by_id(user_id)
- get_user_by_email(email)

### ActivityRepository
- upsert_activity_by_source(user_id, provider, external_id, payload)
- list_activities(user_id, from_time=None, to_time=None, limit=50, offset=0)
- get_activity_by_id(activity_id)

### GoalRepository
- create_goal(user_id, payload)
- list_goals(user_id)
- get_goal_by_id(goal_id)

---

## Users table

Purpose:
Stores registered users and supports lookup by unique user identifier and email.

Fields:

id
- type: UUID
- primary key
- required

email
- type: TEXT
- required
- unique

display_name
- type: TEXT
- optional

created_at
- type: TIMESTAMP WITH TIME ZONE
- required
- default: now()

Constraints:
- PRIMARY KEY (id)
- UNIQUE (email)

Indexes:
- UNIQUE INDEX on email

Why this supports repository methods:
- create_user requires a unique user record
- get_user_by_id uses the primary key
- get_user_by_email uses the unique email lookup

---

## Activities table

Purpose:
Stores activity data imported from external providers and supports upsert, retrieval, and paginated listing.

Fields:

id
- type: UUID
- primary key
- required

user_id
- type: UUID
- foreign key -> users.id
- required

provider
- type: TEXT
- required

external_id
- type: TEXT
- required

type
- type: TEXT
- required

start_time
- type: TIMESTAMP WITH TIME ZONE
- required

duration_seconds
- type: INTEGER
- required

distance_meters
- type: INTEGER
- optional

calories
- type: INTEGER
- optional

created_at
- type: TIMESTAMP WITH TIME ZONE
- required
- default: now()

updated_at
- type: TIMESTAMP WITH TIME ZONE
- required
- default: now()

Constraints:
- PRIMARY KEY (id)
- FOREIGN KEY (user_id) REFERENCES users(id)
- UNIQUE (provider, external_id)

Indexes:
- INDEX on (user_id, start_time)
- INDEX on (provider, external_id)

Why this supports repository methods:
- upsert_activity_by_source is supported by UNIQUE(provider, external_id)
- get_activity_by_id uses the primary key
- list_activities(user_id, from_time, to_time, limit, offset) is supported by user_id and start_time indexing
- updated_at supports future update tracking for upsert behavior

Deduplication rule:
- An activity is uniquely identified by provider + external_id
- If the same provider and external_id are received again, the existing activity should be updated instead of inserting a duplicate

Pagination support:
- list_activities uses limit and offset
- the (user_id, start_time) index supports efficient time filtering and ordered retrieval

---

## Goals table

Purpose:
Stores user goals and supports creation and retrieval by user and goal identifier.

Fields:

id
- type: UUID
- primary key
- required

user_id
- type: UUID
- foreign key -> users.id
- required

type
- type: TEXT
- required

target_value
- type: INTEGER
- required

period_start
- type: DATE
- required

created_at
- type: TIMESTAMP WITH TIME ZONE
- required
- default: now()

Constraints:
- PRIMARY KEY (id)
- FOREIGN KEY (user_id) REFERENCES users(id)

Indexes:
- INDEX on (user_id)

Why this supports repository methods:
- create_goal inserts a goal for a user
- list_goals(user_id) is supported by the user_id index
- get_goal_by_id uses the primary key

---

## Schema Summary

This refined schema supports the Group 11 repository contract by providing:

- clear primary keys for entity retrieval
- foreign key relationships between users and dependent data
- a unique constraint for activity deduplication and upsert behavior
- indexes for paginated activity listing and goal retrieval
- field naming that matches CONTRACT.md and payload examples

This schema refinement is intended to make future implementation more consistent, reduce ambiguity, and ensure that repository behavior is supported directly by the database design.