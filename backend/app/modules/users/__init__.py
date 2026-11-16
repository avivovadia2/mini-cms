from app.registry import ModuleRegistration


def _import_models() -> None:
    from app.modules.users.internal.models.user import User  # noqa: F401


registration = ModuleRegistration(name="users", import_models=_import_models)
