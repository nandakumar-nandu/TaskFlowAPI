# -*- coding: utf-8 -*-
"""
🛡️ UPLOAD SIZE LIMIT MIDDLEWARE (upload_limit.py)
-------------------------------------------------
Custom ASGI middleware that enforces a maximum HTTP request body size on POST requests.

Why this exists:
  Without a payload size guard, a malicious or careless client could send an
  extremely large file upload (e.g. a 500 MB video) which would consume all
  available server memory before FastAPI even begins processing the request.

How it works:
  1. For every incoming POST request, this middleware reads the Content-Length
     HTTP header (a standard header clients send to declare payload size).
  2. If Content-Length exceeds MAX_UPLOAD_BYTES (5 MB), it immediately rejects
     the request with HTTP 413 Payload Too Large — before the body is read.
  3. For non-POST methods or requests without a Content-Length header, the
     middleware passes the request through to the next layer unchanged.

Registration order (see app/main.py):
  UploadSizeLimitMiddleware is registered AFTER SlowAPIMiddleware, meaning in
  Starlette's LIFO middleware stack it executes BEFORE the rate limiter.
  This ensures oversized uploads are rejected cheaply before rate-limit tracking.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class UploadSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    🛡️ ASGI middleware enforcing a maximum payload size on POST requests.

    Inherits from BaseHTTPMiddleware (Starlette) which handles the async
    dispatch boilerplate, letting us focus purely on the size-check logic.
    """

    # Maximum allowed request body in bytes: 5 Megabytes.
    # 5 * 1024 * 1024 = 5,242,880 bytes.
    MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB

    async def dispatch(self, request: Request, call_next):
        """
        🛡️ Intercept every HTTP request before it reaches the route handler.

        Parameters:
            request  → The incoming ASGI request object (headers, body, method, etc.)
            call_next → A callable that forwards the request to the next middleware
                        or the actual route handler if no middleware remains.

        Returns:
            JSONResponse (HTTP 413) if the payload is too large.
            Otherwise, the response produced by the downstream handler.
        """
        # ⚙️ Only enforce size limits on POST requests.
        # GET, DELETE, PATCH, PUT are either body-less or handled differently.
        if request.method == "POST":
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    # ⚙️ Convert the Content-Length header string to an integer byte count.
                    size = int(content_length)
                    if size > self.MAX_UPLOAD_BYTES:
                        # ❌ Reject immediately — do not read the oversized body.
                        return JSONResponse(
                            status_code=413,
                            content={"detail": "Payload too large. Maximum allowed size is 5 MB."}
                        )
                except ValueError:
                    # ⚙️ If Content-Length is non-numeric, ignore it and pass through.
                    # The route handler will deal with any malformed body downstream.
                    pass

        # ⚙️ Forward the request to the next layer (rate limiter or route handler).
        return await call_next(request)
