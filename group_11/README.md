Group 11 – Persistence & Data Access Layer

Group 11 Scope

Group 11 will take care of the repository/database access part in the system.


What We Are Responsible For

We are responsible for the following

- Decide how data is stored
- Provide repository interfaces for other backend teams
- Manage database connections and data access
- Prevent services from talking directly to the database

We only handle data. We don’t handle business logic or how it looks.


What We Are NOT Responsible For

We don’t handle

- Frontend or UI
- Business logic or workflows
- Authentication (like login or JWT)
- External API integrations

This helps keep the backend loosely coupled and the architecture clean.



Architecture Overview
Architectural Style

We use layers. Each layer only talks to the layers on either side of it.

Service Layer 
↓  
Repository Layer (Group 11)
↓  
Database

- The Service Layer contains our business logic. It only uses methods from the repository.
- The Repository Layer talks to the database.
- The Service Layer does not talk to the database.

Data Flow

1. A service function is called. It might be creating a goal.
2. The service asks the repository to do something.
3. The repository talks to the database.
4. The database sends back the result.
5. The repository sends the result back to the service.

Database Decision (Checkpoint 1 Status)

Group 11 will use PostgreSQL as the database for this project
Database schema draft: see group_11/SCHEMA.md

As the system has clearly defined parts such as User, Goal, Activity, a relational database will suit the system well. 

Checkpoint 1 Status



Group 11 has completed the following for CP1:
- Architecture
- Scope
- Defining the repository structure
- Folder scaffolding
- Documentation

The database will be integrated in the next milestone.

## Checkpoint 2 Status

Group 11 has completed the following for CP2:
- Architecture and data flow documentation
- Repository logic design
- Testing strategy
- Sequence diagrams
- Database schema refinement

Checkpoint 2 database schema refinement:
- group_11/SCHEMA_CP2.md

The CP2 schema refinement makes the persistence design more explicit by documenting:
- primary keys and foreign keys
- unique constraints
- indexing strategy
- repository method support
- pagination and deduplication behavior


## Milestone 3 Database Setup

For Milestone 3, Group 11 now includes a working local SQLite database setup for the persistence layer.

Files:
- `group_11/db/schema.sql`
- `group_11/db/connection.py`
- `group_11/db/init_db.py`

This implementation supports the repository contract for:
- users
- activities
- goals

To initialize the database, run:

```bash
python -m group_11.db.init_db

