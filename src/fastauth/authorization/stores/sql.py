"""
SQL database role store implementation.

Stores roles and role assignments in a SQL database.
"""

from typing import Any, TYPE_CHECKING

from ..base import Role, RoleStore, UserRole

if TYPE_CHECKING:
    from ...core.types import DatabaseSession


class SQLRoleStore(RoleStore):
    """SQL database-backed role store.

    Stores roles and role assignments in any SQL database.
    Requires database models that follow the RoleModel and UserRoleModel protocols.

    Args:
        role_model: Database model class for roles
        user_role_model: Database model class for user-role assignments
        db_session: Database session client (e.g., SQLAlchemy session)
    """

    def __init__(
        self,
        role_model: type[Any],
        user_role_model: type[Any],
        db_session: "DatabaseSession",
    ):
        self.role_model = role_model
        self.user_role_model = user_role_model
        self.db_session = db_session

    async def create_role(self, role: Role) -> Role:
        """Create a new role.

        Args:
            role: Role object to create

        Returns:
            The created role
        """
        existing = await self.get_role(role.name)
        if existing:
            return existing

        role_record = self.role_model(
            name=role.name,
            permissions=[p.value for p in role.permissions],
        )
        self.db_session.add(role_record)
        self.db_session.commit()
        return role

    async def get_role(self, role_name: str) -> Role | None:
        """Get a role by name.

        Args:
            role_name: The role name

        Returns:
            Role object or None if not found
        """
        from ..base import Permission

        record = (
            self.db_session.query(self.role_model)
            .filter(self.role_model.name == role_name)
            .first()
        )
        if not record:
            return None

        permissions = [Permission(p) for p in record.permissions]
        return Role(name=record.name, permissions=permissions)

    async def delete_role(self, role_name: str) -> None:
        """Delete a role.

        Args:
            role_name: The role name
        """
        record = (
            self.db_session.query(self.role_model)
            .filter(self.role_model.name == role_name)
            .first()
        )
        if record:
            self.db_session.delete(record)

        assignments = (
            self.db_session.query(self.user_role_model)
            .filter(self.user_role_model.role_name == role_name)
            .all()
        )
        for assignment in assignments:
            self.db_session.delete(assignment)

        self.db_session.commit()

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
        existing = (
            self.db_session.query(self.user_role_model)
            .filter(
                self.user_role_model.user_id == user_id,
                self.user_role_model.role_name == role_name,
            )
            .first()
        )
        if existing:
            existing.attributes = attributes
            self.db_session.commit()
            return UserRole(user_id, role_name, attributes)

        import json

        role_record = self.user_role_model(
            user_id=user_id,
            role_name=role_name,
            attributes=json.dumps(attributes) if attributes else None,
        )
        self.db_session.add(role_record)
        self.db_session.commit()
        return UserRole(user_id, role_name, attributes)

    async def unassign_role(self, user_id: str, role_name: str) -> None:
        """Remove a role from a user.

        Args:
            user_id: The user ID
            role_name: The role name
        """
        record = (
            self.db_session.query(self.user_role_model)
            .filter(
                self.user_role_model.user_id == user_id,
                self.user_role_model.role_name == role_name,
            )
            .first()
        )
        if record:
            self.db_session.delete(record)
            self.db_session.commit()

    async def get_user_roles(self, user_id: str) -> list[UserRole]:
        """Get all roles for a user.

        Args:
            user_id: The user ID

        Returns:
            List of UserRole objects
        """
        import json

        records = (
            self.db_session.query(self.user_role_model)
            .filter(self.user_role_model.user_id == user_id)
            .all()
        )
        result = []
        for record in records:
            attributes = None
            if record.attributes:
                try:
                    attributes = json.loads(record.attributes)
                except (json.JSONDecodeError, TypeError):
                    pass
            result.append(UserRole(record.user_id, record.role_name, attributes))
        return result

    async def get_all_assignments(self) -> list[UserRole]:
        """Get all role assignments.

        Returns:
            List of all UserRole objects
        """
        import json

        records = self.db_session.query(self.user_role_model).all()
        result = []
        for record in records:
            attributes = None
            if record.attributes:
                try:
                    attributes = json.loads(record.attributes)
                except (json.JSONDecodeError, TypeError):
                    pass
            result.append(UserRole(record.user_id, record.role_name, attributes))
        return result
