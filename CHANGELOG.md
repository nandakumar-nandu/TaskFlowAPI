# Changelog

All notable changes to the TaskFlow API project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-07-15 17:30:00 +05:30

### Added
- SQLAlchemy Task database model in `app/models/task.py` with custom enums and foreign key mappings.
- Alembic database migration script for creating the `tasks` table.
- Pydantic Task validation schemas in `app/schemas/task.py` (TaskCreate, TaskRead, TaskUpdate, TaskListResponse).
- Business logic service layer in `app/services/task_service.py` incorporating strict task ownership checks.
- Task CRUD API router endpoints in `app/routes/tasks.py` (GET /tasks, POST /tasks, GET /tasks/{id}, PUT /tasks/{id}, DELETE /tasks/{id}) protected by JWT authorization.
- Automated integration test suites inside `tests/test_tasks.py`.

## [0.2.0] - 2026-07-15 17:23:00 +05:30

### Added
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
