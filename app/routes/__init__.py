# -*- coding: utf-8 -*-
# 🛣️ API routers package

from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router

__all__ = ["auth_router", "tasks_router"]
