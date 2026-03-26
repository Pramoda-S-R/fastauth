import pytest
from fastapi import Request, Response

from fastauth.exceptions import TokenException
from fastauth.strategies.jwt import JWTStrategy


@pytest.fixture
def jwt_strategy():
    return JWTStrategy(secret="test_secret", use_cookie=False)


@pytest.mark.asyncio
async def test_jwt_strategy_issue(jwt_strategy):
    response = Response()
    data = {"sub": "user_123", "sid": "session_123"}
    tokens = await jwt_strategy.issue(response, data, ttl_seconds=3600)

    assert tokens is not None
    assert "access_token" in tokens
    assert "refresh_token" in tokens


@pytest.mark.asyncio
async def test_jwt_strategy_verify(jwt_strategy):
    response = Response()
    data = {"sub": "user_123", "sid": "session_123"}
    tokens = await jwt_strategy.issue(response, data, ttl_seconds=3600)

    claims = await jwt_strategy.verify(tokens["access_token"])
    assert claims["sub"] == "user_123"
    assert claims["sid"] == "session_123"


@pytest.mark.asyncio
async def test_jwt_strategy_extract_header(jwt_strategy):
    # Mock Request with Authorization header
    response = Response()
    data = {"sub": "user_123", "sid": "session_123"}
    tokens = await jwt_strategy.issue(response, data, ttl_seconds=3600)

    request = Request(
        scope={
            "type": "http",
            "headers": [
                (b"authorization", f"Bearer {tokens['access_token']}".encode())
            ],
            "path": "/test",
        }
    )

    claims = await jwt_strategy.extract(request)
    assert claims is not None
    assert claims["sub"] == "user_123"


@pytest.mark.asyncio
async def test_jwt_strategy_extract_cookie():
    strategy = JWTStrategy(
        secret="test_secret", use_cookie=True, cookie_name="test_cookie"
    )
    response = Response()
    data = {"sub": "user_123", "sid": "session_123"}

    # This will set the cookie in the response
    await strategy.issue(response, data, ttl_seconds=3600)

    # Get the cookie from the response
    cookie_header = response.headers.get("set-cookie")
    token = cookie_header.split("=")[1].split(";")[0]

    request = Request(
        scope={
            "type": "http",
            "headers": [(b"cookie", f"test_cookie={token}".encode())],
            "path": "/test",
        }
    )

    claims = await strategy.extract(request)
    assert claims is not None
    assert claims["sub"] == "user_123"


@pytest.mark.asyncio
async def test_jwt_strategy_invalid_token(jwt_strategy):
    with pytest.raises(TokenException):
        await jwt_strategy.verify("invalid.token.here")
