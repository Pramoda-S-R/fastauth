"""
Redis session store implementation.

Stores sessions in Redis with automatic expiration via TTL.
Requires a Redis client that implements the Redis protocol.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..auth.types import Redis


class RedisSessionStore:
    """Redis-backed session storage.

    Stores sessions as JSON in Redis with automatic expiration.
    Supports both sync and async Redis clients.
    """

    def __init__(self, redis: "Redis", key_prefix: str = "session:"):
        """Initialize the Redis session store.

        Args:
            redis: Redis client instance
            key_prefix: Prefix for session keys (default: "session:")
        """
        self.redis = redis
        self.key_prefix = key_prefix

    def _make_key(self, session_id: str) -> str:
        """Generate a Redis key for a session."""
        return f"{self.key_prefix}{session_id}"

    async def create(self, user_id: str, data: dict[str, Any], **kwargs) -> str:
        """Create a new session.

        Args:
            user_id: The user's ID
            data: Session data to store
            **kwargs: Required 'ttl' for Redis expiration

        Returns:
            The created session_id
        """
        session_id = uuid.uuid4().hex
        ttl = kwargs.get("ttl")

        if not ttl:
            raise ValueError("Redis session store requires 'ttl' parameter")

        payload = {
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        payload.update(data)

        key = self._make_key(session_id)
        await self.redis.set(key, json.dumps(payload), ex=ttl)
        return session_id

    async def get(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session data by ID.

        Args:
            session_id: The session ID to look up

        Returns:
            Session data dict or None if not found
        """
        key = self._make_key(session_id)
        payload = await self.redis.get(key)

        if payload:
            return dict(json.loads(payload))
        return None

    async def get_by_user(self, user_id: str) -> list[dict[str, Any]] | None:
        """Get all sessions for a user.

        **IMPORTANT: This method is not implemented for Redis session store.**
        Note: This is expensive in Redis as it requires scanning all keys.
        Consider using a separate index (e.g., SET of session IDs per user) for production.

        Args:
            user_id: The user ID to find sessions for

        Returns:
            List of session data dicts (may include expired sessions)
        """
        raise NotImplementedError("Redis session store does not support get_by_user")

    async def delete(self, session_id: str) -> None:
        """Delete a session.

        Args:
            session_id: The session ID to delete
        """
        key = self._make_key(session_id)
        await self.redis.delete(key)

    async def refresh(self, session_id: str, **kwargs) -> None:
        """Refresh/update a session's expiration and data.

        Args:
            session_id: The session ID to refresh
            **kwargs: Required 'ttl' to update expiration time
        """
        ttl = kwargs.get("ttl")
        if not ttl:
            raise ValueError("Redis session refresh requires 'ttl' parameter")

        data = await self.get(session_id)
        if data:
            data["updated_at"] = datetime.now(timezone.utc).isoformat()
            key = self._make_key(session_id)
            await self.redis.set(key, json.dumps(data), ex=ttl)
