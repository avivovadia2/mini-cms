from abc import ABC, abstractmethod

from app.modules.users.schemas import UserInfo


class UsersServiceInterface(ABC):
    """Public API of the users module."""

    @abstractmethod
    def create_user(
        self, *, organization_id: int, email: str, full_name: str, password: str
    ) -> UserInfo:
        """Add a user to the current transaction (the caller commits).

        Raises EmailAlreadyRegisteredError (a ConflictError) if the email is taken.
        """
