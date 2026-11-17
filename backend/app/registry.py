"""A minimal service registry, modelled on the CMS's third-generation service modules.

Each domain module (app/modules/<name>/) exposes a ModuleRegistration. At startup, create_app()
asks every module for its models, its services and its blueprint. Code outside a module talks to
it only through its interface, fetched with get_service(Interface), never by importing internal/.

Services are created lazily, once (singletons), on the first get_service() call. Like the CMS,
constructor parameters typed as a registered interface are injected automatically:

    class AuthService(AuthServiceInterface):
        def __init__(self, users: UsersServiceInterface) -> None: ...
"""

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TypeVar, get_type_hints

from flask import Blueprint

T = TypeVar("T")

_implementations: dict[type, type] = {}
_instances: dict[type, object] = {}
_resolving: set[type] = set()


def _no_models() -> None:
    return None


def _no_blueprint() -> Blueprint | None:
    return None


@dataclass(frozen=True)
class ModuleRegistration:
    name: str
    # Returns {Interface: ImplementationClass}. A function so internal/ is imported lazily.
    get_services: Callable[[], dict[type, type]] = field(default=dict)
    # Imports the module's models so SQLAlchemy and Alembic (autogenerate) know about them.
    import_models: Callable[[], None] = _no_models
    get_blueprint: Callable[[], Blueprint | None] = _no_blueprint


def register_service(interface: type, implementation_class: type) -> None:
    _implementations[interface] = implementation_class
    _instances.pop(interface, None)


def get_service(interface: type[T]) -> T:
    """Return the singleton implementation of `interface`, creating it on first use."""
    if interface not in _instances:
        _instances[interface] = _create(interface)
    return _instances[interface]  # type: ignore[return-value]


def _create(interface: type) -> object:
    if interface not in _implementations:
        raise LookupError(f"No service registered for {interface.__name__}")
    if interface in _resolving:
        raise RuntimeError(f"Circular service dependency involving {interface.__name__}")

    implementation_class = _implementations[interface]
    _resolving.add(interface)
    try:
        hints = get_type_hints(implementation_class.__init__)
        dependencies = {
            name: get_service(hints[name])
            for name in inspect.signature(implementation_class.__init__).parameters
            if hints.get(name) in _implementations
        }
        return implementation_class(**dependencies)
    finally:
        _resolving.discard(interface)
