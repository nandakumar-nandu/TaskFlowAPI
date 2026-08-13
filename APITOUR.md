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
        U1["GET /users/me"]
        U2["PATCH /users/me"]
        U3["POST /users/me/avatar"]
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

    subgraph Comments (Implemented)
        CO1["GET /tasks/{task_id}/comments"]
        CO2["POST /tasks/{task_id}/comments"]
        CO3["PATCH /tasks/{task_id}/comments/{comment_id}"]
        CO4["DELETE /tasks/{task_id}/comments/{comment_id}"]
    end

    subgraph System Utility
        H1["GET /health"]
    end
```

---

## API Route Reference

### 1. Authentication Endpoints

Welcome to the Authentication section! These endpoints act as the front door to our API. Before a user can do anything else, they need an account. They can create one using the Register endpoint, and then sign in using the Login endpoint to receive a "key" (a JWT token). This key must be sent with all future requests to prove who they are.

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

### 2. User Profile Endpoints

The User Profile section handles personal account settings. Once a user is logged in, they can use these endpoints to view their own profile details, update their display name, or upload a custom avatar image. Because these actions are sensitive, the API strictly ensures that a user can only ever view or modify their own profile.

All endpoints below require authentication via a valid JWT bearer token.

#### `GET /users/me`
- **Goal**: Fetch current authenticated user's profile details.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK`
  ```json
  {
    "id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "avatar_url": "/media/avatars/7b0a88bf-97cc-44a3-ad6c-9411649b8032.png",
    "created_at": "2026-07-15T17:23:00Z"
  }
  ```

#### `PATCH /users/me`
- **Goal**: Partially update the current user's profile fields. Only submitted fields will be modified.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "full_name": "Johnathan Doe"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "email": "user@example.com",
    "full_name": "Johnathan Doe",
    "is_active": true,
    "avatar_url": "/media/avatars/7b0a88bf-97cc-44a3-ad6c-9411649b8032.png",
    "created_at": "2026-07-15T17:23:00Z"
  }
  ```

#### `POST /users/me/avatar`
- **Goal**: Upload an image to serve as the user's avatar.
- **Headers**: `Authorization: Bearer <token>`, `Content-Type: multipart/form-data`
- **Payload**: Form data with key `file` containing the binary image file.
- **Validation Rules**:
  - Max upload size is **5 MB**. Files exceeding this size will return an `HTTP 413 Payload Too Large`.
  - Accepted MIME types are: `image/jpeg`, `image/png`, and `image/webp`. Other types return an `HTTP 415 Unsupported Media Type`.
- **Response**: `200 OK`
  ```json
  {
    "id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "email": "user@example.com",
    "full_name": "Johnathan Doe",
    "is_active": true,
    "avatar_url": "/media/avatars/7b0a88bf-97cc-44a3-ad6c-9411649b8032.png",
    "created_at": "2026-07-15T17:23:00Z"
  }
  ```
- **Error Responses**:
  - `413 Payload Too Large`:
    ```json
    {
      "detail": "Payload too large. Maximum allowed size is 5 MB."
    }
    ```
  - `415 Unsupported Media Type`:
    ```json
    {
      "detail": "Unsupported media type. Only image/jpeg, image/png, and image/webp are accepted."
    }
    ```

---

### 3. Task Management (Implemented)

The Task Management section is the core of our application! Here, users can create new tasks, update their progress, or delete them when they're no longer needed. The API includes robust filters so users can easily sort through hundreds of tasks to find exactly what they're looking for. It also automatically tracks any changes made to a task in a detailed activity log.

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

#### `GET /tasks/{task_id}/activity`
- **Goal**: Fetch the append-only activity audit trail for a task (ordered newest first).
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `limit`: Capped integer between 1 and 200 (default `50`).
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "e8c901e9-8967-43cd-ad1c-82b3cf1fg499",
      "task_id": "f5c901e9-8967-43cd-ad1c-82b3cf1fg4b1",
      "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
      "action": "task.updated",
      "diff": {
        "status": {
          "before": "todo",
          "after": "in_progress"
        }
      },
      "occurred_at": "2026-07-25T12:00:00Z"
    },
    {
      "id": "a1c901e9-8967-43cd-ad1c-82b3cf1fg411",
      "task_id": "f5c901e9-8967-43cd-ad1c-82b3cf1fg4b1",
      "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
      "action": "task.created",
      "diff": null,
      "occurred_at": "2026-07-25T11:50:00Z"
    }
  ]
  ```
- **Error Responses**:
  - `404 Not Found`: Task not found.
  - `403 Forbidden`: User does not own the task.

---

### 4. Category Management (Implemented)

To help keep things organized, the Category Management section allows users to group their tasks into custom folders or "categories" (like "Work", "Personal", or "Shopping"). Users have full control to create, rename, or delete these categories as their needs change.

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

### 5. Task Comments Endpoints

The Task Comments section adds a layer of collaboration and note-taking. Users can leave comments on tasks to document progress or share thoughts. For security, the API guarantees that only the original author of a comment is allowed to edit or delete it.

All endpoints below require authentication via a valid JWT bearer token.

#### `GET /tasks/{task_id}/comments`
- **Goal**: Retrieve all comments associated with the specified task in `created_at` ascending order.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "1c0a88bf-97cc-44a3-ad6c-9411649b8090",
      "task_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
      "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
      "body": "First comment on this task.",
      "created_at": "2026-07-25T11:55:00Z",
      "updated_at": null
    }
  ]
  ```
- **Error Codes**:
  - `404 Not Found`: Task not found.
  - `403 Forbidden`: Task belongs to another user.

#### `POST /tasks/{task_id}/comments`
- **Goal**: Create a new comment on the specified task.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "body": "This is a new task comment."
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": "1c0a88bf-97cc-44a3-ad6c-9411649b8090",
    "task_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "body": "This is a new task comment.",
    "created_at": "2026-07-25T11:55:00Z",
    "updated_at": null
  }
  ```
- **Error Codes**:
  - `400 Bad Request`: Body validation fails (e.g. empty comment).
  - `404 Not Found`: Task not found.
  - `403 Forbidden`: Task belongs to another user.

#### `PATCH /tasks/{task_id}/comments/{comment_id}`
- **Goal**: Update the body text of an existing comment.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "body": "This is the updated comment text."
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "id": "1c0a88bf-97cc-44a3-ad6c-9411649b8090",
    "task_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "user_id": "7b0a88bf-97cc-44a3-ad6c-9411649b8032",
    "body": "This is the updated comment text.",
    "created_at": "2026-07-25T11:55:00Z",
    "updated_at": "2026-07-25T11:58:00Z"
  }
  ```
- **Error Codes**:
  - `404 Not Found`: Comment not found.
  - `403 Forbidden`: Comment belongs to another user (only the author can edit it).

#### `DELETE /tasks/{task_id}/comments/{comment_id}`
- **Goal**: Delete an existing comment.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `204 No Content`
- **Error Codes**:
  - `404 Not Found`: Comment not found.
  - `403 Forbidden`: Comment belongs to another user (only the author can delete it).

---

### 6. Health Check

The Health Check endpoint is a simple diagnostic tool. Systems and administrators use it to quickly verify that the API is running smoothly and that it can successfully communicate with the database. If something is broken, this endpoint will tell us!

#### `GET /health`
- **Goal**: Perform immediate service connectivity diagnostics.
- **Response**:
  ```json
  {
    "status": "ok",
    "database": "connected"
  }
  ```

