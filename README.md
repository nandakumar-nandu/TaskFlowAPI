# TaskFlow API

[![TaskFlow API CI](https://github.com/nandakumar-nandu/TaskFlowAPI/actions/workflows/ci.yml/badge.svg)](https://github.com/nandakumar-nandu/TaskFlowAPI/actions/workflows/ci.yml)

TaskFlow API is a production-ready, high-performance, asynchronous REST API built with Python, FastAPI, and PostgreSQL. It is designed to serve as a robust task management platform with built-in JWT authentication, task filtering, sorting, pagination, and database migrations.

## Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.111.0-teal?style=for-the-badge&logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-v0.30.1-purple?style=for-the-badge&logo=uvicorn&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-v2.0.31-red?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-v15%2B-blue?style=for-the-badge&logo=postgresql&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-v1.13.2-orange?style=for-the-badge)
![Pydantic](https://img.shields.io/badge/Pydantic-v2.9.0-red?style=for-the-badge&logo=pydantic&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-v9.1.1-green?style=for-the-badge&logo=pytest&logoColor=white)

</div>

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

---

## Running Tests

TaskFlow API uses **pytest** and **pytest-cov** to validate application code and measure test coverage.

### 🧪 Run the Test Suite
To execute the entire integration and unit test suite, run:
```bash
# Windows PowerShell
.venv\Scripts\pytest

# Linux/macOS
.venv/bin/pytest
```

### 📊 Run Tests with Coverage Report
To run all tests and generate a coverage summary table directly in the terminal, run:
```bash
# Windows PowerShell
.venv\Scripts\pytest --cov=app tests/

# Linux/macOS
.venv/bin/pytest --cov=app tests/
```

### 🏷️ Generating a Coverage Badge
To generate a dynamic coverage badge image (`coverage.svg`), you can use the `coverage-badge` CLI:
1. Install `coverage-badge`:
   ```bash
   .venv\Scripts\pip install coverage-badge
   ```
2. Generate the badge SVG file:
   ```bash
   .venv\Scripts\coverage-badge -o coverage.svg
   ```
This reads the latest `.coverage` file in the project root and outputs an SVG badge representing the coverage percentage (e.g., `91%`).

---

## Docker Setup

TaskFlow API is fully containerized using **Docker** and **Docker Compose**, providing a consistent local environment for development and production deployments.

### 🐳 Services Configured
- **`api`**: The FastAPI application server (port `8000`).
- **`db`**: A PostgreSQL 15 database instance (port `5432`).
- **`pgadmin`**: A web-based PostgreSQL administration interface (port `5050`).

### 🚀 Running the Containers
To build the application image and launch all services in the background, run:
```bash
docker-compose up --build -d
```

Once execution completes:
- **FastAPI Endpoints**: Access the API server at [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Documentation**: Open [http://localhost:8000/docs](http://localhost:8000/docs)
- **pgAdmin Console**: Login to the database administrator panel at [http://localhost:5050](http://localhost:5050) using:
  - **Email**: `admin@taskflow.local`
  - **Password**: `admin_secure_pwd`

To stop and remove active containers and network settings, run:
```bash
docker-compose down
```

To stop containers and wipe persistent PostgreSQL database volumes, run:
```bash
docker-compose down -v
```

---

## Interactive Swagger API Documentation

FastAPI automatically parses endpoint routing, models schemas, and security scopes to render an interactive Swagger UI dashboard. 

You can view response schemas, parameter configurations, and trigger requests directly from the browser:

![Swagger UI Mockup Screenshot](docs/assets/swagger_ui_mockup.png)
