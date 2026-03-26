from datetime import datetime, timedelta, timezone

import pytest

from fastauth.sessions.memory import MemorySessionStore


@pytest.mark.asyncio
async def test_memory_session_create():
    store = MemorySessionStore()
    user_id = "user_123"
    data = {"role": "admin"}

    session_id = await store.create(user_id, data)
    assert session_id is not None
    assert session_id in store.store
    assert store.store[session_id]["user_id"] == user_id
    assert store.store[session_id]["role"] == "admin"


@pytest.mark.asyncio
async def test_memory_session_get():
    store = MemorySessionStore()
    user_id = "user_123"
    data = {"role": "admin"}

    session_id = await store.create(user_id, data)
    session = await store.get(session_id)

    assert session is not None
    assert session["user_id"] == user_id
    assert session["role"] == "admin"


@pytest.mark.asyncio
async def test_memory_session_expiration():
    store = MemorySessionStore()
    user_id = "user_123"
    # Create session with 1 second TTL
    session_id = await store.create(user_id, {"role": "admin"}, ttl=1)

    # Check session exists
    session = await store.get(session_id)
    assert session is not None

    # Mock expiration by changing the expires_at timestamp
    store.store[session_id]["expires_at"] = datetime.now(timezone.utc) - timedelta(
        seconds=1
    )

    # Check session is expired and deleted
    expired_session = await store.get(session_id)
    assert expired_session is None
    assert session_id not in store.store


@pytest.mark.asyncio
async def test_memory_session_delete():
    store = MemorySessionStore()
    session_id = await store.create("user_123", {})

    await store.delete(session_id)
    assert session_id not in store.store


@pytest.mark.asyncio
async def test_memory_session_get_by_user():
    store = MemorySessionStore()
    user_id = "user_123"

    await store.create(user_id, {"session": 1})
    await store.create(user_id, {"session": 2})
    await store.create("other_user", {"session": 3})

    sessions = await store.get_by_user(user_id)
    assert len(sessions) == 2
    assert all(s["user_id"] == user_id for s in sessions)
