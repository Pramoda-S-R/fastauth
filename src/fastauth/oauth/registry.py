# oauth/registry.py
from typing import Dict, Type

from .base import OAuthProvider

_PROVIDERS: Dict[str, Type[OAuthProvider]] = {}


def register_provider(provider: Type[OAuthProvider]) -> None:
    _PROVIDERS[provider.name] = provider


def get_provider(name: str, **kwargs) -> OAuthProvider:
    provider_cls = _PROVIDERS[name]
    return provider_cls(**kwargs)
