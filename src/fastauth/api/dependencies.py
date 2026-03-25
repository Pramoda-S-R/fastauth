"""
FastAPI dependencies for authentication.

Provides dependency functions for:
- Getting the current authenticated user
- Getting the current session ID
- Extracting credentials from requests
"""

from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional

from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..exceptions import (
    CredentialsException,
    SessionException,
    TokenException,
    UserException,
)

if TYPE_CHECKING:
    from ..auth.manager import AuthManager

from ..users.base import BaseUser


def _get_use_bearer(auth: "AuthManager") -> bool:
    """Determine if bearer token authentication should be used.

    Checks if the strategy uses cookie-based auth.
    If so, returns False (don't require bearer token).
    """
    if hasattr(auth.strategy, "use_cookie") and auth.strategy.use_cookie:
        return False
    return True


def get_current_user_dependency(
    auth: "AuthManager",
) -> Callable[[Request], Coroutine[Any, Any, BaseUser]]:
    """Factory to create the get_current_user dependency.

    Returns a callable that extracts and validates the current user
    from the request authentication credentials.
    """
    use_bearer = _get_use_bearer(auth)
    security = HTTPBearer(auto_error=False)

    async def _extract_credentials(request: Request) -> dict[str, Any]:
        """Extract credentials from request using strategy."""
        try:
            credentials = await auth.strategy.extract(request)
            if not credentials:
                raise CredentialsException("No credentials provided")
        except HTTPException:
            raise
        except Exception as e:
            raise TokenException(str(e))
        return credentials

    async def _get_current_user_impl(request: Request) -> BaseUser:
        """Core implementation for getting current user."""
        credentials = await _extract_credentials(request)

        # Extract user ID from credentials
        user_id = credentials.get("sub") or credentials.get("user_id")
        if not user_id:
            raise CredentialsException("Invalid token: missing subject")

        # Validate session if session store is configured
        if auth.session:
            session_id = credentials.get("sid")
            if not session_id:
                raise CredentialsException("No session ID in token")

            try:
                session_data = await auth.session.get(session_id)
            except Exception as e:
                raise SessionException(str(e))

            if not session_data:
                raise CredentialsException("Session not found or expired")

            # Verify session belongs to the same user
            session_user_id = session_data.get("user_id")
            if session_user_id != user_id:
                raise CredentialsException("Session/user mismatch")

        # Fetch user from user store
        user = await auth.user.get(user_id)
        if not user:
            raise UserException("User not found", status_code=404)

        return user

    if use_bearer:

        async def current_user_with_bearer(
            request: Request,
            credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
        ) -> BaseUser:
            return await _get_current_user_impl(request)

        return current_user_with_bearer

    else:

        async def current_user_with_cookie(request: Request) -> BaseUser:
            return await _get_current_user_impl(request)

        return current_user_with_cookie


def get_current_session_dependency(
    auth: "AuthManager",
) -> Callable[[Request], Coroutine[Any, Any, str]]:
    """Factory to create the get_current_session dependency.

    Returns a callable that extracts the current session ID
    from the request authentication credentials.
    """
    use_bearer = _get_use_bearer(auth)
    security = HTTPBearer(auto_error=False)

    async def _extract_credentials(request: Request) -> dict[str, Any]:
        """Extract credentials from request using strategy."""
        try:
            credentials = await auth.strategy.extract(request)
            if not credentials:
                raise CredentialsException("No credentials provided")
        except HTTPException:
            raise
        except Exception as e:
            raise TokenException(str(e))
        return credentials

    async def _get_current_session_impl(request: Request) -> str:
        """Core implementation for getting current session."""
        credentials = await _extract_credentials(request)

        session_id = credentials.get("sid")
        if not session_id:
            raise CredentialsException("No session ID in token")

        return session_id

    if use_bearer:

        async def current_session_with_bearer(
            request: Request,
            credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
        ) -> str:
            return await _get_current_session_impl(request)

        return current_session_with_bearer

    else:

        async def current_session_with_cookie(request: Request) -> str:
            return await _get_current_session_impl(request)

        return current_session_with_cookie
