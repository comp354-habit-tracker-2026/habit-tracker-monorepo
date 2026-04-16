# Group 11 – Data Flow & System Architecture (Milestone 3)

## System Structure

This is a layered architecture approach where each layer performs its functions and interacts with only the layers adjacent to it.
The success of this architecture has been tested by the implementation process, where methods of repositories interact with the database design through the controller calls.

---

## System Layers

- API/Controller Layer
Responsible for receiving requests from either the client or demo script. Input validation is done, and then repository functions are called accordingly.

- Repository Layer (Group 11)
Performs data access functions. It includes actions like user creation, record retrieval, listing of activities with pagination, and data updates using upsert.

- Database Layer
Manages persistent storage. This layer stores Users, Activities, and Goals. Constraints like primary key, foreign key, and uniqueness are enforced.

---

## Data Flow

1. The client/demo sends a request to the API/Controller layer.
2. The controller validates the data and decides which operation needs to be performed.
3. The controller calls the corresponding repository function.
4. The repository performs database actions (insert, read, update).
5. The database sends the results.
6. The result is sent back to the controller through the repository.
7. The controller sends the results back to the client.
   
The flow is consistent with the sequence diagrams established in the earlier milestones and proves that the system developed follows the planned architecture.

---

## Architecture Diagram

Client / Demo Script
        ↓
API / Controller
        ↓
Repository (Group 11)
        ↓
Database
        ↑
Repository
        ↑
API / Controller
        ↑
Response

---

### Design Principles

- Low Coupling
Each layer only communicates with its adjacent layers. The controller cannot directly communicate with the database, instead, it uses the repository layer to interact with the database.

- High Cohesion
Each layer has a specific job to do. For example, the controller takes care of the requests, the repository deals with the data access layer, and the database layer handles data storage.

- Controller Pattern
The controller acts as an interface between the client application and the database using the repository layer.



## Validation and Logic

The validation process is mainly done at the controller level, where the inputs are validated before passing them to the repository layer.

The repository layer  performs the logic for accessing the data without doing any business validation. The purpose is to ensure that there is a proper interface with the database and deduplication and pagination are taken care of.

The database layer enforces constraints like uniqueness and relationship enforcement on the data.
