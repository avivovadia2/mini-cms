from abc import ABC, abstractmethod

from app.modules.organizations.schemas import OrganizationInfo


class OrganizationsServiceInterface(ABC):
    """Public API of the organizations module."""

    @abstractmethod
    def create_organization(self, name: str) -> OrganizationInfo:
        """Add a new organization to the current transaction (the caller commits)."""
