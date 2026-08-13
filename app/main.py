# -*- coding: utf-8 -*-
"""
🚀 MAIN APPLICATION ENTRYPOINT (main.py)
----------------------------------------
This is the first file FastAPI reads when the server starts. It ties together
every piece of the project: middleware layers, route handlers, and the health check.

Key responsibilities of this file:
  1. Configure and attach the IP-based rate limiter (slowapi).
  2. Register ASGI middleware layers (rate-limiting + upload size guard).
  3. Mount domain-specific API routers (/auth, /tasks, /categories, /users, /comments).
  4. Expose the /health endpoint for uptime monitoring.
"""

from fastapi import FastAPI, Depends, Response, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db

import sys
import logging
import json
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.core.limiter import limiter

# ⚙️ JSON LOGGING SETUP
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt)
        }
        return json.dumps(log_obj)

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
# Only add the handler if one doesn't exist to prevent duplicate logs in testing
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(settings.LOG_LEVEL)


from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router
from app.routes.categories import router as categories_router
from app.routes.users import router as users_router
from app.routes.comments import router as comments_router
from app.middleware.upload_limit import UploadSizeLimitMiddleware

# ⚙️ RATE LIMITER SETUP
# limiter is imported from app.core.limiter

# ⚙️ CREATE THE FASTAPI APPLICATION INSTANCE
# The title, version, and description appear in the auto-generated Swagger UI
# documentation accessible at /docs when the server is running.
app = FastAPI(
    title="TaskFlow API",
    version="1.3.0",
    description=(
        "TaskFlow API is a production-ready, high-performance, asynchronous REST API "
        "built with Python, FastAPI, and PostgreSQL.\n\n"
        "It provides robust features for user authentication, task organization, categorizations, "
        "tag mappings, sorting, pagination, and database query optimizations."
    ),
    contact={
        "name": "TaskFlow Developer Support",
        "email": "support@taskflow.local",
        "url": "https://github.com/nandakumar-nandu/TaskFlowAPI"
    }
)

# ⚙️ ATTACH RATE LIMITER STATE
# The limiter object must be stored on app.state so the SlowAPIMiddleware
# (registered below) can find and use it to track request counts.
app.state.limiter = limiter

# ⚙️ REGISTER EXCEPTION HANDLER FOR RATE LIMIT EXCEEDED
# When a client exceeds the 100/min threshold, slowapi raises RateLimitExceeded.
# This handler converts that exception into an HTTP 429 Too Many Requests response
# with a Retry-After header so clients know when to try again.
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ⚙️ REGISTER MIDDLEWARE (execution order is LIFO — last-in is outermost)
# Rate limiter must come before auth middleware to prevent unnecessary token validation on rate-limited requests.
app.add_middleware(SlowAPIMiddleware)

# We allow all origins in development; restrict to specific domains in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Rejects payloads over 5 MB with HTTP 413 Payload Too Large.
app.add_middleware(UploadSizeLimitMiddleware)

# 🛣️ MOUNT DOMAIN-SPECIFIC ROUTERS
# Each router declares its own URL prefix and Swagger tag group.
# Mounted under the global /api/v1 prefix for future-proofing.
api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth_router)
api_v1.include_router(tasks_router)
api_v1.include_router(categories_router)
api_v1.include_router(users_router)
api_v1.include_router(comments_router)

app.include_router(api_v1)


@app.get("/health")
async def health_check(response: Response, db: AsyncSession = Depends(get_db)):
    """
    🔌 GET /health — Service health status probe.

    Executes a minimal "SELECT 1" query against the database to confirm
    that both the API process and the PostgreSQL connection pool are alive.

    Returns:
        200 OK  → {"status": "ok", "database": "connected"}
        503 Service Unavailable → {"status": "error", "database": "disconnected: <reason>"}

    This endpoint is intentionally unauthenticated (no JWT required) so that
    external monitors, Docker HEALTHCHECK instructions, and Railway can probe
    liveness without needing to maintain a login token.
    """
    try:
        # ⚙️ Run the lightest possible query — "SELECT 1" — to ping the database.
        # This verifies the async connection pool is healthy without reading any table data.
        await db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        # ❌ Any exception here means the database is unreachable (refused connection,
        # timeout, bad credentials, etc.). We downgrade the response to HTTP 503
        # so that uptime monitors can detect the degraded state and trigger alerts.
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "error",
            "database": f"disconnected: {str(e)}"
        }
