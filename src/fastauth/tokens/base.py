# tokens/base.py
from typing import Protocol

from fastapi import Request, Response


class AuthStrategy(Protocol):
    async def issue(self, response: Response, data: dict, ttl_seconds: int) -> None | dict[str, str]: ...
    async def extract(self, request: Request) -> dict | None: ...
    async def revoke(self, response: Response) -> None: ...
