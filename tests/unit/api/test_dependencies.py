import pytest
from fastapi import Request

from fastauth.api.dependencies import (get_current_session_dependency,
                                       get_current_user_dependency)
from fastauth.exceptions import CredentialsException


class MockUser:
    def __init__(self, id):
        self.id = id


class MockUserStore:
    async def get(self, user_id):
        if user_id == "valid_user":
            return MockUser(id=user_id)
        return None


class MockSessionStore:
    async def get(self, session_id):
        if session_id == "valid_session":
            return {"user_id": "valid_user"}
        return None


class MockAuthManager:
    def __init__(self, is_jwt=True, has_session=True):
        self.strategy = None
        self.is_jwt_strategy = is_jwt
        self.user = MockUserStore()
        self.session = MockSessionStore() if has_session else None


@pytest.fixture
def mock_strategy():
    class Strategy:
        def __init__(self):
            self.use_cookie = False

        async def extract(self, request):
            return {"sub": "valid_user", "sid": "valid_session"}

    return Strategy()


@pytest.mark.asyncio
async def test_get_current_user_success(mock_strategy):
    auth = MockAuthManager(is_jwt=True, has_session=True)
    auth.strategy = mock_strategy

    dependency = get_current_user_dependency(auth)
    request = Request(scope={"type": "http"})

    user = await dependency(request)
    assert user.id == "valid_user"


@pytest.mark.asyncio
async def test_get_current_user_no_session_fail(mock_strategy):
    auth = MockAuthManager(is_jwt=True, has_session=True)
    auth.strategy = mock_strategy

    # Replace strategy with one that gives invalid sid
    async def extract(r):
        return {"sub": "valid_user", "sid": "invalid_session"}

    mock_strategy.extract = extract

    dependency = get_current_user_dependency(auth)
    request = Request(scope={"type": "http"})

    with pytest.raises(CredentialsException, match="Session not found or expired"):
        await dependency(request)


@pytest.mark.asyncio
async def test_get_current_session_success(mock_strategy):
    auth = MockAuthManager(is_jwt=True, has_session=True)
    auth.strategy = mock_strategy

    dependency = get_current_session_dependency(auth)
    request = Request(scope={"type": "http"})

    session_id = await dependency(request)
    assert session_id == "valid_session"


@pytest.mark.asyncio
async def test_get_current_user_stateless_jwt(mock_strategy):
    # Setup for stateless JWT (no session store)
    auth = MockAuthManager(is_jwt=True, has_session=False)
    auth.strategy = mock_strategy

    # Strategy only provides 'sub'
    async def extract(r):
        return {"sub": "valid_user"}

    mock_strategy.extract = extract

    dependency = get_current_user_dependency(auth)
    request = Request(scope={"type": "http"})

    user = await dependency(request)
    assert user.id == "valid_user"
