import json
import uuid
from datetime import datetime, timezone
from typing import Any

from ..auth.types import Redis


class RedisSessionStore:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def create(self, user_id: str, data: dict[str, Any]) -> str:
        session_id = uuid.uuid4().hex
        payload = {
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        payload.update(data)
        self.redis.set(session_id, json.dumps(payload))
        return session_id

    async def get(self, session_id: str) -> dict[str, Any] | None:
        payload = self.redis.get(session_id)
        if payload:
            return dict(json.loads(payload))
        return None

    async def delete(self, session_id: str) -> None:
        self.redis.delete(session_id)

    async def refresh(self, session_id: str) -> None:
        data = await self.get(session_id)
        if data:
            data.update({"updated_at": datetime.now(timezone.utc).isoformat()})
            await self.create(data["user_id"], data)
