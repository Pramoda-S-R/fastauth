from typing import Any, Optional

import pytest
from pydantic import BaseModel, ConfigDict

# -----------------
# Mock Models
# -----------------


class MockUserSchema(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    password: str
    model_config = ConfigDict(extra="allow", from_attributes=True)


class MockSessionModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    # Class attributes to avoid AttributeError in 'Model.column' access
    session_id = None
    user_id = None
    data = None
    expires_at = None
    created_at = None
    updated_at = None


# -----------------
# Mock Clients
# -----------------


class MockRedis:
    def __init__(self):
        self.data = {}

    async def get(self, key: str) -> Optional[bytes]:
        return self.data.get(key)

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        self.data[key] = value
        return True

    async def delete(self, key: str) -> int:
        if key in self.data:
            del self.data[key]
            return 1
        return 0


class MockDatabaseQuery:
    def __init__(self, data: list):
        self.data = data

    def filter(self, *expressions: Any) -> "MockDatabaseQuery":
        # Simplified filter logic for testing
        return self

    def first(self) -> Any:
        return self.data[0] if self.data else None

    def all(self) -> list[Any]:
        return self.data


class MockDatabaseSession:
    def __init__(self):
        self.added = []
        self.deleted = []
        self.committed = False

    def query(self, model: type[Any]) -> MockDatabaseQuery:
        return MockDatabaseQuery(self.added)

    def add(self, instance: Any) -> None:
        self.added.append(instance)

    def delete(self, instance: Any) -> None:
        self.deleted.append(instance)
        if instance in self.added:
            self.added.remove(instance)

    def commit(self) -> None:
        self.committed = True


# -----------------
# Fixtures
# -----------------


@pytest.fixture
def mock_redis():
    return MockRedis()


@pytest.fixture
def mock_db_session():
    return MockDatabaseSession()


@pytest.fixture
def mock_session_model():
    return MockSessionModel
