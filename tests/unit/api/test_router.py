import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from fastauth.api.router import build_auth_router
from fastauth.auth.config import AuthConfig
from fastauth.auth.manager import AuthManager


class MockUserSchema(BaseModel):
    id: str = "user_123"
    username: str
    password: str


class MockUserStore:
    def __init__(self):
        self.users = {}

    async def create(self, **kwargs):
        user = MockUserSchema(**kwargs)
        self.users[user.username] = user
        return user

    async def find(self, **kwargs):
        return self.users.get(kwargs.get("username"))

    async def get(self, user_id):
        for u in self.users.values():
            if u.id == user_id:
                return u
        return None


class MockStrategy:
    def __init__(self):
        self.is_json_web_token = True
        self.use_cookie = False

    async def issue(self, response, data, ttl):
        return {"access_token": "token_123"}

    async def extract(self, request):
        return {"sub": "user_123", "sid": "session_123"}

    async def revoke(self, response):
        pass


@pytest.fixture
def auth_manager():
    config = AuthConfig(slug="auth", login_fields=["username"])
    return AuthManager(
        config=config,
        user_store=MockUserStore(),
        session_store=None,  # Stateless for simplicity
        strategy=MockStrategy(),
        schema=MockUserSchema,
    )


@pytest.fixture
def client(auth_manager):
    app = FastAPI()
    router = build_auth_router(auth_manager)
    app.include_router(router)
    return TestClient(app)


def test_signup_endpoint(client):
    response = client.post(
        "/auth/signup", json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
    assert "access_token" in response.json()


def test_login_endpoint(client):
    # First signup
    client.post(
        "/auth/signup", json={"username": "testuser", "password": "password123"}
    )

    # Then login
    response = client.post(
        "/auth/login", json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login", json={"username": "nonexistent", "password": "password"}
    )
    assert response.status_code == 401
