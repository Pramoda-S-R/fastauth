# auth/manager.py
from pydantic import BaseModel

from ..oauth.base import OAuthProvider
from ..sessions.base import SessionStore
from ..tokens.base import AuthStrategy
from ..users.base import UserStore

from .config import AuthConfig


class AuthManager:
    def __init__(
        self,
        *,
        config: AuthConfig,
        user_store: UserStore,
        session_store: SessionStore | None = None,
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