from abc import ABC, abstractmethod

from app.modules.auth.schemas import LoginRequest, MeResponse, RegisterRequest


class AuthServiceInterface(ABC):
    """Public API of the auth module: who is logged in, and how they got there."""

    @abstractmethod
    def register(self, params: RegisterRequest) -> MeResponse:
        """Create an organization with its first user, and log that user in.

        Both rows are added to the current transaction; the caller commits. If the user can't be
        created (e.g. the email is taken), the error propagates, nothing is committed, and no
        organization is left behind.
        """

    @abstractmethod
    def login(self, params: LoginRequest) -> MeResponse:
        """Log the user in. Raises InvalidCredentialsError (an AuthenticationError) if the email
        or password is wrong, or the user is inactive."""

    @abstractmethod
    def logout(self) -> None:
        """End the current session."""

    @abstractmethod
    def get_me(self, user_id: int) -> MeResponse:
        """The logged-in user and their organization."""
