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

    subgraph Task Management (Implemented)
        T1["GET /tasks"]
        T2["POST /tasks"]
        T3["GET /tasks/{id}"]
        T4["PUT /tasks/{id}"]
        T5["DELETE /tasks/{id}"]
    end

    subgraph Category Management (Implemented)
        C1["GET /categories"]
        C2["POST /categories"]
        C3["GET /categories/{id}"]
        C4["PUT /categories/{id}"]
        C5["DELETE /categories/{id}"]
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
- **Goal**: Retrieve a list of tasks owned by the authenticated user with optional filtering by status/priority/category/tag, sorting, and pagination support.
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `status`: `todo`, `in_progress`, `done` (optional)
  - `priority`: `low`, `medium`, `high` (optional)
  - `category_id`: Category UUID filter (optional)
  - `tag`: Tag name string filter, e.g. `work` (optional)
  - `page`: Page index number starting at 1, defaults to `1` (optional)
  - `limit`: Page records limit, defaults to `10` (optional)
  - `sort`: Column name to sort by, defaults to `created_at` (optional)
  - `order`: Sort direction: `asc` or `desc`, defaults to `desc` (optional)
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
        "category_id": "8a0a88bf-97cc-44a3-ad6c-9411649b8054",
        "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
        "created_at": "2026-07-15T17:23:00Z",
        "tags": [
          {
            "id": "c1a901e9-8967-43cd-ad1c-82b3cf1fg401",
            "name": "work",
            "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
            "created_at": "2026-07-15T17:25:00Z"
          }
        ]
      }
    ],
    "total_count": 1,
    "limit": 10,
    "offset": 0,
    "pages": 1
  }
  ```

#### `POST /tasks`
- **Goal**: Create a new task (with optional category mapping and inline tags creation).
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "title": "Implement database",
    "description": "Configure models and migrations",
    "status": "todo",
    "priority": "high",
    "due_date": "2026-07-22T18:00:00Z",
    "category_id": "8a0a88bf-97cc-44a3-ad6c-9411649b8054",
    "tags": ["work", "important"]
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
    "category_id": "8a0a88bf-97cc-44a3-ad6c-9411649b8054",
    "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "created_at": "2026-07-15T17:30:00Z",
    "tags": [
      {
        "id": "c1a901e9-8967-43cd-ad1c-82b3cf1fg401",
        "name": "work",
        "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
        "created_at": "2026-07-15T17:25:00Z"
      },
      {
        "id": "c2a901e9-8967-43cd-ad1c-82b3cf1fg402",
        "name": "important",
        "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
        "created_at": "2026-07-15T17:30:00Z"
      }
    ]
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
    "category_id": "8a0a88bf-97cc-44a3-ad6c-9411649b8054",
    "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "created_at": "2026-07-15T17:30:00Z",
    "tags": [
      {
        "id": "c1a901e9-8967-43cd-ad1c-82b3cf1fg401",
        "name": "work",
        "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
        "created_at": "2026-07-15T17:25:00Z"
      }
    ]
  }
  ```

#### `PUT /tasks/{id}`
- **Goal**: Update details, status, category, or tags of a specific task.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "status": "in_progress",
    "priority": "medium",
    "tags": ["work"]
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
    "category_id": "8a0a88bf-97cc-44a3-ad6c-9411649b8054",
    "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "created_at": "2026-07-15T17:30:00Z",
    "tags": [
      {
        "id": "c1a901e9-8967-43cd-ad1c-82b3cf1fg401",
        "name": "work",
        "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
        "created_at": "2026-07-15T17:25:00Z"
      }
    ]
  }
  ```

#### `DELETE /tasks/{id}`
- **Goal**: Delete a task by ID.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `204 No Content`

---

### 4. Category Management (Implemented)

#### `GET /categories`
- **Goal**: Retrieve a list of all categories owned by the authenticated user.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "8a0a88bf-97cc-44a3-ad6c-9411649b8054",
      "name": "Work Tasks",
      "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
      "created_at": "2026-07-15T17:23:00Z"
    }
  ]
  ```

#### `POST /categories`
- **Goal**: Create a new category.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "name": "Personal Tasks"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": "9a0b88bf-97cc-44a3-ad6c-9411649b8055",
    "name": "Personal Tasks",
    "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "created_at": "2026-07-15T17:35:00Z"
  }
  ```

#### `GET /categories/{id}`
- **Goal**: Retrieve details of a specific category by ID.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK`
  ```json
  {
    "id": "8a0a88bf-97cc-44a3-ad6c-9411649b8054",
    "name": "Work Tasks",
    "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "created_at": "2026-07-15T17:23:00Z"
  }
  ```

#### `PUT /categories/{id}`
- **Goal**: Update details of a specific category.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "name": "Office Tasks"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "id": "8a0a88bf-97cc-44a3-ad6c-9411649b8054",
    "name": "Office Tasks",
    "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "created_at": "2026-07-15T17:23:00Z"
  }
  ```

#### `DELETE /categories/{id}`
- **Goal**: Delete a category.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `204 No Content`

---

### 5. Health Check

#### `GET /health`
- **Goal**: Perform immediate service connectivity diagnostics.
- **Response**:
  ```json
  {
    "status": "ok",
    "database": "connected"
  }
  ```

