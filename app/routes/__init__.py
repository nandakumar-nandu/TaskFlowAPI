# -*- coding: utf-8 -*-
# 🛣️ API routers package

from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router
from app.routes.categories import router as categories_router
from app.routes.users import router as users_router
from app.routes.comments import router as comments_router

__all__ = [
    "auth_router",
    "tasks_router",
    "categories_router",
    "users_router",
    "comments_router"
]
