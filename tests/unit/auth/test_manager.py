import pytest
from pydantic import BaseModel

from fastauth import AuthConfig, AuthManager


class TestSchema(BaseModel):
    __test__ = False
    id: str
    username: str
    password: str


class MockStrategy:
    def __init__(self, is_jwt=False):
        self.is_json_web_token = is_jwt


def test_auth_manager_init_success():
    config = AuthConfig(slug="auth", login_fields=["username"])
    # Should work with mock stores and matching schema
    AuthManager(
        config=config,
        user_store=None,  # We can pass None if we just test init
        session_store=None,
        strategy=MockStrategy(is_jwt=True),
        schema=TestSchema,
    )


def test_auth_manager_validation_error_missing_field():
    config = AuthConfig(slug="auth", login_fields=["email"])  # Missing in TestSchema
    with pytest.raises(
        ValueError, match="Login field 'email' is not in the user schema"
    ):
        AuthManager(
            config=config,
            user_store=None,
            session_store=None,
            strategy=MockStrategy(is_jwt=True),
            schema=TestSchema,
        )


def test_auth_manager_validation_stateless_opaque():
    config = AuthConfig(slug="auth", login_fields=["username"])
    # Opaque strategy requires session store
    with pytest.raises(ValueError, match="requires a session store"):
        AuthManager(
            config=config,
            user_store=None,
            session_store=None,  # Stateless
            strategy=MockStrategy(is_jwt=False),
            schema=TestSchema,
        )
