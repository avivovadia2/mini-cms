from app.modules.users.interface import UsersServiceInterface
from app.registry import ModuleRegistration

__all__ = ["UsersServiceInterface", "registration"]


def _import_models() -> None:
    from app.modules.users.internal.models.user import User  # noqa: F401


def _get_services() -> dict[type, type]:
    from app.modules.users.internal.service import UsersService

    return {UsersServiceInterface: UsersService}


registration = ModuleRegistration(
    name="users", get_services=_get_services, import_models=_import_models
)
