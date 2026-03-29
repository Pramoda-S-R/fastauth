"""
Authorization module (RBAC + ABAC).

Provides role-based and attribute-based access control.
"""

from .base import ABACPolicy, Permission, Role, RoleStore, UserRole
from .engine import AuthorizationEngine
from .stores.memory import MemoryRoleStore
from .stores.sql import SQLRoleStore
from .dependencies import require_permission, require_role

__all__ = [
    "ABACPolicy",
    "AuthorizationEngine",
    "MemoryRoleStore",
    "Permission",
    "Role",
    "RoleStore",
    "SQLRoleStore",
    "UserRole",
    "require_permission",
    "require_role",
]
