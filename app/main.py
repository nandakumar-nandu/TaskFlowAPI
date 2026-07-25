# -*- coding: utf-8 -*-
"""
🚀 MAIN APPLICATION ENTRYPOINT (main.py)
----------------------------------------
Initializes the FastAPI framework, hooks up middleware, routers, and health checks.
"""

from fastapi import FastAPI, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db

import sys
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router
from app.routes.categories import router as categories_router
from app.routes.users import router as users_router
from app.middleware.upload_limit import UploadSizeLimitMiddleware

# ⚙️ Configure API Rate Limiting strategy: IP-based rate limiting (using get_remote_address)
# 🛡️ Global default limit: 100 requests per minute.
# 🧪 Rate limiter is disabled during unit/integration test runs (checked via sys.modules) to avoid test interference.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    enabled="pytest" not in sys.modules
)

app = FastAPI(
    title="TaskFlow API",
    version="1.0.0",
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

# ⚙️ Attach rate limiter state, middleware, and error handlers to application instance
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(UploadSizeLimitMiddleware)

# 🛣️ Include API routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(categories_router)
app.include_router(users_router)


@app.get("/health")
async def health_check(response: Response, db: AsyncSession = Depends(get_db)):
    """
    🔌 Utility health status check.
    Queries the database using the asynchronous engine to verify active connection.
    """
    try:
        # ⚙️ Run a lightweight validation query
        await db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        # ❌ Connection failure logging and degraded response mapping
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "error",
            "database": f"disconnected: {str(e)}"
        }
