from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import jwt
from fastapi import Request, Response
from fastapi.security import HTTPBearer

from ..exceptions import InvalidTokenException, TokenExpiredException


class JWTStrategy:
    def __init__(
        self,
        secret: str,
        algorithm: str = "HS256",
        use_cookie: bool = True,
        get_additional_claims: Callable[[None], dict[str, str]] = lambda: {},
        refresh_ttl_seconds: int = 604800,
    ):
        self.secret = secret
        self.algorithm = algorithm
        self.refresh_ttl_seconds = refresh_ttl_seconds
        self.use_cookie = use_cookie
        self.get_additional_claims = get_additional_claims
        self._security = HTTPBearer()

    async def verify(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError as e:
            raise TokenExpiredException(e)
        except jwt.InvalidTokenError as e:
            raise InvalidTokenException(e)

    async def issue(
        self, response: Response, data: dict[str, Any], ttl_seconds: int
    ) -> dict[str, str] | None:
        claims = self.get_additional_claims() | data

        issued_at = datetime.now(timezone.utc)

        access_claims = claims | {
            "iat": issued_at,
            "exp": issued_at + timedelta(seconds=ttl_seconds),
        }

        access_token = jwt.encode(access_claims, self.secret, algorithm=self.algorithm)

        refresh_claims = claims | {
            "iat": issued_at,
            "exp": issued_at + timedelta(seconds=self.refresh_ttl_seconds),
        }

        refresh_token = jwt.encode(
            refresh_claims, self.secret, algorithm=self.algorithm
        )

        # set refresh token cookie
        if self.use_cookie:
            response.set_cookie(
                key="refresh-token",
                value=refresh_token,
                expires=self.refresh_ttl_seconds,
                httponly=True,
                secure=True,
                samesite="lax",
            )
            return None
        else:
            return {"access_token": access_token, "refresh_token": refresh_token}

    async def extract(self, request: Request) -> dict[str, Any] | None:
        token: str | None = None

        if self.use_cookie:
            token = request.cookies.get("refresh-token")
        else:
            authorization = request.headers.get("Authorization")
            if authorization:
                scheme, _, param = authorization.partition(" ")
                if scheme.lower() == "bearer":
                    token = param

        if not token:
            return None

        return await self.verify(token)

    async def revoke(self, response: Response) -> None:
        if self.use_cookie:
            response.delete_cookie("refresh-token")
