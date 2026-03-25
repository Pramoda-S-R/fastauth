"""
In-memory session store implementation.

Stores sessions in a simple in-memory dictionary.
Note: Sessions are not persisted and will be lost on restart.
Best for development/testing or single-instance deployments.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any


class MemorySessionStore:
    """In-memory session storage with expiration support.

    Stores session data in memory with optional TTL-based expiration.
    Automatically cleans up expired sessions on access.
    """

    def __init__(self, default_ttl: int = 86400):
        """Initialize the session store.

        Args:
            default_ttl: Default time-to-live in seconds (default: 24 hours)
        """
        self.store: dict[str, dict[str, Any]] = {}
        self.default_ttl = default_ttl

    async def create(self, user_id: str, data: dict[str, Any], **kwargs) -> str:
        """Create a new session.

        Args:
            user_id: The user's ID
            data: Session data to store
            **kwargs: Optional 'ttl' for custom expiration

        Returns:
            The created session_id
        """
        session_id = uuid.uuid4().hex
        ttl = kwargs.get("ttl", self.default_ttl)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)

        self.store[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "expires_at": expires_at,
            **data,
        }
        return session_id

    async def get(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session data by ID.

        Checks expiration and deletes expired sessions.

        Args:
            session_id: The session ID to look up

        Returns:
            Session data dict or None if not found/expired
        """
        session = self.store.get(session_id)
        if not session:
            return None

        # Check expiration
        expires_at = session.get("expires_at")
        if expires_at and expires_at < datetime.now(timezone.utc):
            await self.delete(session_id)
            return None

        return session

    async def get_by_user(self, user_id: str) -> list[dict[str, Any]] | None:
        """Get all non-expired sessions for a user.

        Args:
            user_id: The user ID to find sessions for

        Returns:
            List of session data dicts
        """
        now = datetime.now(timezone.utc)
        sessions = [
            session
            for session in self.store.values()
            if session["user_id"] == user_id
            and (not session.get("expires_at") or session["expires_at"] >= now)
        ]
        return sessions if sessions else None

    async def delete(self, session_id: str) -> None:
        """Delete a session.

        Args:
            session_id: The session ID to delete
        """
        if session_id in self.store:
            del self.store[session_id]

    async def refresh(self, session_id: str, **kwargs) -> None:
        """Refresh/update a session's expiration and data.

        Args:
            session_id: The session ID to refresh
            **kwargs: Optional 'ttl' to update expiration time
        """
        if session_id not in self.store:
            return

        ttl = kwargs.get("ttl", self.default_ttl)
        now = datetime.now(timezone.utc)

        self.store[session_id]["updated_at"] = now
        self.store[session_id]["expires_at"] = now + timedelta(seconds=ttl)
