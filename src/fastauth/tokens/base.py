# tokens/base.py
from typing import Protocol

from fastapi import Request, Response


class AuthStrategy(Protocol):
    async def issue(self, response: Response, user_id: str) -> None: ...
    async def extract(self, request: Request) -> str | None: ...
    async def revoke(self, response: Response) -> None: ...
