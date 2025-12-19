# users/base.py
from typing import Protocol

from pydantic import BaseModel


class BaseUser(BaseModel):
    id: str | None = None
    password: str

class UserStore(Protocol):
    async def create(self, data: dict) -> BaseUser: ...
    async def get(self, user_id: str) -> BaseUser | None: ...
    async def delete(self, user_id: str) -> None: ...
