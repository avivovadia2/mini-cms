from abc import ABC, abstractmethod

from app.modules.users.schemas import UserInfo
from app.schemas import Page, PageParams


class UsersServiceInterface(ABC):
    """Public API of the users module.

    Methods that take `organization_id` only ever see that organization's users; the caller
    passes the logged-in user's organization, never a value from the request.
    """

    @abstractmethod
    def create_user(
        self, *, organization_id: int, email: str, full_name: str, password: str
    ) -> UserInfo:
        """Add a user to the current transaction (the caller commits).

        Raises EmailAlreadyRegisteredError (a ConflictError) if the email is taken, in any
        organization.
        """

    @abstractmethod
    def list_users(self, organization_id: int, page: PageParams) -> Page[UserInfo]:
        """One page of the organization's users, oldest first, with the total count."""

    @abstractmethod
    def get_organization_user(self, organization_id: int, user_id: int) -> UserInfo:
        """Raises UserNotFoundError (a NotFoundError) if the user doesn't exist or belongs to
        another organization."""

    @abstractmethod
    def get_user(self, user_id: int) -> UserInfo | None:
        """The user with this id, in any organization, or None.

        Not scoped to an organization: only for loading the session's own user. Anything that
        serves a request about other users uses get_organization_user.
        """

    @abstractmethod
    def check_credentials(self, email: str, password: str) -> UserInfo | None:
        """The user if the email exists and the password matches it, otherwise None.

        Doesn't look at `is_active`: deciding who may log in is the caller's business.
        """
