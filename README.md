# TaskFlow API

TaskFlow API is a production-ready, high-performance, asynchronous REST API built with Python, FastAPI, and PostgreSQL. It is designed to serve as a robust task management platform with built-in JWT authentication, task filtering, sorting, pagination, and database migrations.

## Tech Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI (v0.111.0)
- **ASGI Server**: Uvicorn (v0.30.1)
- **Database Engine**: SQLAlchemy (v2.0.31) with asyncpg driver (v0.29.0)
- **Database**: PostgreSQL (v15+)
- **Migrations**: Alembic (v1.13.2)
- **Settings Management**: Pydantic Settings (v2.3.4)
- **Tests**: Pytest (v8.2.2)

---

## Database Schema (ER Diagram)

The relationship diagram below maps out user profiles, task structures, categories, and tags in the database:

```mermaid
erDiagram
    User ||--o{ Task : "owns"
    User ||--o{ Category : "owns"
    User ||--o{ Tag : "owns"
    Category ||--o{ Task : "classifies"
    Task }o--o{ Tag : "labeled by"

    User {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        boolean is_active
        timestamp created_at
    }
    Task {
        uuid id PK
        string title
        text description
        string status
        string priority
        timestamp due_date
        uuid user_id FK
        uuid category_id FK
        timestamp created_at
    }
    Category {
        uuid id PK
        string name
        uuid user_id FK
        timestamp created_at
    }
    Tag {
        uuid id PK
        string name
        uuid user_id FK
        timestamp created_at
    }
```

---

## Architecture Overview

TaskFlow API follows a clean layer separation architecture to isolate business concerns:

```mermaid
graph TD
    Client[Client Browser / Mobile App] <--> |HTTPS Requests| FastAPI[FastAPI Application]
    subgraph FastAPI App
        Router[API Router] <--> Service[Service Layer]
        Service <--> DB_Sess[SQLAlchemy AsyncSession]
    end
    DB_Sess <--> |asyncpg| DB[(PostgreSQL Database)]
```

---

## Planned API Endpoints

The planned API endpoints are structured by resource domain:

```mermaid
graph TD
    API[TaskFlow API]
    API --> Auth[Auth Resource]
    API --> Tasks[Tasks Resource]
    API --> Categories[Categories Resource]
    API --> Users[Users Resource]

    Auth --> POST_Login[POST /auth/login]
    Auth --> POST_Register[POST /auth/register]

    Tasks --> GET_Tasks[GET /tasks]
    Tasks --> POST_Tasks[POST /tasks]
    Tasks --> GET_Task["GET /tasks/{id}"]
    Tasks --> PUT_Task["PUT /tasks/{id}"]
    Tasks --> DELETE_Task["DELETE /tasks/{id}"]

    Categories --> GET_Categories[GET /categories]
    Categories --> POST_Categories[POST /categories]
    Categories --> GET_Category["GET /categories/{id}"]
    Categories --> PUT_Category["PUT /categories/{id}"]
    Categories --> DELETE_Category["DELETE /categories/{id}"]

    Users --> GET_Me[GET /auth/me]
```

### Endpoints Status Reference Table

