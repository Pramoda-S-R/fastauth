import uuid
from datetime import datetime, timezone

class MemorySessionStore:
    def __init__(self):
        self.store = {}

    async def create(self, user_id: str, data: dict) -> str:
        session_id = uuid.uuid4().hex
        self.store[session_id] = {"user_id": user_id, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc), **data}
        return session_id

    async def get(self, session_id: str) -> dict | None:
        return self.store.get(session_id)

    async def delete(self, session_id: str) -> None:
        if session_id in self.store:
            del self.store[session_id]

    async def refresh(self, session_id: str) -> None:
        if session_id in self.store:
            self.store[session_id]["updated_at"] = datetime.now(timezone.utc)