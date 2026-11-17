from app.modules.organizations.interface import OrganizationsServiceInterface
from app.registry import ModuleRegistration

__all__ = ["OrganizationsServiceInterface", "registration"]


def _import_models() -> None:
    from app.modules.organizations.internal.models.organization import Organization  # noqa: F401


def _get_services() -> dict[type, type]:
    from app.modules.organizations.internal.service import OrganizationsService

    return {OrganizationsServiceInterface: OrganizationsService}


registration = ModuleRegistration(
    name="organizations", get_services=_get_services, import_models=_import_models
)
