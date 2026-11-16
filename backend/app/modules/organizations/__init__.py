from app.registry import ModuleRegistration


def _import_models() -> None:
    from app.modules.organizations.internal.models.organization import Organization  # noqa: F401


registration = ModuleRegistration(name="organizations", import_models=_import_models)
