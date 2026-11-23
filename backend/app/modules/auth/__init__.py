from flask import Blueprint

from app.modules.auth.interface import AuthServiceInterface
from app.registry import ModuleRegistration

__all__ = ["AuthServiceInterface", "registration"]


def _get_services() -> dict[type, type]:
    from app.modules.auth.internal.service import AuthService

    return {AuthServiceInterface: AuthService}


def _get_blueprint() -> Blueprint:
    from app.modules.auth.api.auth_api import bp

    return bp


# No import_models: auth owns no tables.
registration = ModuleRegistration(
    name="auth", get_services=_get_services, get_blueprint=_get_blueprint
)
