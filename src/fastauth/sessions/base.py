"""
Session store protocol definitions.

Defines the interface for session storage backends (memory, Redis, DB, etc.)
"""

from typing import Any, Protocol


class SessionStore(Protocol):
    """Protocol for session storage implementations.

    Implementations must provide async methods for:
    - Creating new sessions
    - Retrieving sessions by ID
    - Getting all sessions for a user
    - Deleting sessions
    - Refreshing/updating sessions

    Methods:
        create: Create a new session
            Args:
                user_id: The user's ID
                data: Session data to store
                **kwargs: Additional args (commonly 'ttl' for expiration)
            Returns:
                The created session ID
        get: Retrieve a session by ID
            Args:
                session_id: The session ID to look up
            Returns:
                Session data dict or None if not found
        get_by_user: Get all sessions for a user
            Args:
                user_id: The user ID to find sessions for
            Returns:
                List of session data dicts, or None if none exist
        delete: Delete a session
            Args:
                session_id: The session ID to delete
        refresh: Refresh/update a session
            Args:
                session_id: The session ID to refresh
                **kwargs: Optional updates (commonly 'ttl')
    """

    async def create(self, user_id: str, data: dict[str, Any], **kwargs: Any) -> str:
        """Create a new session for a user.

        Args:
            user_id: The user's ID
            data: Session data to store
            **kwargs: Additional args (commonly 'ttl' for expiration)

        Returns:
            The created session ID
        """
        ...

    async def get(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session data by ID.

        Args:
            session_id: The session ID to look up

        Returns:
            Session data dict or None if not found
        """
        ...

    async def get_by_user(self, user_id: str) -> list[dict[str, Any]] | None:
        """Get all sessions for a user.

        Args:
            user_id: The user ID to find sessions for

        Returns:
            List of session data dicts, or None if none exist
        """
        ...

    async def delete(self, session_id: str) -> None:
        """Delete a session.

        Args:
            session_id: The session ID to delete
        """
        ...

    async def refresh(self, session_id: str, **kwargs: Any) -> None:
        """Refresh/update a session's expiration and data.

        Args:
            session_id: The session ID to refresh
            **kwargs: Optional updates (commonly 'ttl')
        """
        ...
