# import pytest (removed)
from pydantic import BaseModel
from fastauth.auth.manager import AuthManager
from fastauth.auth.config import AuthConfig
from fastauth.users.base import BaseUser, UserStore
from fastauth.sessions.base import SessionStore
from fastauth.tokens.base import AuthStrategy
from enum import Enum
from fastapi import Response, Request

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

class Roles(Enum):
    USER = "USER"
    ADMIN = "ADMIN"

# Custom Schema
class CustomUser(BaseUser):
    username: str
    age: int

def test_auth_manager_validation_success():
    config = AuthConfig(login_fields=["username"])
    # Should not raise
    AuthManager(
        config=config,
        user_store=MockUserStore(),
        session_store=MockSessionStore(),
        strategy=MockAuthStrategy(),
        role_enum=Roles,
        schema=CustomUser
    )

def test_auth_manager_validation_failure():
    config = AuthConfig(login_fields=["phone"]) # phone missing
    try:
        AuthManager(
            config=config,
            user_store=MockUserStore(),
            session_store=MockSessionStore(),
            strategy=MockAuthStrategy(),
            role_enum=Roles,
            schema=CustomUser
        )
        print("Error: validation failed to raise ValueError")
        exit(1)
    except ValueError as e:
        if "Login field 'phone' is not in the user schema" not in str(e):
            print(f"Error: Unexpected error message: {e}")
            exit(1)

import asyncio

def test_signup_flow():
    config = AuthConfig(login_fields=["username"])
    auth = AuthManager(
        config=config,
        user_store=MockUserStore(),
        session_store=MockSessionStore(),
        strategy=MockAuthStrategy(),
        role_enum=Roles,
        schema=CustomUser
    )
    
    # Simulate Router Request
    async def run_signup():
        # Instantiate schema (simulating FastAPI parsing)
        req_data = {"username": "testuser", "password": "password", "age": 25}
        req = CustomUser(**req_data)
        
        # Manually call what the router would call
        user = await auth.user.create(req.model_dump())
        assert user.id == "user_123"
        assert user.username == "testuser"
        assert user.age == 25
    
    asyncio.run(run_signup())

if __name__ == "__main__":
    # verification via running this script directly
    test_auth_manager_validation_success()
    test_auth_manager_validation_failure()
    test_signup_flow()
    print("All tests passed!")
