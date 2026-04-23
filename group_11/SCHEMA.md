# Group 11 Draft Database Schema (Checkpoint 1)

This document defines the draft persistence models and PostgreSQL schema for Group 11.

This schema is aligned with:
- group_11/CONTRACT.md
- Repository interfaces: UserRepository, ActivityRepository, GoalRepository
- Snake_case naming convention

NOTE:
This is a draft schema for Checkpoint 1. No database is implemented yet.

---

## Users table

Purpose:
Stores registered users.

Fields:

id
- type: UUID
- primary key

email
- type: TEXT
- required
- unique

display_name
- type: TEXT
- optional

created_at
- type: TIMESTAMP WITH TIME ZONE
- default: now()

---

## Activities table

Purpose:
Stores activity data imported from external providers (Strava, Fitbit, etc).

Fields:

id
- type: UUID
- primary key

user_id
- type: UUID
- foreign key → users.id
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
- default: now()

updated_at
- type: TIMESTAMP WITH TIME ZONE
- default: now()

Constraints:

UNIQUE(provider, external_id)

This supports the CONTRACT.md dedup/upsert rule.

Indexes:

INDEX(user_id, start_time)

This supports list_activities queries with time filtering and pagination.

---

## Goals table

Purpose:
Stores user goals.

Fields:

id
- type: UUID
- primary key

user_id
- type: UUID
- foreign key → users.id
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
- default: now()

Indexes:

INDEX(user_id)

Supports list_goals queries.