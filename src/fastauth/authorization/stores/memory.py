"""
In-memory role store implementation.

Stores roles and role assignments in memory.
Note: Data is not persisted and will be lost on restart.
Best for development/testing.
"""

from typing import Any

from ..base import Role, RoleStore, UserRole


class MemoryRoleStore:
    """In-memory role storage."""

    def __init__(self, default_roles: list[Role] | None = None):
        """Initialize the role store.

        Args:
            default_roles: Optional list of roles to create on initialization
        """
        self.roles: dict[str, Role] = {}
        self.user_roles: dict[str, list[UserRole]] = {}  # user_id -> list of UserRole

        if default_roles:
            for role in default_roles:
                self.roles[role.name] = role

    async def create_role(self, role: Role) -> Role:
        """Create a new role.

        Args:
            role: Role object to create

        Returns:
            The created role
        """
        self.roles[role.name] = role
        return role

    async def get_role(self, role_name: str) -> Role | None:
        """Get a role by name.

        Args:
            role_name: The role name

        Returns:
            Role object or None if not found
        """
        return self.roles.get(role_name)

    async def delete_role(self, role_name: str) -> None:
        """Delete a role.

        Args:
            role_name: The role name
        """
        if role_name in self.roles:
            del self.roles[role_name]

        for user_id in self.user_roles:
            self.user_roles[user_id] = [
                ur for ur in self.user_roles[user_id] if ur.role_name != role_name
            ]

    async def assign_role(
        self, user_id: str, role_name: str, attributes: dict[str, Any] | None = None
    ) -> UserRole:
        """Assign a role to a user.

        Args:
            user_id: The user ID
            role_name: The role name
            attributes: Optional role attributes

        Returns:
            The created UserRole assignment
        """
        if role_name not in self.roles:
            raise ValueError(f"Role '{role_name}' does not exist")

        user_role = UserRole(user_id, role_name, attributes)

        if user_id not in self.user_roles:
            self.user_roles[user_id] = []

        existing = [ur for ur in self.user_roles[user_id] if ur.role_name == role_name]
        if existing:
            self.user_roles[user_id] = [
                ur for ur in self.user_roles[user_id] if ur.role_name != role_name
            ]

        self.user_roles[user_id].append(user_role)
        return user_role

    async def unassign_role(self, user_id: str, role_name: str) -> None:
        """Remove a role from a user.

        Args:
            user_id: The user ID
            role_name: The role name
        """
        if user_id in self.user_roles:
            self.user_roles[user_id] = [
                ur for ur in self.user_roles[user_id] if ur.role_name != role_name
            ]

    async def get_user_roles(self, user_id: str) -> list[UserRole]:
        """Get all roles for a user.

        Args:
            user_id: The user ID

        Returns:
            List of UserRole objects
        """
        return self.user_roles.get(user_id, [])

    async def get_all_assignments(self) -> list[UserRole]:
        """Get all role assignments.

        Returns:
            List of all UserRole objects
        """
        all_assignments = []
        for roles in self.user_roles.values():
            all_assignments.extend(roles)
        return all_assignments
