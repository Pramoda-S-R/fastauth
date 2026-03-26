import json

import pytest

from fastauth.sessions.redis import RedisSessionStore


@pytest.mark.asyncio
async def test_redis_session_create(mock_redis):
    store = RedisSessionStore(mock_redis)
    user_id = "user_123"
    data = {"role": "admin"}

    # TTL is required for RedisSessionStore
    with pytest.raises(ValueError):
        await store.create(user_id, data)

    session_id = await store.create(user_id, data, ttl=3600)

    assert session_id is not None
    key = store._make_key(session_id)
    raw_payload = await mock_redis.get(key)

    assert raw_payload is not None
    payload = json.loads(raw_payload)
    assert payload["user_id"] == user_id
    assert payload["role"] == "admin"


@pytest.mark.asyncio
async def test_redis_session_get(mock_redis):
    store = RedisSessionStore(mock_redis)
    user_id = "user_123"
    data = {"role": "admin"}

    session_id = await store.create(user_id, data, ttl=3600)
    session = await store.get(session_id)

    assert session is not None
    assert session["user_id"] == user_id
    assert session["role"] == "admin"


@pytest.mark.asyncio
async def test_redis_session_delete(mock_redis):
    store = RedisSessionStore(mock_redis)
    session_id = await store.create("user_123", {}, ttl=3600)

    await store.delete(session_id)
    assert await mock_redis.get(store._make_key(session_id)) is None


@pytest.mark.asyncio
async def test_redis_session_refresh(mock_redis):
    store = RedisSessionStore(mock_redis)
    user_id = "user_123"

    session_id = await store.create(user_id, {"step": 1}, ttl=3600)
    old_payload = json.loads(await mock_redis.get(store._make_key(session_id)))

    # Refresh session
    await store.refresh(session_id, ttl=7200)
    new_payload = json.loads(await mock_redis.get(store._make_key(session_id)))

    assert new_payload["updated_at"] != old_payload["updated_at"]
    assert new_payload["step"] == 1
