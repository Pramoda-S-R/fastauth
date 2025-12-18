# auth/manager.py
from fastauth.users.base import UserStore
from fastauth.sessions.base import SessionStore
from fastauth.tokens.base import AuthStrategy
from fastauth.oauth.base import OAuthProvider
from enum import Enum
from .config import AuthConfig

from pydantic import BaseModel

class AuthManager:
    def __init__(
        self,
        *,
        config: AuthConfig,
        user_store: UserStore,
        session_store: SessionStore,
        strategy: AuthStrategy,
        schema: type[BaseModel],
        oauth_provider: OAuthProvider | None = None,
    ):
        self.config = config
        self.user = user_store
        self.session = session_store
        self.strategy = strategy
        self.schema = schema
        self.oauth = oauth_provider

        for field in self.config.login_fields:
            if field not in self.schema.model_fields:
                 raise ValueError(f"Login field '{field}' is not in the user schema")

        from fastauth.api.router import build_auth_router
        self.router = build_auth_router(self)