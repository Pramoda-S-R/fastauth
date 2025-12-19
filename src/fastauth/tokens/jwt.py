from fastapi import Request, Response
from datetime import datetime, timezone, timedelta
from typing import Callable
import jwt

class JWTStrategy:
    def __init__(self, secret: str, algorithm: str = "HS256", set_refresh_cookie: bool = True, get_additional_claims: Callable[[None], dict[str, str]] = lambda: {}, refresh_ttl_seconds: int = 604800):
        self.secret = secret
        self.algorithm = algorithm
        self.refresh_ttl_seconds = refresh_ttl_seconds
        self.set_refresh_cookie = set_refresh_cookie
        self.get_additional_claims = get_additional_claims
    
    async def issue(self, response: Response, data: dict, ttl_seconds: int) -> dict[str, str]:
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

        refresh_token = jwt.encode(refresh_claims, self.secret, algorithm=self.algorithm)

        # set refresh token cookie
        if self.set_refresh_cookie:
            response.set_cookie(key="refresh-token", value=refresh_token, expires=self.refresh_ttl_seconds, httponly=True, secure=True, samesite="lax")

        return {"access_token": access_token, "refresh_token": refresh_token}
    
    async def extract(self, request: Request) -> str | None:
        pass
    
    async def revoke(self, response: Response) -> None:
        pass