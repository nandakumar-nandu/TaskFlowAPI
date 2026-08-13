# Changelog

All notable changes to the TaskFlow API project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-07-25 12:00:00 +05:30

### Added
- **Migration Note:** Run `alembic upgrade head` to create the task_activity table for audit logging.
- Append-only `TaskActivity` database model in `app/models/activity.py`.
- Alembic database migration script `022fb9df4f9b` creating `task_activity` table.
- Pydantic response schema `ActivityRead` in `app/schemas/activity.py`.
- Atomic transaction audit trail logging functions in `app/services/activity_service.py`.
- Integrated atomic logging into task creation, modification, and deletion in `app/services/task_service.py`.
- Protected activity route `GET /tasks/{task_id}/activity` in `app/routes/tasks.py`.
- Integration tests for activity audit trail in `tests/test_activity.py`.

## [1.2.0] - 2026-07-25 11:55:00 +05:30

### Added
- **Migration Note:** Run `alembic upgrade head` to create the comments table.
- SQLAlchemy Comment model mapping comments to parent tasks and user authors.
- Alembic database migration script `7d5c9cfcd93c` to create the `comments` table.
- Comment Pydantic schemas (`CommentCreate`, `CommentUpdate`, `CommentRead`).
- Task comments business services with strict ownership and authorship checks.
- Protected nested routes `/tasks/{task_id}/comments` mapping comment CRUD operations.
- Four integration test cases validating comment operations in `tests/test_comments.py`.

## [1.1.0] - 2026-07-25 11:48:00 +05:30

### Added
- **Migration Note:** Run `alembic upgrade head` to add avatar_url column to users table.
- User profile management endpoints `GET /users/me` and `PATCH /users/me`.
- Avatar image multipart/form-data upload endpoint `POST /users/me/avatar`.
- Custom ASGI `UploadSizeLimitMiddleware` restricting requests to a maximum of 5MB.
- SQLAlchemy database model column `avatar_url` inside `app/models/user.py`.
- Alembic database migration script `5bfa399b5973` to update the `users` table schema.
- Comprehensive integration tests in `tests/test_users.py`.

## [1.0.0] - 2026-07-18 09:05:00 +05:30

### Added
- IP-based rate limiting security middleware using `slowapi` library, defaulting to 100 requests per minute with client bypasses configured during unit testing.
- Platform descriptor file `Procfile` configured to launch uvicorn processes on cloud hosting services like Railway.
- Extensively documented environment configuration references in `.env.example`.
- Completed all architecture Mermaid diagrams, API references, Docker Quickstarts, and cloud deployment guides inside `README.md` and walkthroughs.

## [0.6.0] - 2026-07-18 09:00:00 +05:30

### Added
- Multi-container virtualization with `Dockerfile` and `docker-compose.yml` orchestrating API (FastAPI), Database (PostgreSQL), and PGAdmin GUI admin tools.
- Detailed plain-English execution instructions inside Dockerfile and Compose YAML attributes.
- Continuous Integration workflow configuration in `.github/workflows/ci.yml` running pytest suites on pushes and pull requests to `main`.
- Enhanced OpenAPI documentation schema definitions containing field validation examples and detailed endpoint descriptions for Swagger UI.

## [0.5.0] - 2026-07-18 08:55:00 +05:30

### Added
- pytest configuration in `pytest.ini` with `asyncio_mode = auto` setting.
- Global testing fixtures inside `tests/conftest.py` covering mock database session context, async http client, auth user template, and JWT authorization headers.
- Comprehensive integration tests in `tests/test_auth.py` for successful registrations, login failures, credential checks, and unauthorized accesses.
- Dynamic task querying and relationship assertions in `tests/test_tasks.py` for task updates, status filters, paging, and cross-user authorization controls.
- Code coverage reporting configured via `pytest-cov` resulting in 91% code coverage.

## [0.4.0] - 2026-07-18 08:45:00 +05:30

### Added
- **Migration Note:** Run `alembic upgrade head` to create categories, tags, and task_tags tables.
- Database models for `Category` (`app/models/category.py`) and `Tag` (`app/models/tag.py`) with user ownership and comments.
- Junction table `task_tags` establishing a many-to-many relationship between tasks and tags.
- Alembic database migration file `7ae8a893652f` to create the new tables, add `category_id` FK column to `tasks`, and provision optimized query indexes.
- Database indexes on `tasks` table columns (`user_id`, `status`, `priority`, `category_id`, `due_date`) for query performance optimization.
- Category CRUD service methods and endpoint routes in `/categories`.
- Advanced task filtering (by `category_id` and `tag`), dynamic sorting (`due_date`, `created_at`, etc.), and pagination (`page`, `limit`) inside `GET /tasks`.
- Automatic tag resolve & association in `POST /tasks` and `PUT /tasks/{id}` based on tag names.
- Integration tests in `tests/test_categories.py` and `tests/test_tasks.py` to cover all Commit 4 functionality.

## [0.3.0] - 2026-07-15 17:30:00 +05:30

### Added
- **Migration Note:** Run `alembic upgrade head` to create the tasks table.
- SQLAlchemy Task database model in `app/models/task.py` with custom enums and foreign key mappings.
- Alembic database migration script for creating the `tasks` table.
- Pydantic Task validation schemas in `app/schemas/task.py` (TaskCreate, TaskRead, TaskUpdate, TaskListResponse).
- Business logic service layer in `app/services/task_service.py` incorporating strict task ownership checks.
- Task CRUD API router endpoints in `app/routes/tasks.py` (GET /tasks, POST /tasks, GET /tasks/{id}, PUT /tasks/{id}, DELETE /tasks/{id}) protected by JWT authorization.
- Automated integration test suites inside `tests/test_tasks.py`.

## [0.2.0] - 2026-07-15 17:23:00 +05:30

### Added
- **Migration Note:** Run `alembic upgrade head` to create the users table.
- SQLAlchemy User database model in `app/models/user.py`.
- Alembic database migration script for creating the `users` table.
- Pydantic User validation schemas in `app/schemas/user.py` (UserCreate, UserRead, UserUpdate, Token, UserLogin).
- Cryptographic utility functions in `app/core/security.py` using `bcrypt` and `pyjwt`.
- User authentication router endpoints in `app/routes/auth.py` (POST /auth/register, POST /auth/login, GET /auth/me).
- Comprehensive mock-based integration tests in `tests/test_auth.py`.

## [0.1.0] - 2026-07-14 14:00:00 +05:30

### Added
- Initial project scaffolding for FastAPI application.
- Asynchronous database engine setup using SQLAlchemy and asyncpg.
- Async `/health` check route checking database connectivity.
- Core configuration model using `pydantic-settings`.
- Stubs for models, schemas, services, routes, and custom middlewares.
- Draft documentation (README, CHANGELOG, WALKTHROUGH, APITOUR).
