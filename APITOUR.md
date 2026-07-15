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

### 3. Task Management (Implemented)

#### `GET /tasks`
- **Goal**: Retrieve a list of tasks owned by the authenticated user with optional filtering by status/priority and pagination support.
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `status`: `todo`, `in_progress`, `done` (optional)
  - `priority`: `low`, `medium`, `high` (optional)
  - `skip`: pagination offset integer, defaults to `0` (optional)
  - `limit`: pagination record limit, defaults to `10` (optional)
- **Response**: `200 OK`
  ```json
  {
    "tasks": [
      {
        "id": "e4b901d8-7956-42bc-9d0b-71a2be0ef3a0",
        "title": "Build scaffold",
        "description": "Initialize repository structure",
        "status": "todo",
        "priority": "medium",
        "due_date": "2026-07-20T12:00:00Z",
        "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
        "created_at": "2026-07-15T17:23:00Z"
      }
    ],
    "total_count": 1,
    "limit": 10,
    "offset": 0,
    "pages": 1
  }
  ```

#### `POST /tasks`
- **Goal**: Create a new task.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "title": "Implement database",
    "description": "Configure models and migrations",
    "status": "todo",
    "priority": "high",
    "due_date": "2026-07-22T18:00:00Z"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": "f5c901e9-8967-43cd-ad1c-82b3cf1fg4b1",
    "title": "Implement database",
    "description": "Configure models and migrations",
    "status": "todo",
    "priority": "high",
    "due_date": "2026-07-22T18:00:00Z",
    "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "created_at": "2026-07-15T17:30:00Z"
  }
  ```

#### `GET /tasks/{id}`
- **Goal**: Fetch details of a single task by ID.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK`
  ```json
  {
    "id": "f5c901e9-8967-43cd-ad1c-82b3cf1fg4b1",
    "title": "Implement database",
    "description": "Configure models and migrations",
    "status": "todo",
    "priority": "high",
    "due_date": "2026-07-22T18:00:00Z",
    "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "created_at": "2026-07-15T17:30:00Z"
  }
  ```

#### `PUT /tasks/{id}`
- **Goal**: Update details or status of a specific task.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "status": "in_progress",
    "priority": "medium"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "id": "f5c901e9-8967-43cd-ad1c-82b3cf1fg4b1",
    "title": "Implement database",
    "description": "Configure models and migrations",
    "status": "in_progress",
    "priority": "medium",
    "due_date": "2026-07-22T18:00:00Z",
    "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "created_at": "2026-07-15T17:30:00Z"
  }
  ```

#### `DELETE /tasks/{id}`
- **Goal**: Delete a task by ID.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `204 No Content`

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
