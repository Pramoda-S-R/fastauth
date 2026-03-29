"""
ABAC policy engine and authorization service.

Provides authorization evaluation combining RBAC and ABAC.
"""

from typing import Any

from .base import ABACPolicy, Permission, Role, RoleStore, UserRole


class AuthorizationEngine:
    """Combines RBAC and ABAC for authorization decisions."""

    def __init__(
        self,
        role_store: RoleStore,
        policies: list[ABACPolicy] | None = None,
    ):
        """Initialize the authorization engine.

        Args:
            role_store: Role storage backend
            policies: Optional list of ABAC policies
        """
        self.role_store = role_store
        self.policies = policies or []

    async def check_permission(
        self,
        user_id: str,
        permission: Permission,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Check if a user has a specific permission.

        Args:
            user_id: The user ID
            permission: The permission to check
            context: Optional context for ABAC evaluation

        Returns:
            True if authorized, False otherwise
        """
        user_roles = await self.role_store.get_user_roles(user_id)
        if not user_roles:
            return False

        rbac_granted = False
        for user_role in user_roles:
            role = await self.role_store.get_role(user_role.role_name)
            if role and role.has_permission(permission):
                rbac_granted = True
                break

        if not context and not self.policies:
            return rbac_granted

        if context:
            return await self._evaluate_abac(user_id, context, rbac_granted)
            
        return rbac_granted

    async def check_role(self, user_id: str, role_name: str) -> bool:
        """Check if a user has a specific role.

        Args:
            user_id: The user ID
            role_name: The role name to check

        Returns:
            True if user has the role, False otherwise
        """
        user_roles = await self.role_store.get_user_roles(user_id)
        return any(ur.role_name == role_name for ur in user_roles)

    async def get_user_permissions(self, user_id: str) -> list[Permission]:
        """Get all permissions for a user.

        Args:
            user_id: The user ID

        Returns:
            List of permissions the user has
        """
        user_roles = await self.role_store.get_user_roles(user_id)
        permissions = set()

        for user_role in user_roles:
            role = await self.role_store.get_role(user_role.role_name)
            if role:
                permissions.update(role.permissions)

        return list(permissions)

    async def _evaluate_abac(self, user_id: str, context: dict[str, Any], rbac_granted: bool = False) -> bool:
        """Evaluate ABAC policies for a user.

        Args:
            user_id: The user ID
            context: The authorization context
            rbac_granted: Whether RBAC already granted permission

        Returns:
            True if any policy allows or RBAC allows and no deny policy, False otherwise
        """
        context["user_id"] = user_id

        user_roles = await self.role_store.get_user_roles(user_id)
        for user_role in user_roles:
            role = await self.role_store.get_role(user_role.role_name)
            if role:
                context["role"] = role.name
                context["role_attributes"] = {
                    **(role.attributes or {}),
                    **(user_role.attributes or {})
                }

        allow_found = False
        for policy in self.policies:
            if policy.effect == "deny" and policy.evaluate(context):
                return False
            elif policy.effect == "allow" and policy.evaluate(context):
                allow_found = True

        if rbac_granted:
            return True
            
        return allow_found

    def add_policy(self, policy: ABACPolicy) -> None:
        """Add an ABAC policy.

        Args:
            policy: The policy to add
        """
        self.policies.append(policy)

    def remove_policy(self, policy_name: str) -> None:
        """Remove an ABAC policy by name.

        Args:
            policy_name: The name of the policy to remove
        """
        self.policies = [p for p in self.policies if p.name != policy_name]

    async def authorize(
        self,
        user_id: str,
        permission: Permission | None = None,
        role_name: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Full authorization check combining RBAC and ABAC.

        Args:
            user_id: The user ID
            permission: Optional permission to check
            role_name: Optional role to check
            context: Optional ABAC context

        Returns:
            True if authorized, False otherwise
        """
        if role_name:
            has_role = await self.check_role(user_id, role_name)
            if not has_role:
                return False

        if permission:
            has_permission = await self.check_permission(user_id, permission, context)
            if not has_permission:
                return False

        return True
