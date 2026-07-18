# Walkthrough - TaskFlow API Flow

TaskFlow API is built to help teams and developers easily orchestrate, manage, and audit their day-to-day work tasks. This document details the high-level workflow, authentication strategies, and data retrieval structures.

## API Overview & Use Cases

TaskFlow API provides core functionality to:
- **Register & Authenticate Users**: Secure password storage and session verification via JWT.
- **Manage Task Lifecycles**: Create, edit, assign, complete, and delete tasks.
- **Filter and Search**: Query tasks based on complete status, priority, and date limits.

---

## Authentication Flow

> [!NOTE]
> Authentication is fully implemented in Commit 2. It utilizes JSON Web Tokens (JWT) inside HTTP Authorization headers (`Authorization: Bearer <token>`).

The authorization pipeline operates as follows:
- **Password Encryption**: Uses the `bcrypt` library to securely hash and verify passwords during user registration and login, ensuring hashes are salted and resistant to timing and brute-force attacks.
- **Token Generation**: Uses the `pyjwt` library to sign JSON Web Tokens with a secure `HS256` HMAC algorithm using the application's `SECRET_KEY`.
- **Route Guarding**: FastAPI security dependency `HTTPBearer` extracts and decodes the token from the request header, loading the current user context directly into guarded endpoints.

---

## Planned User and Data Workflow

The diagram below outlines the full authentication and data-fetching flow that will be built:

```mermaid
sequenceDiagram
    autonumber
    actor User as Client Application
    participant API as TaskFlow FastAPI App
    participant DB as PostgreSQL Database

    Note over User, API: Authentication Flow
    User->>API: POST /auth/register (username, password, email)
    API->>DB: Create user with hashed password
    DB-->>API: Confirm user created
    API-->>User: User metadata response

    User->>API: POST /auth/login (username, password)
    API->>API: Verify password hash
    API-->>User: Return JWT Access Token

    Note over User, API: Data Access Flow
    User->>API: GET /tasks (Authorization: Bearer <token>)
    API->>API: Decode and validate JWT
    API->>DB: Fetch tasks for decoded User ID
    DB-->>API: Query results
    API-->>User: Array of user tasks
```

---

## Testing

TaskFlow API employs a comprehensive integration testing framework built on **pytest** to ensure functional correctness, data security, and API reliability:

- **pytest-asyncio Integration**: As a fully asynchronous API, our test suite runs test cases asynchronously to match uvicorn/asyncpg execution patterns.
- **Dependency Overrides**: The tests dynamically override database dependencies (`get_db`) with transactional `AsyncMock(spec=AsyncSession)` sessions. This permits mocking complex database execution queries, return scalars, and model refreshes, avoiding database lockups and network roundtrips.
- **Shared Fixtures Configuration**: We consolidate testing setups inside [conftest.py](file:///d:/projects/TaskFlowAPI/tests/conftest.py), which exposes standard fixtures:
  - `db`: Isolates mock session instances per test run.
  - `client`: Initializes asynchronous ASGI clients to communicate with FastAPI endpoints.
  - `auth_user` & `auth_headers`: Provisions pre-configured authenticated contexts.
- **Coverage Reports**: Configured with `pytest-cov` to monitor testing coverage, ensuring critical routes, schemas, and services are covered by at least 80% coverage (attaining 91% total coverage).

