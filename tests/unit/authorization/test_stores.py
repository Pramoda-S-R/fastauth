import pytest

from fastauth.authorization import MemoryRoleStore, Permission, Role


@pytest.mark.asyncio
async def test_memory_role_store_create_role():
    store = MemoryRoleStore()
    role = Role(name="admin", permissions=[Permission.ADMIN])

    created = await store.create_role(role)

    assert created.name == "admin"
    assert created.permissions == [Permission.ADMIN]


@pytest.mark.asyncio
async def test_memory_role_store_get_role():
    store = MemoryRoleStore()
    role = Role(name="user", permissions=[Permission.READ])
    await store.create_role(role)

    found = await store.get_role("user")

    assert found is not None
    assert found.name == "user"
    assert Permission.READ in found.permissions


@pytest.mark.asyncio
async def test_memory_role_store_get_role_not_found():
    store = MemoryRoleStore()

    found = await store.get_role("nonexistent")

    assert found is None


@pytest.mark.asyncio
async def test_memory_role_store_delete_role():
    store = MemoryRoleStore()
    role = Role(name="admin", permissions=[Permission.ADMIN])
    await store.create_role(role)

    await store.delete_role("admin")

    assert await store.get_role("admin") is None


@pytest.mark.asyncio
async def test_memory_role_store_assign_role():
    store = MemoryRoleStore()
    role = Role(name="admin", permissions=[Permission.ADMIN])
    await store.create_role(role)

    user_role = await store.assign_role(
        "user_123", "admin", {"department": "engineering"}
    )

    assert user_role.user_id == "user_123"
    assert user_role.role_name == "admin"
    assert user_role.attributes == {"department": "engineering"}


@pytest.mark.asyncio
async def test_memory_role_store_assign_role_not_exists():
    store = MemoryRoleStore()

    with pytest.raises(ValueError, match="Role 'admin' does not exist"):
        await store.assign_role("user_123", "admin")


@pytest.mark.asyncio
async def test_memory_role_store_unassign_role():
    store = MemoryRoleStore()
    role = Role(name="admin", permissions=[Permission.ADMIN])
    await store.create_role(role)
    await store.assign_role("user_123", "admin")

    await store.unassign_role("user_123", "admin")

    user_roles = await store.get_user_roles("user_123")
    assert len(user_roles) == 0


@pytest.mark.asyncio
async def test_memory_role_store_get_user_roles():
    store = MemoryRoleStore()
    role1 = Role(name="admin", permissions=[Permission.ADMIN])
    role2 = Role(name="user", permissions=[Permission.READ])
    await store.create_role(role1)
    await store.create_role(role2)
    await store.assign_role("user_123", "admin")
    await store.assign_role("user_123", "user")

    user_roles = await store.get_user_roles("user_123")

    assert len(user_roles) == 2
    role_names = {ur.role_name for ur in user_roles}
    assert "admin" in role_names
    assert "user" in role_names


@pytest.mark.asyncio
async def test_memory_role_store_get_all_assignments():
    store = MemoryRoleStore()
    role1 = Role(name="admin", permissions=[Permission.ADMIN])
    role2 = Role(name="user", permissions=[Permission.READ])
    await store.create_role(role1)
    await store.create_role(role2)
    await store.assign_role("user_1", "admin")
    await store.assign_role("user_2", "user")

    assignments = await store.get_all_assignments()

    assert len(assignments) == 2


@pytest.mark.asyncio
async def test_memory_role_store_default_roles():
    default_roles = [
        Role(name="admin", permissions=[Permission.ADMIN]),
        Role(name="user", permissions=[Permission.READ]),
    ]
    store = MemoryRoleStore(default_roles=default_roles)

    admin = await store.get_role("admin")
    user = await store.get_role("user")

    assert admin is not None
    assert user is not None


@pytest.mark.asyncio
async def test_memory_role_store_update_existing_assignment():
    store = MemoryRoleStore()
    role = Role(name="admin", permissions=[Permission.ADMIN])
    await store.create_role(role)
    await store.assign_role("user_123", "admin", {"dept": "A"})
    await store.assign_role("user_123", "admin", {"dept": "B"})

    user_roles = await store.get_user_roles("user_123")

    assert len(user_roles) == 1
    assert user_roles[0].attributes == {"dept": "B"}
