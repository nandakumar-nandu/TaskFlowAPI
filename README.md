# TaskFlow API

[![TaskFlow API CI](https://github.com/nandakumar-nandu/TaskFlowAPI/actions/workflows/ci.yml/badge.svg)](https://github.com/nandakumar-nandu/TaskFlowAPI/actions/workflows/ci.yml)

## Overview — What Is TaskFlowAPI?

TaskFlowAPI is a backend application that works like the brain behind a to-do list or project management app. It handles the core logic: letting users create accounts, securely log in, and manage their daily tasks. It securely stores all this data in a database and provides a standardized set of rules (the API) that a website or mobile app can follow to interact with it.

---

## Feature List

- **🔑 Secure Authentication**: Users can register and log in securely. Passwords are mathematically hashed, and login sessions are protected by JSON Web Tokens (JWT).
- **📝 Task Management**: Create, read, update, and delete tasks with ease.
- **📁 Categorization**: Group tasks into distinct categories (like "Work" or "Personal") to keep things organized.
- **🏷️ Tagging System**: Assign multiple labels to a task (like "urgent" or "feature") to help with filtering.
- **🔎 Advanced Filtering & Sorting**: Easily search through hundreds of tasks by status, priority, or category, and sort them by due date or creation time.
- **📄 Pagination**: The API returns tasks in pages (like 10 at a time) to keep the app fast and save bandwidth.
- **💬 Task Comments**: Collaborate with others or leave notes for yourself by commenting directly on specific tasks.
- **📜 Activity Audit Trail**: Every time a task is created, updated, or deleted, the API secretly logs it. This creates a transparent history of who changed what and when.
- **👤 User Profiles**: Users can update their display names and manage their accounts.
- **🖼️ Avatar Uploads**: Users can upload profile pictures, and the API automatically limits file sizes to prevent abuse.
- **🛡️ Rate Limiting**: The system automatically blocks users or bots that send too many requests too quickly (DDoS protection).
- **✅ Automated Testing**: Over 90% of the codebase is covered by automated robots (tests) that run every time code is changed to make sure nothing breaks.

---

## System Architecture

TaskFlowAPI is built using a modern separation of concerns. Here is how the pieces fit together:

1. **Client**: A browser or mobile app sends an HTTP request (like "get my tasks").
2. **API (FastAPI)**: The web server receives the request, checks the user's ID card (JWT token), and asks the Service Layer to do the work.
3. **Database (PostgreSQL)**: The Service Layer talks to the PostgreSQL database to safely retrieve or update the user's data.
4. **pgAdmin**: An optional web dashboard for developers to manually look inside the database.

```text
+-------------------+        HTTP        +--------------------+
|                   |  <-------------->  |                    |
|  Client / Browser |                    |  FastAPI (Backend) |
|                   |                    |                    |
+-------------------+                    +---------+----------+
                                                   |
                                            async database
                                              connection
                                                   |
+-------------------+                    +---------v----------+
|                   |  admin dashboard   |                    |
|      pgAdmin      |  <-------------->  | PostgreSQL (DB)    |
|                   |                    |                    |
+-------------------+                    +--------------------+
```

---

## Getting Started — Setup & Installation

If you want to run this API on your own computer, follow these simple steps!

1. **Clone the Repository**
   Download the code to your computer:
   ```bash
   git clone https://github.com/nandakumar-nandu/TaskFlowAPI.git
   cd TaskFlowAPI
   ```

2. **Configure Environment Variables**
   The application needs some secret passwords and configurations to run. We provide a template file for you:
   - Copy `.env.example` and rename it to `.env`.
   - You can leave the default values inside for local testing!

3. **Start Docker**
   Make sure you have Docker installed. We use Docker to automatically download and run the database and the API without you having to install them manually.
   ```bash
   docker-compose up --build -d
   ```

4. **Run Database Migrations**
   Now we need to tell the database to create all the empty tables (like `users` and `tasks`).
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. **Access the API!**
   You are all set! Open your web browser and go to [http://localhost:8000/docs](http://localhost:8000/docs). This is a beautiful, interactive dashboard where you can click buttons to test the API directly!

---

## Navigating the Codebase

Here is a map of the project to help you find your way around. We recommend reading them in the order listed below!

| Directory/File | Purpose |
| :--- | :--- |
| `app/models/` | **Start Here:** Defines what the database tables look like (e.g., a Task has a title and a due date). |
| `app/schemas/` | Defines the exact JSON format the API expects to receive and send back. |
| `app/routes/` | The "doorways" of the API. This is where URLs like `/tasks` are defined. |
| `app/services/` | The "brains" of the API. This contains the business logic (e.g., making sure a user can't delete someone else's task). |
| `app/core/` | Foundational settings, database connections, and security/password tools. |
| `app/main.py` | The main engine that starts the FastAPI server and plugs everything together. |
| `alembic/` | Contains the instructions for upgrading or changing the database schema over time. |
| `tests/` | Contains all the automated test scripts that verify the code works correctly. |

---

## How to Run & Test the Project

### Running the App
The easiest way to run the app is using **Docker Compose** (as shown in the Setup instructions). It starts the API, the database, and the pgAdmin dashboard all at once.

If you prefer to run it manually using Python:
1. Activate your virtual environment.
2. Run `uvicorn app.main:app --reload`.

### Running Tests
We use a tool called `pytest` to run our automated tests. These tests create a fake database and simulate a user logging in and clicking around to make sure the app responds correctly.

To run the tests and see how much of the code is covered:
```bash
pytest --cov=app tests/
```

---

## 📘 Tutorial: Your First 10 Minutes with TaskFlowAPI
*This is a condensed version of the full [WALKTHROUGH.md](file:///d:/Projects_Portfolio/TaskFlowAPI/WALKTHROUGH.md) guide.*

### Step 1: Register
- **Endpoint**: `POST /auth/register`
- **Request Payload**: `{"email": "user@example.com", "password": "securepassword", "full_name": "Test User"}`
- **Behind the Scenes**: The API receives the payload, hashes the password using `bcrypt`, creates a new `User` model, and commits it to the database.
- **Expected Response**: `201 Created` with the new user's metadata (excluding the password).

### Step 2: Login
- **Endpoint**: `POST /auth/login`
- **Request Payload**: `{"username": "user@example.com", "password": "securepassword"}`
- **Behind the Scenes**: The API fetches the user by email, verifies the password against the stored hash, and generates a JWT (JSON Web Token) signed with a secret key.
- **Expected Response**: `200 OK` with the `access_token` and `token_type` ("bearer").

### Step 3: Create Category
- **Endpoint**: `POST /categories`
- **Request Payload**: `{"name": "Work Projects"}` (Requires `Authorization: Bearer <token>` header)
- **Behind the Scenes**: The API decodes the JWT to find the user's ID. It then creates a new `Category` model linked to that user and saves it to the database.
- **Expected Response**: `201 Created` with the new category details (including its UUID).

### Step 4: Create Task with Tags
- **Endpoint**: `POST /tasks`
- **Request Payload**: `{"title": "Finish Report", "description": "Q3 Sales", "status": "todo", "priority": "high", "category_id": "<uuid-from-step-3>", "tags": ["urgent", "sales"]}`
- **Behind the Scenes**: The API validates the category belongs to the user. It creates the `Task`, finds or creates the requested `Tag`s, links them in the `task_tags` junction table, and creates a `TaskActivity` log entry recording the creation.
- **Expected Response**: `201 Created` with the task details, nested category, and array of tags.

### Step 5: Fetch Task List
- **Endpoint**: `GET /tasks?status=todo&priority=high`
- **Request Payload**: None (Query parameters used instead)
- **Behind the Scenes**: The API queries the database for tasks belonging to the user, applying the filters provided. It supports pagination and dynamic sorting.
- **Expected Response**: `200 OK` with a paginated array of tasks.

### Step 6: Add Comment
- **Endpoint**: `POST /tasks/<task-uuid>/comments`
- **Request Payload**: `{"body": "I need to ask Sarah for the Q3 numbers."}`
- **Behind the Scenes**: The API verifies the task belongs to the user, then creates a new `Comment` linked to the task and the user.
- **Expected Response**: `201 Created` with the comment details.

### Step 7: View Activity Log
- **Endpoint**: `GET /tasks/<task-uuid>/activity`
- **Request Payload**: None
- **Behind the Scenes**: The API queries the `task_activity` table for all logs related to this task, returning an append-only audit trail of who did what and when.
- **Expected Response**: `200 OK` with an array of activity logs (e.g., showing the task was "created").

### Step 8: Run Tests
- **Command**: `pytest --cov=app tests/`
- **Behind the Scenes**: The `pytest` framework spins up a test environment, using an in-memory SQLite database or a test PostgreSQL instance. It overrides the FastAPI `get_db` dependency to use test sessions, simulating HTTP requests via `httpx.AsyncClient`, and validates the API logic securely without affecting production data.
- **Expected Response**: A terminal output showing all tests passing and a coverage report indicating the percentage of code tested.

---

## Glossary for Beginners

- **JWT (JSON Web Token)**: A secure, encrypted digital "ID card" the API gives you when you log in. You show this card with every request to prove who you are.
- **FastAPI**: The Python framework we use to build the web server quickly and efficiently.
- **Pydantic**: A library that strictly checks incoming data (e.g., ensuring a user's age is a number, not a word).
- **SQLAlchemy**: A tool that lets us write Python code to talk to the database, instead of having to write raw SQL code.
- **Alembic**: A tool that tracks changes to our database over time (like adding a new column to a table).
- **ASGI**: The asynchronous standard that allows our Python server to handle thousands of requests at the exact same time without waiting in line.
- **Dependency Injection**: A technique where FastAPI automatically hands our functions the tools they need (like a database connection) exactly when they need them.
- **Docker**: A tool that packages the whole app into a virtual "box" so it runs the exact same way on your laptop as it does on a cloud server.
- **PostgreSQL**: The robust, open-source database engine where all the data is actually saved on the hard drive.

---

## FAQ / Common Questions

**Q: Where do I change the JWT secret?**
A: You can change the `SECRET_KEY` inside the `.env` file. Never share this secret with anyone!

**Q: How do I add a new endpoint?**
A: First, define the URL in a file inside `app/routes/`. Then, write the business logic for it inside `app/services/`. Finally, make sure the input/output formats are defined in `app/schemas/`.

**Q: How do I reset the database?**
A: If you are using Docker, you can destroy the database and start fresh by running `docker-compose down -v` and then `docker-compose up -d`.

**Q: What does the activity log do?**
A: It secretly records every action taken on a task (like changing its status to "done"). This creates an "audit trail" so teams can see exactly who changed what, preventing disputes.

**Q: Why do we use async/await?**
A: It allows the server to keep working on other things while it waits for the database to fetch data, making the API incredibly fast.

**Q: How do I view the database manually?**
A: If you are running Docker, open your browser to `http://localhost:5050`. This is the pgAdmin dashboard. You can log in using the credentials in your `.env` file and look directly at the tables!

---

## For Developers vs For Non-Programmers

**For Non-Programmers**: You don't need to read the code to understand what this project does! Start by reading this README, the `WALKTHROUGH.md`, and the `APITOUR.md`. You can even run the app using Docker and click around the Swagger dashboard at `http://localhost:8000/docs` to see it in action!

**For Developers**: Start by exploring `app/models/` to understand the data structures, then follow the request lifecycle from `app/routes/` down to `app/services/`. We enforce a strict separation of concerns, and rely heavily on Pydantic for validation and SQLAlchemy for async database operations. Run the tests frequently!
