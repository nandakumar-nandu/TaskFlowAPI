# API Tour - TaskFlow API Endpoints

This document maps out the endpoint routes and payload schemas planned and built for the TaskFlow API.

---

## Endpoint Map

```mermaid
graph LR
    subgraph Authentication & Profile
        A1["POST /auth/register"]
        A2["POST /auth/login"]
        A3["GET /auth/me"]
    end

    subgraph User Settings (Planned)
        U2["PUT /api/v1/users/me"]
    end

    subgraph Task Management (Planned)
        T1["GET /api/v1/tasks"]
        T2["POST /api/v1/tasks"]
        T3["GET /api/v1/tasks/{id}"]
        T4["PUT /api/v1/tasks/{id}"]
        T5["DELETE /api/v1/tasks/{id}"]
    end

    subgraph System Utility
        H1["GET /health"]
    end
```

---

## API Route Reference

### 1. Authentication Endpoints

#### `POST /auth/register`
- **Goal**: Register a new user in the database.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword123",
    "full_name": "John Doe"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2026-07-15T17:23:00.123456Z"
  }
  ```

#### `POST /auth/login`
- **Goal**: Verify user credentials and issue an authentication JWT access token.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword123"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3YjBhODhiZi05N2NjLTQ0YTMtYWQ2Yy05NDExNjQ5YjgwMzIiLCJleHAiOjE3ODUwMzAzMDZ9...",
    "token_type": "bearer"
  }
  ```

#### `GET /auth/me`
- **Goal**: Fetch current authenticated user's profile details.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK`
  ```json
  {
    "id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2026-07-15T17:23:00.123456Z"
  }
  ```

---

### 2. User Settings (Planned)

#### `PUT /api/v1/users/me`
- **Goal**: Update profile details of the current authenticated user.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK` with updated user details.

---

### 3. Task Management (Planned)

#### `GET /api/v1/tasks`
- **Goal**: Retrieve list of tasks owned by the authenticated user.
- **Query Params**: `status` (completed/pending), `skip` (pagination offset), `limit` (pagination page size).
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK` with list of task objects.

#### `POST /api/v1/tasks`
- **Goal**: Create a new task.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "title": "Build scaffold",
    "description": "Initialize repository structure",
    "due_date": "2026-07-20T12:00:00Z"
  }
  ```
- **Response**: `201 Created` with the newly created task.

#### `GET /api/v1/tasks/{id}`
- **Goal**: Fetch a single task by ID.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK` with task details.

#### `PUT /api/v1/tasks/{id}`
- **Goal**: Update details or change status of a specific task.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK` with updated task details.

#### `DELETE /api/v1/tasks/{id}`
- **Goal**: Delete a task.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `204 No Content`.

---

### 4. Health Check

#### `GET /health`
- **Goal**: Perform immediate service connectivity diagnostics.
- **Response**:
  ```json
  {
    "status": "ok",
    "database": "connected"
  }
  ```
