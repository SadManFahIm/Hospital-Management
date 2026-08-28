"""
ASGI middleware for request correlation ids and safe access logging.

- Attaches a request id to the request context so all logs within the request
  carry it (via app.core.log.set_request_id).
- Logs one access line per request with method, path, status, and duration.
- NEVER logs Authorization headers, tokens, passwords, or request bodies.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import MutableMapping
from typing import Any

from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.log import set_request_id

logger = logging.getLogger("medcore.access")


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())
        set_request_id(request_id)

        method = scope.get("method", "")
        path = scope.get("path", "")

        status_holder: dict[str, int] = {"status": 0}
        started = time.perf_counter()

        async def _send(message: MutableMapping[str, Any]) -> None:
            if message["type"] == "http.response.start":
                status_holder["status"] = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, _send)
        except Exception:
            # Server-side diagnostics only; clients get a safe 500 from the app.
            logger.exception(
                "Unhandled exception",
                extra={"_extra": {"method": method, "path": path, "request_id": request_id}},
            )
            raise
        finally:
            duration_ms = (time.perf_counter() - started) * 1000
            logger.info(
                "request",
                extra={
                    "_extra": {
                        "method": method,
                        "path": path,
                        "status": status_holder["status"],
                        "duration_ms": round(duration_ms, 2),
                        "request_id": request_id,
                    }
                },
            )

        set_request_id(None)


class SecurityHeadersMiddleware:
    """Adds safe, standard HTTP security headers to every response.

    The security-relevant headers here are safe for any deployment. HSTS is
    added only when the request arrived over HTTPS, so a plain-HTTP dev/local
    deployment is not forced onto https by a stale header.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def _send(message: MutableMapping[str, Any]) -> None:
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                headers = [h for h in headers if h[0].lower() not in _PROTECTED_HEADERS]
                headers.extend(_DEFAULT_HEADERS)
                if scope.get("scheme") == "https":
                    headers.append((b"strict-transport-security", _HSTS_VALUE))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, _send)


_DEFAULT_HEADERS: list[tuple[bytes, bytes]] = [
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"no-referrer"),
    (b"x-permitted-cross-domain-policies", b"none"),
]
_PROTECTED_HEADERS = {
    b"x-content-type-options",
    b"x-frame-options",
    b"referrer-policy",
    b"x-permitted-cross-domain-policies",
    b"strict-transport-security",
}
_HSTS_VALUE = b"max-age=31536000; includeSubDomains"
