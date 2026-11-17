from app.modules.organizations.interface import OrganizationsServiceInterface
from app.modules.organizations.internal.managers import organization_manager
from app.modules.organizations.schemas import OrganizationInfo


class OrganizationsService(OrganizationsServiceInterface):
    def create_organization(self, name: str) -> OrganizationInfo:
        organization = organization_manager.create_organization(name)
        return OrganizationInfo.model_validate(organization)
