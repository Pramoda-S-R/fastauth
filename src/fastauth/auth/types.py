# fastauth/types.py
from datetime import datetime, timedelta
from typing import Any, Awaitable, Optional, Protocol, Union

EncodedT = Union[bytes, bytearray, memoryview]
DecodedT = Union[str, int, float]
EncodableT = Union[EncodedT, DecodedT]
KeyT = Union[bytes, str, memoryview]
ExpiryT = Union[int, timedelta]
AbsExpiryT = Union[int, datetime]
ResponseT = Union[Awaitable[Any], Any]


class Redis(Protocol):
    def set(
        self,
        name: KeyT,
        value: EncodableT,
        ex: Optional[ExpiryT] = None,
        px: Optional[ExpiryT] = None,
        nx: bool = False,
        xx: bool = False,
        keepttl: bool = False,
        get: bool = False,
        exat: Optional[AbsExpiryT] = None,
        pxat: Optional[AbsExpiryT] = None,
        ifeq: Optional[Union[bytes, str]] = None,
        ifne: Optional[Union[bytes, str]] = None,
        ifdeq: Optional[str] = None,  # hex digest of current value
        ifdne: Optional[str] = None,  # hex digest of current value
    ) -> ResponseT: ...
    def get(self, key: KeyT) -> ResponseT: ...
    def delete(self, *keys: KeyT) -> ResponseT: ...
    def expire(
        self,
        name: KeyT,
        time: ExpiryT,
        nx: bool = False,
        xx: bool = False,
        gt: bool = False,
        lt: bool = False,
    ) -> ResponseT: ...
