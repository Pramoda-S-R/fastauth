# users/base.py
from pydantic import BaseModel
from typing import Protocol

class BaseUser(BaseModel):
    id: str | None = None
    password: str

class UserStore(Protocol):
    async def create(self, data: dict) -> BaseUser: ...
    async def get(self, user_id: str) -> BaseUser | None: ...
    async def delete(self, user_id: str) -> None: ...
