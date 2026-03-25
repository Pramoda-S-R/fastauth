import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Union

from fastapi import Request, Response

from ..exceptions import TokenException


class OpaqueStrategy:
    """Opaque token strategy - tokens are random strings with no embedded claims.

    Session data is stored server-side (via SessionStore), making this suitable
    for scenarios requiring session revocation, rotation, or server-side state.
    """

    def __init__(
        self,
        use_cookie: bool = True,
        cookie_name: str = "__Host-access",
        token_length: int = 32,
        get_additional_claims: Callable[
            [dict[str, Any]], dict[str, str]
        ] = lambda _: {},
        refresh_ttl_seconds: int = 604800,
    ):
        self.cookie_name = cookie_name
        self.token_length = token_length
        self.use_cookie = use_cookie
        self.get_additional_claims = get_additional_claims
        self.refresh_ttl_seconds = refresh_ttl_seconds

    def _generate_token(self) -> str:
        """Generate a cryptographically secure random token."""
        return uuid.uuid4().hex[: self.token_length]

    async def issue(
        self, response: Response, data: dict[str, Any], ttl_seconds: int
    ) -> dict[str, str] | None:
        """Issue new access and refresh tokens.

        Args:
            response: FastAPI response object to set cookies on
            data: Token claims including 'sub' (user_id), 'sid' (session_id), 'jti' (token_id)
            ttl_seconds: Time-to-live for access token in seconds

        Returns:
            Dict with access_token and refresh_token if not using cookies, None otherwise
        """
        access_token = self._generate_token()
        refresh_token = self._generate_token()

        claims = self.get_additional_claims(data) | data
        issued_at = datetime.now(timezone.utc)

        access_claims = claims | {
            "iat": issued_at,
            "exp": issued_at + timedelta(seconds=ttl_seconds),
            "type": "access",
        }

        refresh_claims = claims | {
            "iat": issued_at,
            "exp": issued_at + timedelta(seconds=self.refresh_ttl_seconds),
            "type": "refresh",
        }

        if self.use_cookie:
            response.set_cookie(
                key=self.cookie_name,
                value=access_token,
                max_age=ttl_seconds,
                httponly=True,
                secure=True,
                samesite="lax",
            )
            response.set_cookie(
                key=f"{self.cookie_name}-refresh",
                value=refresh_token,
                max_age=self.refresh_ttl_seconds,
                httponly=True,
                secure=True,
                samesite="lax",
            )
            return None
        else:
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }

    async def extract(self, request: Request) -> dict[str, Any] | None:
        """Extract token claims from request.

        Looks for token in:
        - Cookie (if use_cookie=True)
        - Authorization header (Bearer scheme)

        Returns:
            Dict with claims or None if no valid token found
        """
        token: str | None = None

        if self.use_cookie:
            token = request.cookies.get(self.cookie_name)
        else:
            authorization = request.headers.get("Authorization")
            if authorization:
                scheme, _, param = authorization.partition(" ")
                if scheme.lower() == "bearer":
                    token = param

        if not token:
            return None

        return {"token": token}

    async def revoke(self, response: Response) -> None:
        """Revoke tokens by clearing cookies or delegating to session store."""
        if self.use_cookie:
            response.delete_cookie(
                key=self.cookie_name,
                path="/",
                secure=True,
                httponly=True,
                samesite="lax",
            )
            response.delete_cookie(
                key=f"{self.cookie_name}-refresh",
                path="/",
                secure=True,
                httponly=True,
                samesite="lax",
            )
