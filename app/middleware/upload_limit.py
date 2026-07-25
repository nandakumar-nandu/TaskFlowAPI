# -*- coding: utf-8 -*-
"""
🛡️ UPLOAD SIZE LIMIT MIDDLEWARE (upload_limit.py)
-----------------------------------------------
Intercepts HTTP POST requests and validates the Content-Length header.
Rejects bodies exceeding 5MB with an HTTP 413 Payload Too Large.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class UploadSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    🛡️ ASGI middleware to enforce a maximum payload size limit on POST requests.
    Prevents large uploads from consuming server bandwidth/storage.
    """
    MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 Megabytes

    async def dispatch(self, request: Request, call_next):
        # 🛡️ Only enforce limit on POST requests
        if request.method == "POST":
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    size = int(content_length)
                    if size > self.MAX_UPLOAD_BYTES:
                        return JSONResponse(
                            status_code=413,
                            content={"detail": "Payload too large. Maximum allowed size is 5 MB."}
                        )
                except ValueError:
                    pass  # Ignore invalid Content-Length headers

        return await call_next(request)
