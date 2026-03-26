"""
Authentication strategy protocol definitions.

Defines the interface for token strategies (JWT, Opaque, etc.)
that handle token issuance, extraction, and revocation.
"""

from typing import Any, Protocol

from fastapi import Request, Response


class AuthStrategy(Protocol):
    """Protocol for token-based authentication strategies.

    Implementations must provide methods for:
    - Issuing tokens (with optional cookie support)
    - Extracting credentials from requests
    - Revoking tokens (clearing cookies/headers)

    Attributes:
        use_cookie: Whether to use cookies for authentication
    
    Methods:
        issue: Issue a new authentication token
            Args:
                response: FastAPI response object (for setting cookies)
                data: Token claims (sub, jti, sid, etc.)
                ttl_seconds: Token time-to-live in seconds
            Returns:
                None if using cookies, or dict with access_token/refresh_token
        extract: Extract credentials from a request
            Args:
                request: FastAPI request object
            Returns:
                Dict with claims (sub, sid, etc.) or None if not authenticated
        revoke: Revoke/clear authentication tokens
            Args:
                response: FastAPI response object (for clearing cookies)
    """

    # Optional attribute indicating cookie-based auth
    use_cookie: bool = True

    async def issue(
        self, response: Response, data: dict[str, Any], ttl_seconds: int
    ) -> None | dict[str, str]:
        """Issue a new authentication token.

        Args:
            response: FastAPI response object (for setting cookies)
            data: Token claims (sub, jti, sid, etc.)
            ttl_seconds: Token time-to-live in seconds

        Returns:
            None if using cookies, or dict with access_token/refresh_token
        """
        ...

    async def extract(self, request: Request) -> dict[str, Any] | None:
        """Extract credentials from a request.

        Args:
            request: FastAPI request object

        Returns:
            Dict with claims (sub, sid, etc.) or None if not authenticated
        """
        ...

    async def revoke(self, response: Response) -> None:
        """Revoke/clear authentication tokens.

        Args:
            response: FastAPI response object (for clearing cookies)
        """
        ...
