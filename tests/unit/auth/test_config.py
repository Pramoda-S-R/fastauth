import pytest
from pydantic import BaseModel, ValidationError

from fastauth import AuthConfig


def test_auth_config_valid_slug():
    config = AuthConfig(slug="auth_v1")
    assert config.slug == "auth_v1"


def test_auth_config_invalid_slug():
    with pytest.raises(ValueError):
        AuthConfig(slug="Auth-V1")  # Must be lower snake case


def test_auth_config_missing_password_in_signup():
    class BadSignup(BaseModel):
        email: str

    with pytest.raises(ValidationError, match="Model must include 'password' field"):
        AuthConfig(slug="auth", signup_request=BadSignup)


def test_auth_config_missing_login_field_in_signup():
    class BadSignup(BaseModel):
        password: str
        phone: str

    with pytest.raises(
        ValueError, match="Model must include at least one of the login fields"
    ):
        AuthConfig(slug="auth", login_fields=["email"], signup_request=BadSignup)


def test_auth_config_valid_custom_requests():
    class GoodSignup(BaseModel):
        email: str
        password: str

    config = AuthConfig(slug="auth", login_fields=["email"], signup_request=GoodSignup)
    assert config.signup_request == GoodSignup
