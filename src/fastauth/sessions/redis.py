import json
import uuid
from datetime import datetime, timezone
from typing import Any

from ..auth.types import Redis


class RedisSessionStore:
    def __init__(self, redis: Redis):
        self.redis = redis

    def _session_key(self, session_id: str) -> str:
        return f"session:{session_id}"

    def _user_index_key(self, user_id: str) -> str:
        return f"user_sessions:{user_id}"

    async def create(self, user_id: str, data: dict[str, Any], ttl: int) -> str:
        session_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat()

        payload = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": now,
            "updated_at": now,
            **data,
        }

        session_key = self._session_key(session_id)
        user_index_key = self._user_index_key(user_id)

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.set(session_key, json.dumps(payload), ex=ttl)
            pipe.sadd(user_index_key, session_id)
            await pipe.execute()

        return session_id

    async def get(self, session_id: str) -> dict[str, Any] | None:
        payload = await self.redis.get(self._session_key(session_id))
        if payload:
            return json.loads(payload)
        return None

    async def get_by_user(self, user_id: str) -> list[dict[str, Any]]:
        session_ids = await self.redis.smembers(self._user_index_key(user_id))
        if not session_ids:
            return []

        pipe = self.redis.pipeline()
        for sid in session_ids:
            pipe.get(self._session_key(sid))
        results = await pipe.execute()

        return [json.loads(p) for p in results if p]

    async def delete(self, session_id: str) -> None:
        session_key = self._session_key(session_id)

        payload = await self.redis.get(session_key)
        if not payload:
            return

        data = json.loads(payload)
        user_id = data.get("user_id")

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.delete(session_key)
            if user_id:
                pipe.srem(self._user_index_key(user_id), session_id)
            await pipe.execute()

    async def refresh(self, session_id: str, ttl: int) -> None:
        session_key = self._session_key(session_id)

        payload = await self.redis.get(session_key)
        if not payload:
            return

        data = json.loads(payload)
        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        await self.redis.set(session_key, json.dumps(data), ex=ttl)
