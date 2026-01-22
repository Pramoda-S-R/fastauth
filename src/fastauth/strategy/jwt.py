from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Pattern, Union

import jwt
from fastapi import Request, Response

from ..exceptions import TokenException


class JWTStrategy:
    def __init__(
        self,
        secret: str,
        algorithm: str = "HS256",
        use_cookie: bool = True,
        cookie_name: str = "__Host-access",
        expired_token_whitelist: list[Union[str, Pattern[str]]] = ["/auth/logout"],
        get_additional_claims: Callable[[None], dict[str, str]] = lambda: {},
        refresh_ttl_seconds: int = 604800,
    ):
        self.secret = secret
        self.algorithm = algorithm
        self.cookie_name = cookie_name
        self.refresh_ttl_seconds = refresh_ttl_seconds
        self.use_cookie = use_cookie
        self.get_additional_claims = get_additional_claims
        self.expired_token_whitelist: list[Union[str, Pattern[str]]] = (
            expired_token_whitelist
        )

    def is_expired_token_allowed(self, path: str) -> bool:
        for entry in self.expired_token_whitelist:
            if isinstance(entry, str) and entry == path:
                return True
            if hasattr(entry, "match") and entry.match(path):
                return True
        return False

    async def verify(self, token: str, allow_expired: bool = False) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={"verify_exp": not allow_expired},
            )
        except jwt.ExpiredSignatureError as e:
            raise TokenException(e)
        except jwt.InvalidTokenError as e:
            raise TokenException(e)

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
                key=self.cookie_name,
                value=access_token,
                max_age=ttl_seconds,
                httponly=True,
                secure=True,
                samesite="lax",
            )
            return None
        else:
            return {"access_token": access_token, "refresh_token": refresh_token}

    async def extract(self, request: Request) -> dict[str, Any] | None:
        token: str | None = None
        allow_expired = False

        path = request.url.path
        if self.is_expired_token_allowed(path):
            allow_expired = True

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

        return await self.verify(token, allow_expired)

    async def revoke(self, response: Response) -> None:
        if self.use_cookie:
            response.delete_cookie(
                key=self.cookie_name,
                path="/",
                secure=True,
                httponly=True,
                samesite="lax",
            )
        return None
