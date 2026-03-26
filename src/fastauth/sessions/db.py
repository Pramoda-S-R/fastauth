import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from .base import SessionStore

if TYPE_CHECKING:
    from ..auth.types import DatabaseSession, SessionModel


class DBSessionStore(SessionStore):
    """Database-backed session store.

    Stores sessions in any SQL database. Requires a database model
    that follows the SessionModel protocol.

    Args:
        session_model: Database model class for sessions
        db_session: Database session client (e.g., SQLAlchemy session)
    """

    def __init__(self, session_model: type["SessionModel"], db_session: "DatabaseSession"):
        self.session_model = session_model
        self.db_session = db_session

    async def create(self, user_id: str, data: dict[str, Any], **kwargs) -> str:
        """Create a new session.

        Args:
            user_id: The user's ID
            data: Session data to store
            **kwargs: Optional 'ttl' for expiration time

        Returns:
            The created session_id
        """
        ttl = kwargs.get("ttl", 86400)  # default 24 hours
        session_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc)

        session = self.session_model(
            session_id=session_id,
            user_id=user_id,
            data=json.dumps(data),
            expires_at=now.replace(second=0, microsecond=0) + timedelta(seconds=ttl),
            created_at=now,
            updated_at=now,
        )

        self.db_session.add(session)
        self.db_session.commit()

        return session_id

    async def get(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session data by ID.

        Args:
            session_id: The session ID to look up

        Returns:
            Session data dict or None if not found/expired
        """
        session = (
            self.db_session.query(self.session_model)
            .filter(self.session_model.session_id == session_id)
            .first()
        )

        if not session:
            return None

        if session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            await self.delete(session_id)
            return None

        return json.loads(session.data)

    async def get_by_user(self, user_id: str) -> list[dict[str, Any]] | None:
        """Get all sessions for a user.

        Args:
            user_id: The user ID to find sessions for

        Returns:
            List of session data dicts
        """
        sessions = (
            self.db_session.query(self.session_model)
            .filter(
                self.session_model.user_id == user_id,
                self.session_model.expires_at > datetime.now(timezone.utc),
            )
            .all()
        )

        if not sessions:
            return None

        return [json.loads(s.data) for s in sessions]

    async def delete(self, session_id: str) -> None:
        """Delete a session.

        Args:
            session_id: The session ID to delete
        """
        session = (
            self.db_session.query(self.session_model)
            .filter(self.session_model.session_id == session_id)
            .first()
        )

        if session:
            self.db_session.delete(session)
            self.db_session.commit()

    async def refresh(self, session_id: str, **kwargs) -> None:
        """Refresh/update a session's expiration and data.

        Args:
            session_id: The session ID to refresh
            **kwargs: Optional 'ttl' to update expiration time
        """
        session = (
            self.db_session.query(self.session_model)
            .filter(self.session_model.session_id == session_id)
            .first()
        )

        if not session:
            return

        ttl = kwargs.get("ttl", 86400)
        now = datetime.now(timezone.utc)

        session.expires_at = now + timedelta(seconds=ttl)
        session.updated_at = now

        self.db_session.commit()
