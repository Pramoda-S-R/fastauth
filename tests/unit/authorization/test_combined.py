import pytest

from fastauth.authorization import (
    ABACPolicy,
    AuthorizationEngine,
    MemoryRoleStore,
    Permission,
    Role,
    UserRole,
)


@pytest.mark.asyncio
async def test_rbac_with_abac_combined():
    """Test combined RBAC and ABAC authorization."""
    store = MemoryRoleStore()

    admin_role = Role(name="admin", permissions=[Permission.ADMIN, Permission.READ])
    user_role = Role(name="user", permissions=[Permission.READ])
    await store.create_role(admin_role)
    await store.create_role(user_role)

    await store.assign_role("user_123", "admin", {"department": "engineering"})
    await store.assign_role("user_456", "user", {"department": "sales"})

    admin_policy = ABACPolicy(
        name="admin_engineering",
        effect="allow",
        actions=["write"],
        resources=["engineering:*"],
        conditions={"role_attributes.department": "engineering"},
    )

    engine = AuthorizationEngine(role_store=store, policies=[admin_policy])

    has_admin_perm = await engine.check_permission("user_123", Permission.ADMIN)
    assert has_admin_perm is True

    has_engineering_write = await engine.check_permission(
        "user_123",
        Permission.WRITE,
        {
            "action": "write",
            "resource": "engineering:api",
            "role_attributes": {"department": "engineering"},
        },
    )
    assert has_engineering_write is True

    has_user_perm = await engine.check_permission("user_456", Permission.ADMIN)
    assert has_user_perm is False


@pytest.mark.asyncio
async def test_abac_with_multiple_conditions():
    """Test ABAC with multiple conditions."""
    store = MemoryRoleStore()
    role = Role(name="premium", permissions=[Permission.READ])
    await store.create_role(role)
    await store.assign_role(
        "user_123", "premium", {"tier": "premium", "verified": True}
    )

    policy = ABACPolicy(
        name="premium_verified",
        effect="allow",
        actions=["delete"],
        resources=["*"],
        conditions={
            "user_attributes.tier": "premium",
            "user_attributes.verified": True,
        },
    )

    engine = AuthorizationEngine(role_store=store, policies=[policy])

    result = await engine.check_permission(
        "user_123",
        Permission.DELETE,
        {
            "action": "delete",
            "resource": "any",
            "user_attributes": {"tier": "premium", "verified": True},
        },
    )
    assert result is True

    result_fail = await engine.check_permission(
        "user_123",
        Permission.DELETE,
        {
            "action": "delete",
            "resource": "any",
            "user_attributes": {"tier": "premium", "verified": False},
        },
    )
    assert result_fail is False


@pytest.mark.asyncio
async def test_deny_policy_blocks_allow():
    """Test that deny policy takes precedence."""
    store = MemoryRoleStore()
    role = Role(name="contractor", permissions=[Permission.READ, Permission.WRITE])
    await store.create_role(role)
    await store.assign_role("user_123", "contractor")

    deny_policy = ABACPolicy(
        name="deny_contractor_write",
        effect="deny",
        actions=["write"],
        resources=["admin:*"],
    )

    allow_policy = ABACPolicy(
        name="allow_write",
        effect="allow",
        actions=["write"],
        resources=["*"],
    )

    engine = AuthorizationEngine(role_store=store, policies=[deny_policy, allow_policy])

    result = await engine.check_permission(
        "user_123", Permission.WRITE, {"action": "write", "resource": "admin:config"}
    )
    assert result is False


@pytest.mark.asyncio
async def test_wildcard_matching():
    """Test wildcard matching in policies."""
    policy = ABACPolicy(
        name="wildcard_all",
        effect="allow",
        actions=["*"],
        resources=["*"],
    )

    assert policy.evaluate({"action": "read", "resource": "anything"}) is True
    assert policy.evaluate({"action": "write", "resource": "something"}) is True
    assert policy.evaluate({"action": "delete", "resource": "important"}) is True


@pytest.mark.asyncio
async def test_prefix_matching():
    """Test prefix wildcard matching."""
    policy = ABACPolicy(
        name="api_prefix",
        effect="allow",
        actions=["*"],
        resources=["api:v1:*"],
    )

    assert policy.evaluate({"action": "read", "resource": "api:v1:users"}) is True
    assert policy.evaluate({"action": "write", "resource": "api:v1:posts"}) is True
    assert policy.evaluate({"action": "read", "resource": "api:v2:data"}) is False
    assert policy.evaluate({"action": "read", "resource": "other:path"}) is False


@pytest.mark.asyncio
async def test_role_with_attributes():
    """Test role assignments with attributes."""
    store = MemoryRoleStore()
    role = Role(
        name="manager",
        permissions=[Permission.READ, Permission.WRITE],
        attributes={"department": "sales", "level": 3},
    )
    await store.create_role(role)
    await store.assign_role("user_123", "manager", {"team_size": 10})

    user_roles = await store.get_user_roles("user_123")
    assert len(user_roles) == 1
    assert user_roles[0].role_name == "manager"
    assert user_roles[0].attributes == {"team_size": 10}

    stored_role = await store.get_role("manager")
    assert stored_role.attributes == {"department": "sales", "level": 3}


@pytest.mark.asyncio
async def test_multiple_policies_evaluation():
    """Test multiple policies are evaluated correctly."""
    store = MemoryRoleStore()
    role = Role(name="user", permissions=[Permission.READ])
    await store.create_role(role)
    await store.assign_role("user_123", "user")

    policy1 = ABACPolicy(
        name="p1", effect="allow", actions=["read"], resources=["doc1"]
    )
    policy2 = ABACPolicy(
        name="p2", effect="allow", actions=["read"], resources=["doc2"]
    )
    policy3 = ABACPolicy(
        name="p3", effect="deny", actions=["read"], resources=["secret"]
    )

    engine = AuthorizationEngine(role_store=store, policies=[policy1, policy2, policy3])

    assert (
        await engine.check_permission(
            "user_123", Permission.READ, {"action": "read", "resource": "doc1"}
        )
        is True
    )
    assert (
        await engine.check_permission(
            "user_123", Permission.READ, {"action": "read", "resource": "doc2"}
        )
        is True
    )
    assert (
        await engine.check_permission(
            "user_123", Permission.READ, {"action": "read", "resource": "secret"}
        )
        is False
    )


@pytest.mark.asyncio
async def test_empty_conditions_match_any():
    """Test that empty conditions match any context."""
    policy = ABACPolicy(
        name="no_conditions",
        effect="allow",
        actions=["read"],
        resources=["*"],
        conditions={},
    )

    assert policy.evaluate({"action": "read", "resource": "anything"}) is True
    assert policy.evaluate({"action": "read", "resource": "something"}) is True


@pytest.mark.asyncio
async def test_nested_condition_evaluation():
    """Test nested attribute conditions."""
    policy = ABACPolicy(
        name="nested",
        effect="allow",
        actions=["access"],
        resources=["*"],
        conditions={"user.metadata.preferences.theme": "dark"},
    )

    assert (
        policy.evaluate(
            {
                "action": "access",
                "resource": "settings",
                "user": {"metadata": {"preferences": {"theme": "dark"}}},
            }
        )
        is True
    )

    assert (
        policy.evaluate(
            {
                "action": "access",
                "resource": "settings",
                "user": {"metadata": {"preferences": {"theme": "light"}}},
            }
        )
        is False
    )
