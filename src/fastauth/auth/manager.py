# auth/manager.py
from fastapi import APIRouter, Depends
from .config import AuthConfig

class AuthManager:
    def __init__(
        self,
        *,
        config: AuthConfig,
        session_store: SessionStore,
        strategy: AuthStrategy,
        role_enum: type[Enum],
        oauth_provider: OAuthProvider | None = None,
    ):
        self.config = config
        self.store = session_store
        self.strategy = strategy
        self.roles = role_enum
        self.oauth = oauth_provider

        self.router = build_auth_router(self)