| Resource | Method | Path | Description | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/auth/register` | Register a new user | Done (Commit 2) |
| **Auth** | `POST` | `/auth/login` | Authenticate user credentials & return JWT | Done (Commit 2) |
| **Auth** | `GET` | `/auth/me` | Retrieve profile of the current authenticated user | Done (Commit 2) |
| **Tasks** | `GET` | `/tasks` | Retrieve paginated tasks owned by user with filter & sort | Done (Commit 4) |
| **Tasks** | `POST` | `/tasks` | Create a new task (with optional category and tags) | Done (Commit 4) |
| **Tasks** | `GET` | `/tasks/{id}` | Retrieve details of a specific task by ID | Done (Commit 3) |
| **Tasks** | `PUT` | `/tasks/{id}` | Update details, category, or tags of a specific task | Done (Commit 4) |
| **Tasks** | `DELETE` | `/tasks/{id}` | Delete a specific task by ID | Done (Commit 3) |
| **Categories** | `GET` | `/categories` | Retrieve all categories owned by user | Done (Commit 4) |
| **Categories** | `POST` | `/categories` | Create a new category | Done (Commit 4) |
| **Categories** | `GET` | `/categories/{id}` | Retrieve details of a specific category by ID | Done (Commit 4) |
| **Categories** | `PUT` | `/categories/{id}` | Update a specific category's name | Done (Commit 4) |
| **Categories** | `DELETE` | `/categories/{id}` | Delete a category (tasks' category is set to NULL) | Done (Commit 4) |
| **Utility** | `GET` | `/health` | Verify database & server health check | Done (Commit 1) |

### `GET /tasks` Query Parameters Reference Table

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `status` | `string` | No | - | Filter by status: `todo`, `in_progress`, `done` |
| `priority` | `string` | No | - | Filter by priority: `low`, `medium`, `high` |
| `category_id` | `uuid` | No | - | Filter tasks associated with a specific category UUID |
| `tag` | `string` | No | - | Filter tasks associated with a specific tag name |
| `page` | `integer` | No | `1` | Pagination page number (starts at 1) |
| `limit` | `integer` | No | `10` | Maximum number of tasks to return per page |
| `sort` | `string` | No | `created_at` | Sort column: `due_date`, `created_at`, `priority`, `status`, `title` |
| `order` | `string` | No | `desc` | Sort direction: `asc` (ascending) or `desc` (descending) |


---

## JWT Authentication Flow

The sequence diagram below displays the end-to-end user registration and JWT token request lifecycle:

```mermaid
sequenceDiagram
    autonumber
    actor Client as Client App
    participant API as FastAPI App
    participant DB as PostgreSQL DB

    Note over Client, DB: JWT Authentication Flow
    Client->>API: POST /auth/register (email, password, full_name)
    API->>API: Hash password (bcrypt)
    API->>DB: Save User to DB
    DB-->>API: Confirm Save
    API-->>Client: Returns User Profile (UserRead)

    Client->>API: POST /auth/login (email, password)
    API->>DB: Fetch User by Email
    DB-->>API: User Data (hashed_password)
    API->>API: Verify Password (bcrypt)
    API->>API: Generate Access Token (JWT)
    API-->>Client: Returns JWT Access Token

    Client->>API: GET /auth/me (Authorization: Bearer <token>)
    API->>API: Validate JWT Signature (pyjwt)
    API->>DB: Query User from subject ID
    DB-->>API: User Object
    API-->>Client: Returns current user profile
```

---

## Request Lifecycle

The standard flow of an incoming HTTP request through the API layer:

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant MW as Middleware (CORS / Logging)
    participant Route as FastAPI Router (/tasks)
    participant Auth as Auth Dependency (JWT Verify)
    participant Service as Business Service (TaskService)
    participant DB as SQLAlchemy (AsyncSession)
    participant PG as PostgreSQL Database

    Client->>MW: HTTP Request
    MW->>Route: Pass request
    Route->>Auth: Authenticate Request
    Auth-->>Route: User Context
    Route->>Service: Call get_tasks(user_id)
    Service->>DB: Query Tasks
    DB->>PG: execute SELECT * FROM tasks
    PG-->>DB: Task Rows
    DB-->>Service: ORM Objects
    Service-->>Route: Return Task List
    Route-->>MW: Pydantic Response Schema
    MW-->>Client: JSON HTTP Response
```

---

## Local Setup Prerequisites

Ensure you have the following installed on your machine:
- **Python**: Version 3.11 or later.
- **PostgreSQL**: Local server or Docker container running PostgreSQL.
- **Tools**: Command-line terminal configured with Python (e.g. bash, zsh, powershell).
