# users/base.py
from typing import Protocol

from pydantic import BaseModel, ConfigDict


class BaseUser(BaseModel):
    id: str | None = None
    password: str
    model_config = ConfigDict(extra="allow")

class UserStore(Protocol):
    async def create(self, **kwargs) -> BaseUser: ...
    async def find(self, **kwargs) -> BaseUser | None: ...
    async def get(self, user_id: str) -> BaseUser | None: ...
    async def delete(self, user_id: str) -> None: ...
