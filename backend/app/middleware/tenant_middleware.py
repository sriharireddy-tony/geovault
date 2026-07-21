import logging

from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings
from app.core.security import decode_token

logger = logging.getLogger("geovault.tenant")


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Extract tenant_id + user_id from JWT and store on request.state for logging / audit."""

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        request.state.tenant_id = None
        request.state.user_id = None

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                payload = decode_token(auth_header[7:])
                request.state.user_id = payload.get("sub")
                request.state.tenant_id = payload.get("tid")
            except JWTError:
                pass

        response = await call_next(request)

        logger.debug(
            "tenant=%s user=%s %s %s %s",
            request.state.tenant_id,
            request.state.user_id,
            request.method,
            request.url.path,
            response.status_code,
        )
        return response
