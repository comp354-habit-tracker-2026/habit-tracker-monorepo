# Group 11 – Data Flow & System Architecture CP2

## System Structure

This system follows the principle of layered architecture where each layer is responsible for its own functionality and does not communicate with others.

---

## System Layers

- API / Controller Layer
Takes care of requests, validates them and uses the necessary functions.

- Repository Layer (Group 11)
Concerned with the data access and interaction with the database.

- Database Layer
Holds the actual data such as Users, Activities and Goals.

---

## Data Flow

1. User request goes to API/Controller.
2. Controller checks the request.
3. Controller uses repository.
4. Repository interacts with the database.
5. Database responds with an answer.
6. Result goes back to the user.

---

## Architecture Diagram
User
↓
API / Controller
↓
Repository (Group 11)
↓
Database

---

### Design Principles

- Low Coupling: Each layer operates independently of other layers.
- High Cohesion: Each layer has its specific functionality assigned to it.
- Controller Pattern: The controller serves as the mediator between the user and data layers.




