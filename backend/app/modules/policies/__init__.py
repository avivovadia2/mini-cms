from flask import Blueprint

from app.modules.policies.interface import PoliciesServiceInterface
from app.registry import ModuleRegistration

__all__ = ["PoliciesServiceInterface", "registration"]


def _import_models() -> None:
    from app.modules.policies.internal.models.policy import Policy  # noqa: F401


def _get_services() -> dict[type, type]:
    from app.modules.policies.internal.service import PoliciesService

    return {PoliciesServiceInterface: PoliciesService}


def _get_blueprint() -> Blueprint:
    from app.modules.policies.api.policies_api import bp

    return bp


registration = ModuleRegistration(
    name="policies",
    get_services=_get_services,
    import_models=_import_models,
    get_blueprint=_get_blueprint,
)
