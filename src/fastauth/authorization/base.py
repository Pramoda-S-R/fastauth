"""
RBAC and ABAC base protocol definitions.

Defines the interfaces for role-based and attribute-based access control.
"""

from typing import Any, Protocol, TypeVar
from enum import Enum


class Permission(str, Enum):
    """Base permission type."""

    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    ADMIN = "admin"


class Role:
    """Represents a role with permissions."""

    def __init__(
        self,
        name: str,
        permissions: list[Permission],
        attributes: dict[str, Any] | None = None,
    ):
        self.name = name
        self.permissions = permissions
        self.attributes = attributes or {}

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions

    def __repr__(self) -> str:
        return f"Role(name={self.name!r}, permissions={self.permissions})"


class UserRole:
    """Represents a role assignment to a user."""

    def __init__(
        self, user_id: str, role_name: str, attributes: dict[str, Any] | None = None
    ):
        self.user_id = user_id
        self.role_name = role_name
        self.attributes = attributes or {}

    def __repr__(self) -> str:
        return f"UserRole(user_id={self.user_id!r}, role_name={self.role_name!r})"


class ABACPolicy:
    """Represents an ABAC policy with attribute-based rules."""

    def __init__(
        self,
        name: str,
        effect: str,
        actions: list[str],
        resources: list[str],
        conditions: dict[str, Any] | None = None,
    ):
        self.name = name
        self.effect = effect  # "allow" or "deny"
        self.actions = actions  # e.g., ["read", "write"]
        self.resources = resources  # e.g., ["user", "admin:*"]
        self.conditions = conditions or {}  # e.g., {"user.department": "engineering"}

    def evaluate(self, context: dict[str, Any]) -> bool:
        """Evaluate if the policy matches the given context."""
        action = context.get("action")
        resource = context.get("resource")

        if action not in self.actions and "*" not in self.actions:
            return False

        if not self._match_resource(resource):
            return False

        return self._evaluate_conditions(context)

    def _match_resource(self, resource: str | None) -> bool:
        if not resource:
            return False
        for pattern in self.resources:
            if pattern == "*":
                return True
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                if resource.startswith(prefix):
                    return True
            elif pattern == resource:
                return True
        return False

    def _evaluate_conditions(self, context: dict[str, Any]) -> bool:
        for key, expected in self.conditions.items():
            parts = key.split(".")
            value = context
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    value = None
                    break

            if value != expected:
                return False
        return True

    def __repr__(self) -> str:
        return f"ABACPolicy(name={self.name!r}, effect={self.effect!r})"


class RoleStore(Protocol):
    """Protocol for role storage implementations.

    Implementations must provide async methods for:
    - Creating/getting/deleting roles
    - Assigning/unassigning roles to users
    - Getting all roles for a user
    - Getting all role assignments

    Methods:
        create_role: Create a new role
            Args:
                role: Role object
            Returns:
                The created role
        get_role: Get a role by name
            Args:
                role_name: The role name
            Returns:
                Role object or None
        delete_role: Delete a role
            Args:
                role_name: The role name
        assign_role: Assign a role to a user
            Args:
                user_id: The user ID
                role_name: The role name
                attributes: Optional role attributes
        unassign_role: Remove a role from a user
            Args:
                user_id: The user ID
                role_name: The role name
        get_user_roles: Get all roles for a user
            Args:
                user_id: The user ID
            Returns:
                List of UserRole objects
        get_all_assignments: Get all role assignments
            Returns:
                List of UserRole objects
    """

    async def create_role(self, role: Role) -> Role: ...

    async def get_role(self, role_name: str) -> Role | None: ...

    async def delete_role(self, role_name: str) -> None: ...

    async def assign_role(
        self, user_id: str, role_name: str, attributes: dict[str, Any] | None = None
    ) -> UserRole: ...

    async def unassign_role(self, user_id: str, role_name: str) -> None: ...

    async def get_user_roles(self, user_id: str) -> list[UserRole]: ...

    async def get_all_assignments(self) -> list[UserRole]: ...
