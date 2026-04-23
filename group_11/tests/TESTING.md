# Testing Strategy – Group 11 (Checkpoint 2)

## Overview

This document defines the testing strategy for the persistence layer.

Tests are defined at the design level and do not require a database.

---

## Repository Methods and Test Cases

### 1. create_user(user)

Test Cases:
- Valid user -> success
- Missing email -> ValidationError
- Duplicate email -> ConflictError

---

### 2. get_user_by_id(id)

Test Cases:
- Existing user -> return user
- Non-existing user -> NotFoundError

Edge Cases:
- Null id -> ValidationError

---

### 3. upsert_activity_by_source(provider, external_id)

Test Cases:
- New (provider, external_id) -> insert
- Existing (provider, external_id) -> update

Edge Cases:
- Duplicate external_id with different provider -> allowed
- Missing provider -> ValidationError

---

### 4. list_activities(user_id)

Test Cases:
- Activities exist -> return list
- No activities -> return empty list

Edge Cases:
- Invalid user_id -> ValidationError

---

### 5. create_goal(goal)

Test Cases:
- Valid goal -> success
- Missing target_value -> ValidationError

---

### 6. list_goals_by_user(user_id)

Test Cases:
- Goals exist -> return list
- No goals -> return empty list

---

## Error Handling

NotFoundError:
- Raised when resource is not found

ValidationError:
- Raised when input data is invalid

ConflictError:
- Raised when unique constraint is violated

---

## Testing Approach

- Tests will be implemented in Milestone 3
- Unit tests will target repository methods
- No database required in CP2

---

## Limitations

- No real test execution
- No database integration
- No performance testing
