import pytest
from fastapi import Request, Response

from fastauth.auth.config import AuthConfig
from fastauth.auth.manager import AuthManager
from fastauth.users.base import BaseUser


# Mocks
class MockUserStore:
    def __init__(self):
        self.users = {}

    async def create(self, data: dict) -> BaseUser:
        user = CustomUser(**data)
        user.id = "user_123"
        self.users[user.id] = user
        return user

    async def get(self, user_id: str) -> BaseUser | None:
        return self.users.get(user_id)

    async def delete(self, user_id: str) -> None:
        pass


class MockSessionStore:
    async def create(self, user_id: str, data: dict = None) -> str:
        return "session_123"

    async def get(self, session_id: str) -> dict | None:
        return {}

    async def delete(self, session_id: str) -> None:
        pass

    async def refresh(self, session_id: str) -> None:
        pass


class MockAuthStrategy:
    async def issue(self, response: Response, user_id: str) -> None:
        pass

    async def extract(self, request: Request) -> str | None:
        return "token_123"

    async def revoke(self, response: Response) -> None:
        pass


# Custom Schema
class CustomUser(BaseUser):
    username: str
    age: int


def test_auth_manager_validation_success():
    config = AuthConfig(slug="auth", login_fields=["username"])
    # Should not raise
    AuthManager(
        config=config,
        user_store=MockUserStore(),
        session_store=MockSessionStore(),
        strategy=MockAuthStrategy(),
        schema=CustomUser,
    )


# (deprecated)
def test_auth_manager_validation_failure():
    config = AuthConfig(slug="auth", login_fields=["phone"])  # phone missing
    with pytest.raises(
        ValueError, match="Login field 'phone' is not in the user schema"
    ):
        AuthManager(
            config=config,
            user_store=MockUserStore(),
            session_store=MockSessionStore(),
            strategy=MockAuthStrategy(),
            schema=CustomUser,
        )


@pytest.mark.asyncio
async def test_signup_flow():
    config = AuthConfig(slug="auth", login_fields=["username"])
    auth = AuthManager(
        config=config,
        user_store=MockUserStore(),
        session_store=MockSessionStore(),
        strategy=MockAuthStrategy(),
        schema=CustomUser,
    )

    # Simulate Router Request
    # Instantiate schema (simulating FastAPI parsing)
    req_data = {"username": "testuser", "password": "password", "age": 25}
    req = CustomUser(**req_data)

    # Manually call what the router would call
    user = await auth.user.create(req.model_dump())
    assert user.id == "user_123"
    assert user.username == "testuser"
    assert user.age == 25
