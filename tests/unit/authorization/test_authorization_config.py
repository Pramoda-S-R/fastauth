import pytest
from pydantic import ValidationError

from fastauth import AuthConfig, RBACConfig, ABACConfig


def test_rbac_config_defaults():
    config = RBACConfig()
    assert config.enabled is False
    assert config.default_roles == []
    assert config.default_attributes == {}


def test_rbac_config_custom():
    config = RBACConfig(
        enabled=True,
        default_roles=["admin", "user"],
        default_attributes={"department": "default"},
    )
    assert config.enabled is True
    assert config.default_roles == ["admin", "user"]
    assert config.default_attributes == {"department": "default"}


def test_abac_config_defaults():
    config = ABACConfig()
    assert config.enabled is False


def test_abac_config_enabled():
    config = ABACConfig(enabled=True)
    assert config.enabled is True


def test_auth_config_rbac_defaults():
    config = AuthConfig(slug="testapp", secret="secret")
    assert config.rbac.enabled is False
    assert config.rbac.default_roles == []
    assert config.abac.enabled is False


def test_auth_config_rbac_enabled():
    config = AuthConfig(
        slug="testapp",
        secret="secret",
        rbac=RBACConfig(enabled=True, default_roles=["admin"]),
    )
    assert config.rbac.enabled is True
    assert config.rbac.default_roles == ["admin"]


def test_auth_config_abac_enabled():
    config = AuthConfig(
        slug="testapp",
        secret="secret",
        abac=ABACConfig(enabled=True),
    )
    assert config.abac.enabled is True


def test_auth_config_both_rbac_and_abac_enabled():
    config = AuthConfig(
        slug="testapp",
        secret="secret",
        rbac=RBACConfig(enabled=True),
        abac=ABACConfig(enabled=True),
    )
    assert config.rbac.enabled is True
    assert config.abac.enabled is True
