import pytest
from fastapi import Request, Response

from fastauth.strategies.opaque import OpaqueSessionStrategy


@pytest.fixture
def opaque_strategy():
    return OpaqueSessionStrategy(use_cookie=False)


@pytest.mark.asyncio
async def test_opaque_strategy_issue(opaque_strategy):
    response = Response()
    data = {"sid": "session_123"}
    tokens = await opaque_strategy.issue(response, data, ttl_seconds=3600)

    assert tokens is not None
    assert tokens["sid"] == "session_123"


@pytest.mark.asyncio
async def test_opaque_strategy_issue_no_sid(opaque_strategy):
    response = Response()
    with pytest.raises(ValueError, match="Session ID not found in claims"):
        await opaque_strategy.issue(response, {}, ttl_seconds=3600)


@pytest.mark.asyncio
async def test_opaque_strategy_extract_header(opaque_strategy):
    # Mock Request with Authorization header
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"authorization", b"Bearer session_123")],
            "path": "/test",
        }
    )

    claims = await opaque_strategy.extract(request)
    assert claims is not None
    assert claims["sid"] == "session_123"


@pytest.mark.asyncio
async def test_opaque_strategy_extract_cookie():
    strategy = OpaqueSessionStrategy(use_cookie=True, cookie_name="session_id")
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"cookie", b"session_id=session_123")],
            "path": "/test",
        }
    )

    claims = await strategy.extract(request)
    assert claims is not None
    assert claims["sid"] == "session_123"


@pytest.mark.asyncio
async def test_opaque_strategy_revoke():
    strategy = OpaqueSessionStrategy(use_cookie=True, cookie_name="session_id")
    response = Response()
    await strategy.revoke(response)

    # Check if delete-cookie is in headers
    cookie_header = response.headers.get("set-cookie")
    assert "session_id=;" in cookie_header or 'session_id=""' in cookie_header
    assert "Max-Age=0" in cookie_header
