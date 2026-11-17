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

    @abstractmethod
    def get_user(self, user_id: int) -> UserInfo | None:
        """The user with this id, or None if there is none."""

    @abstractmethod
    def check_credentials(self, email: str, password: str) -> UserInfo | None:
        """The user if the email exists and the password matches it, otherwise None.

        Doesn't look at `is_active`: deciding who may log in is the caller's business.
        """
