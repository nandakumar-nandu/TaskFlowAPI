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
    API --> Users[Users Resource]

    Auth --> POST_Login[POST /api/v1/auth/login]
    Auth --> POST_Register[POST /api/v1/auth/register]

    Tasks --> GET_Tasks[GET /api/v1/tasks]
    Tasks --> POST_Tasks[POST /api/v1/tasks]
    Tasks --> GET_Task[GET /api/v1/tasks/{id}]
    Tasks --> PUT_Task[PUT /api/v1/tasks/{id}]
    Tasks --> DELETE_Task[DELETE /api/v1/tasks/{id}]

    Users --> GET_Me[GET /api/v1/users/me]
    Users --> PUT_Me[PUT /api/v1/users/me]
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
