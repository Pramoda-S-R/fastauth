# auth/manager.py
from typing import TYPE_CHECKING

from pydantic import BaseModel

from ..oauth.base import OAuthProvider
from ..authorization.base import RoleStore
from ..sessions.base import SessionStore
from ..strategies.base import AuthStrategy
from ..users.base import UserStore
from .config import AuthConfig

if TYPE_CHECKING:
    from ..authorization.engine import AuthorizationEngine


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
        role_store: RoleStore | None = None,
        authorization_engine: "AuthorizationEngine | None" = None,
    ):
        self.config = config
        self.user = user_store
        self.session = session_store
        self.strategy = strategy
        self.schema = schema
        self.oauth = oauth_provider
        self.role_store = role_store
        self.authorization = authorization_engine

        self.is_jwt_strategy = getattr(self.strategy, "is_json_web_token", False)
        self.is_stateless = self.session is None

        self.is_rbac_enabled = config.rbac.enabled
        self.is_abac_enabled = config.abac.enabled

        if not self.is_jwt_strategy and self.is_stateless:
            raise ValueError(
                f"Auth strategy `{self.strategy.__class__.__name__}` requires a session store"
            )

        if self.is_rbac_enabled and self.role_store is None:
            raise ValueError("RBAC is enabled but no role_store was provided")

        if self.is_abac_enabled and self.authorization is None:
            raise ValueError("ABAC is enabled but no authorization_engine was provided")

        for field in self.config.login_fields:
            if field not in self.schema.model_fields:
                raise ValueError(f"Login field '{field}' is not in the user schema")

        from fastauth.api.dependencies import (
            get_current_session_dependency,
            get_current_user_dependency,
        )
        from fastauth.api.router import build_auth_router

        self.current_user = get_current_user_dependency(self)
        self.current_session = get_current_session_dependency(self)

        if self.is_rbac_enabled and self.role_store:
            from fastauth.authorization.engine import AuthorizationEngine

            if self.authorization is None:
                self.authorization = AuthorizationEngine(
                    role_store=self.role_store, policies=[]
                )

        # always build router at the end
        self.router = build_auth_router(self)
