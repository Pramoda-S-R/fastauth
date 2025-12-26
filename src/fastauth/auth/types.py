from datetime import timedelta
from typing import Optional, Protocol, Set, Union, runtime_checkable

# -----------------
# Basic Types
# -----------------

KeyT = Union[str, bytes]
ValueT = Union[str, bytes]
ExpiryT = Union[int, timedelta]


# -----------------
# Pipeline Protocol
# -----------------


@runtime_checkable
class Pipeline(Protocol):
    # async context manager
    async def __aenter__(self) -> "Pipeline": ...
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None: ...

    # commands used
    def set(
        self,
        key: KeyT,
        value: ValueT,
        *,
        ex: Optional[ExpiryT] = None,
    ) -> "Pipeline": ...

    def sadd(self, key: KeyT, value: ValueT) -> "Pipeline": ...
    def srem(self, key: KeyT, value: ValueT) -> "Pipeline": ...
    def delete(self, key: KeyT) -> "Pipeline": ...

    async def execute(self) -> list[object]: ...


# -----------------
# Redis Protocol
# -----------------


@runtime_checkable
class Redis(Protocol):
    async def get(self, key: KeyT) -> Optional[bytes]: ...

    async def set(
        self,
        key: KeyT,
        value: ValueT,
        *,
        ex: Optional[ExpiryT] = None,
    ) -> bool: ...

    async def delete(self, key: KeyT) -> int: ...

    async def sadd(self, key: KeyT, value: ValueT) -> int: ...
    async def srem(self, key: KeyT, value: ValueT) -> int: ...
    async def smembers(self, key: KeyT) -> Set[bytes]: ...

    def pipeline(self, transaction: bool = True) -> Pipeline: ...
