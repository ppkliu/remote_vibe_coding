import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware - 10 commands/min per user

    Tracks requests per user and returns 429 if limit exceeded.
    Uses X-RateLimit-* headers in responses.
    """

    def __init__(self, app, requests_per_minute: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.user_requests = defaultdict(list)  # user_id -> list of timestamps
        self.window_size = 60  # seconds

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip rate limiting for non-command endpoints
        if request.url.path in ["/health", "/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/refresh", "/api/v1/auth/logout"]:
            return await call_next(request)

        # Extract user from token if available
        user_id = self._get_user_id(request)

        if user_id:
            now = time.time()
            # Clean old requests (older than window_size)
            self.user_requests[user_id] = [
                ts for ts in self.user_requests[user_id]
                if now - ts < self.window_size
            ]

            # Check rate limit
            if len(self.user_requests[user_id]) >= self.requests_per_minute:
                response = Response(
                    content={"detail": "Rate limit exceeded: 10 requests per minute"},
                    status_code=429
                )
                response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(int(self.user_requests[user_id][0] + self.window_size))
                return response

            # Record this request
            self.user_requests[user_id].append(now)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        if user_id:
            remaining = max(0, self.requests_per_minute - len(self.user_requests[user_id]))
            reset_time = int(self.user_requests[user_id][0] + self.window_size) if self.user_requests[user_id] else int(now + self.window_size)

            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response

    def _get_user_id(self, request: Request) -> str | None:
        """Extract user ID from authorization token"""
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Extract user_id from JWT token without full validation
            # This is a simplified extraction - in production use proper JWT validation
            try:
                from ..services.auth_service import AuthService
                user_id = AuthService.verify_token(token, "access")
                return user_id
            except:
                return None
        return None
