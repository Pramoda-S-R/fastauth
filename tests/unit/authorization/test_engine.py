import pytest

from fastauth.authorization import (
    ABACPolicy,
    AuthorizationEngine,
    MemoryRoleStore,
    Permission,
    Role,
)


@pytest.mark.asyncio
async def test_authorization_engine_check_permission():
    store = MemoryRoleStore()
    role = Role(name="admin", permissions=[Permission.ADMIN])
    await store.create_role(role)
    await store.assign_role("user_123", "admin")

    engine = AuthorizationEngine(role_store=store)
    has_permission = await engine.check_permission("user_123", Permission.ADMIN)

    assert has_permission is True


@pytest.mark.asyncio
async def test_authorization_engine_check_permission_denied():
    store = MemoryRoleStore()
    role = Role(name="user", permissions=[Permission.READ])
    await store.create_role(role)
    await store.assign_role("user_123", "user")

    engine = AuthorizationEngine(role_store=store)
    has_permission = await engine.check_permission("user_123", Permission.ADMIN)

    assert has_permission is False


@pytest.mark.asyncio
async def test_authorization_engine_check_permission_no_roles():
    store = MemoryRoleStore()
    engine = AuthorizationEngine(role_store=store)

    has_permission = await engine.check_permission("user_123", Permission.ADMIN)

    assert has_permission is False


@pytest.mark.asyncio
async def test_authorization_engine_check_role():
    store = MemoryRoleStore()
    role = Role(name="admin", permissions=[Permission.ADMIN])
    await store.create_role(role)
    await store.assign_role("user_123", "admin")

    engine = AuthorizationEngine(role_store=store)
    has_role = await engine.check_role("user_123", "admin")

    assert has_role is True


@pytest.mark.asyncio
async def test_authorization_engine_check_role_not_found():
    store = MemoryRoleStore()
    role = Role(name="user", permissions=[Permission.READ])
    await store.create_role(role)
    await store.assign_role("user_123", "user")

    engine = AuthorizationEngine(role_store=store)
    has_role = await engine.check_role("user_123", "admin")

    assert has_role is False


@pytest.mark.asyncio
async def test_authorization_engine_get_user_permissions():
    store = MemoryRoleStore()
    role1 = Role(name="admin", permissions=[Permission.ADMIN, Permission.READ])
    role2 = Role(name="user", permissions=[Permission.READ])
    await store.create_role(role1)
    await store.create_role(role2)
    await store.assign_role("user_123", "admin")
    await store.assign_role("user_123", "user")

    engine = AuthorizationEngine(role_store=store)
    permissions = await engine.get_user_permissions("user_123")

    assert Permission.ADMIN in permissions
    assert Permission.READ in permissions


@pytest.mark.asyncio
async def test_abac_policy_match_action():
    policy = ABACPolicy(
        name="read_policy",
        effect="allow",
        actions=["read"],
        resources=["*"],
    )

    result = policy.evaluate({"action": "read", "resource": "document"})

    assert result is True


@pytest.mark.asyncio
async def test_abac_policy_no_match_action():
    policy = ABACPolicy(
        name="read_policy",
        effect="allow",
        actions=["read"],
        resources=["*"],
    )

    result = policy.evaluate({"action": "write", "resource": "document"})

    assert result is False


@pytest.mark.asyncio
async def test_abac_policy_wildcard_action():
    policy = ABACPolicy(
        name="wildcard_policy",
        effect="allow",
        actions=["*"],
        resources=["*"],
    )

    assert policy.evaluate({"action": "delete", "resource": "anything"}) is True


@pytest.mark.asyncio
async def test_abac_policy_match_resource():
    policy = ABACPolicy(
        name="doc_policy",
        effect="allow",
        actions=["read"],
        resources=["document"],
    )

    assert policy.evaluate({"action": "read", "resource": "document"}) is True
    assert policy.evaluate({"action": "read", "resource": "other"}) is False


