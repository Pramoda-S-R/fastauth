"""
Authorization dependency helpers for FastAPI.

Provides dependency injection functions for RBAC/ABAC authorization.
"""

from typing import TYPE_CHECKING, Any, Callable, Coroutine

from fastapi import Depends, HTTPException, status

from .base import Permission

if TYPE_CHECKING:
    from ..core.manager import AuthManager


async def _check_permission(
    auth: "AuthManager",
    permission: Permission,
    current_user_id: str,
    context_extractor: Callable[[], dict[str, Any]] | None = None,
) -> bool:
    """Check if the current user has a permission."""
    if not auth.authorization:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authorization not configured",
        )

    context = context_extractor() if context_extractor else {}
    has_permission = await auth.authorization.check_permission(
        user_id=current_user_id,
        permission=permission,
        context=context,
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    return True


async def _check_role(
    auth: "AuthManager",
    role_name: str,
    current_user_id: str,
) -> bool:
    """Check if the current user has a role."""
    if not auth.authorization:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authorization not configured",
        )

    has_role = await auth.authorization.check_role(
        user_id=current_user_id,
        role_name=role_name,
    )

    if not has_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    return True


def require_permission(
    auth: "AuthManager",
    permission: Permission,
    context_extractor: Callable[[], dict[str, Any]] | None = None,
) -> Callable[[Any], Coroutine[Any, Any, bool]]:
    """FastAPI dependency that requires a specific permission.

    Usage:
        @app.get("/admin")
        async def admin_endpoint(user = Depends(require_permission(auth, Permission.ADMIN))):
            ...
    """

    async def dependency(current_user) -> bool:
        if not hasattr(current_user, "id") or not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
        return await _check_permission(
            auth, permission, current_user.id, context_extractor
        )

    return Depends(dependency)


def require_role(
    auth: "AuthManager",
    role_name: str,
) -> Callable[[Any], Coroutine[Any, Any, bool]]:
    """FastAPI dependency that requires a specific role.

    Usage:
        @app.get("/admin")
        async def admin_endpoint(user = Depends(require_role(auth, "admin"))):
            ...
    """

    async def dependency(current_user) -> bool:
        if not hasattr(current_user, "id") or not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
        return await _check_role(auth, role_name, current_user.id)

    return Depends(dependency)
