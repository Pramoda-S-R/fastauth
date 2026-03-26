from typing import Any

from fastapi import Request, Response


class OpaqueStrategy:
    """Opaque token strategy - Session id with no embedded claims.

    Session data is stored server-side (via SessionStore), making this suitable
    for scenarios requiring session revocation, rotation, or server-side state.
    """

    def __init__(
        self,
        use_cookie: bool = True,
        cookie_name: str = "__Host-session-id",
    ):
        self.cookie_name = cookie_name
        self.use_cookie = use_cookie

    async def issue(
        self, response: Response, data: dict[str, Any], ttl_seconds: int
    ) -> dict[str, str] | None:
        """Issue new access and refresh tokens.

        Args:
            **response**: FastAPI response object to set cookies on
            **data**: Claims including 'sid' (session_id)
            **ttl_seconds**: Time-to-live for session in seconds

        Returns:
            Dict with `sid` if not using cookies, None otherwise
        """

        session_id = data.get("sid")
        if not session_id:
            raise ValueError("Session ID not found in claims")

        if self.use_cookie:
            response.set_cookie(
                key=self.cookie_name,
                value=session_id,
                max_age=ttl_seconds,
                httponly=True,
                secure=True,
                samesite="lax",
            )
            return None
        else:
            return {
                "sid": session_id,
            }

    async def extract(self, request: Request) -> dict[str, Any] | None:
        """Extract session id from request.

        Looks for session id in:
        - Cookie (if use_cookie=True)
        - Authorization header (Bearer scheme)

        Returns:
            Dict with `sid` or None if no valid session id found
        """
        session_id: str | None = None

        if self.use_cookie:
            session_id = request.cookies.get(self.cookie_name)
        else:
            authorization = request.headers.get("Authorization")
            if authorization:
                scheme, _, param = authorization.partition(" ")
                if scheme.lower() == "bearer":
                    session_id = param

        if not session_id:
            return None

        return {"sid": session_id}

    async def revoke(self, response: Response) -> None:
        """Revoke session by clearing cookies."""
        if self.use_cookie:
            response.delete_cookie(
                key=self.cookie_name,
                path="/",
                secure=True,
                httponly=True,
                samesite="lax",
            )