@pytest.mark.asyncio
async def test_abac_policy_wildcard_resource():
    policy = ABACPolicy(
        name="prefix_policy",
        effect="allow",
        actions=["read"],
        resources=["admin:*"],
    )

    assert policy.evaluate({"action": "read", "resource": "admin:users"}) is True
    assert policy.evaluate({"action": "read", "resource": "user:profile"}) is False


@pytest.mark.asyncio
async def test_abac_policy_conditions():
    policy = ABACPolicy(
        name="dept_policy",
        effect="allow",
        actions=["read"],
        resources=["*"],
        conditions={"user.department": "engineering"},
    )

    assert (
        policy.evaluate(
            {
                "action": "read",
                "resource": "document",
                "user": {"department": "engineering"},
            }
        )
        is True
    )
    assert (
        policy.evaluate(
            {"action": "read", "resource": "document", "user": {"department": "sales"}}
        )
        is False
    )


@pytest.mark.asyncio
async def test_abac_policy_deny_effect():
    store = MemoryRoleStore()
    role = Role(name="user", permissions=[Permission.READ])
    await store.create_role(role)
    await store.assign_role("user_123", "user")

    deny_policy = ABACPolicy(
        name="deny_delete",
        effect="deny",
        actions=["delete"],
        resources=["*"],
    )

    engine = AuthorizationEngine(role_store=store, policies=[deny_policy])
    result = await engine.check_permission("user_123", Permission.DELETE)

    assert result is False


@pytest.mark.asyncio
async def test_abac_allow_overrides_deny():
    store = MemoryRoleStore()
    role = Role(name="admin", permissions=[Permission.DELETE])
    await store.create_role(role)
    await store.assign_role("user_123", "admin")

    deny_policy = ABACPolicy(
        name="deny_delete",
        effect="deny",
        actions=["delete"],
        resources=["*"],
    )
    allow_policy = ABACPolicy(
        name="allow_delete",
        effect="allow",
        actions=["delete"],
        resources=["admin:*"],
    )

    engine = AuthorizationEngine(role_store=store, policies=[deny_policy, allow_policy])
    result = await engine.check_permission(
        "user_123", Permission.DELETE, {"resource": "admin:settings"}
    )

    assert result is True


@pytest.mark.asyncio
async def test_authorization_engine_authorize_with_permission_and_role():
    store = MemoryRoleStore()
    role = Role(name="admin", permissions=[Permission.ADMIN])
    await store.create_role(role)
    await store.assign_role("user_123", "admin")

    engine = AuthorizationEngine(role_store=store)
    result = await engine.authorize(
        user_id="user_123", permission=Permission.ADMIN, role_name="admin"
    )

    assert result is True


@pytest.mark.asyncio
async def test_authorization_engine_authorize_fails_role():
    store = MemoryRoleStore()
    role_admin = Role(name="admin", permissions=[Permission.ADMIN])
    role_user = Role(name="user", permissions=[])
    await store.create_role(role_admin)
    await store.create_role(role_user)
    await store.assign_role("user_123", "user")

    engine = AuthorizationEngine(role_store=store)
    result = await engine.authorize(
        user_id="user_123", permission=Permission.ADMIN, role_name="admin"
    )

    assert result is False


@pytest.mark.asyncio
async def test_engine_add_policy():
    store = MemoryRoleStore()
    engine = AuthorizationEngine(role_store=store)

    policy = ABACPolicy(name="test", effect="allow", actions=["read"], resources=["*"])
    engine.add_policy(policy)

    assert len(engine.policies) == 1
    assert engine.policies[0].name == "test"


@pytest.mark.asyncio
async def test_engine_remove_policy():
    store = MemoryRoleStore()
    policy = ABACPolicy(name="test", effect="allow", actions=["read"], resources=["*"])
    engine = AuthorizationEngine(role_store=store, policies=[policy])

    engine.remove_policy("test")

    assert len(engine.policies) == 0
