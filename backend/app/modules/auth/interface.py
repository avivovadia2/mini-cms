from abc import ABC, abstractmethod

from app.modules.auth.schemas import MeResponse, RegisterRequest


class AuthServiceInterface(ABC):
    """Public API of the auth module: who is logged in, and how they got there."""

    @abstractmethod
    def register(self, params: RegisterRequest) -> MeResponse:
        """Create an organization with its first user, and log that user in.

        Both rows are added to the current transaction; the caller commits. If the user can't be
        created (e.g. the email is taken), the error propagates, nothing is committed, and no
        organization is left behind.
        """
