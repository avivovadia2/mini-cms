from flask import Blueprint

from app.modules.fnol.interface import FnolServiceInterface
from app.registry import ModuleRegistration

__all__ = ["FnolServiceInterface", "registration"]


def _import_models() -> None:
    from app.modules.fnol.internal.models.fnol import Fnol  # noqa: F401


def _get_services() -> dict[type, type]:
    from app.modules.fnol.internal.service import FnolService

    return {FnolServiceInterface: FnolService}


def _get_blueprint() -> Blueprint:
    from app.modules.fnol.api.fnol_api import bp

    return bp


registration = ModuleRegistration(
    name="fnol",
    get_services=_get_services,
    import_models=_import_models,
    get_blueprint=_get_blueprint,
)
