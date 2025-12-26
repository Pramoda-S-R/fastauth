# tokens/base.py
from typing import Protocol, Any

from fastapi import Request, Response


class AuthStrategy(Protocol):
    async def issue(
        self, response: Response, data: dict[str, Any], ttl_seconds: int
    ) -> None | dict[str, str]: ...
    async def extract(self, request: Request) -> dict[str, Any] | None: ...
    async def revoke(self, response: Response) -> None: ...
