# users/base.py
from typing import Protocol

from pydantic import BaseModel, ConfigDict


class BaseUser(BaseModel):
    id: str | None = None
    password: str
    model_config = ConfigDict(extra="allow")


class UserStore(Protocol):
    """Protocol for user storage implementations.
    
    Implementations must provide async methods for:
    - Creating new users
    - Finding users by credentials
    - Getting users by ID
    - Deleting users
    
    Methods:
        create: Create a new user
            Args:
                **kwargs: User data
            Returns:
                The created user
        find: Find a user by credentials
            Args:
                **kwargs: Credentials (e.g., email, username)
            Returns:
                The found user or None if not found
        get: Get a user by ID
            Args:
                user_id: The user ID to look up
            Returns:
                The found user or None if not found
        delete: Delete a user
            Args:
                user_id: The user ID to delete
    """
    async def create(self, **kwargs) -> BaseUser: ...
    async def find(self, **kwargs) -> BaseUser | None: ...
    async def get(self, user_id: str) -> BaseUser | None: ...
    async def delete(self, user_id: str) -> None: ...
