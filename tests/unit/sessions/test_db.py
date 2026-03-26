import json
from datetime import datetime, timedelta, timezone

import pytest

from fastauth.sessions.db import DBSessionStore


@pytest.mark.asyncio
async def test_db_session_create(mock_db_session, mock_session_model):
    store = DBSessionStore(mock_session_model, mock_db_session)
    user_id = "user_123"
    data = {"role": "admin"}

    session_id = await store.create(user_id, data)
    assert session_id is not None
    assert len(mock_db_session.added) == 1
    assert mock_db_session.committed is True

    session = mock_db_session.added[0]
    assert session.session_id == session_id
    assert session.user_id == user_id
    assert json.loads(session.data) == data


@pytest.mark.asyncio
async def test_db_session_get(mock_db_session, mock_session_model):
    store = DBSessionStore(mock_session_model, mock_db_session)
    user_id = "user_123"
    data = {"role": "admin"}

    session_id = await store.create(user_id, data)
    session = await store.get(session_id)

    assert session is not None
    assert session["role"] == "admin"


@pytest.mark.asyncio
async def test_db_session_expiration(mock_db_session, mock_session_model):
    store = DBSessionStore(mock_session_model, mock_db_session)
    user_id = "user_123"

    # Create session
    session_id = await store.create(user_id, {"role": "admin"}, ttl=3600)
    session = mock_db_session.added[0]

    # Mock expiration
    session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)

    # Check session is expired and deleted
    expired_session = await store.get(session_id)
    assert expired_session is None
    assert len(mock_db_session.added) == 0
    assert len(mock_db_session.deleted) == 1


@pytest.mark.asyncio
async def test_db_session_delete(mock_db_session, mock_session_model):
    store = DBSessionStore(mock_session_model, mock_db_session)
    session_id = await store.create("user_123", {})

    await store.delete(session_id)
    assert len(mock_db_session.added) == 0
    assert len(mock_db_session.deleted) == 1


@pytest.mark.asyncio
async def test_db_session_refresh(mock_db_session, mock_session_model):
    store = DBSessionStore(mock_session_model, mock_db_session)
    user_id = "user_123"

    # Simulate an hour old session getting refreshed
    session_id = await store.create(user_id, {"step": 1}, ttl=3600)
    session = mock_db_session.added[0]
    old_expires_at = session.expires_at

    # Refresh session
    await store.refresh(session_id, ttl=7200)
    assert session.expires_at > old_expires_at
    assert mock_db_session.committed is True
