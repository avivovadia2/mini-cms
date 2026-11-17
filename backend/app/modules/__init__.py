"""Domain modules. Each one follows the CMS's third-generation service-module layout:

    app/modules/<name>/
        __init__.py        exports the interface and `registration` (a ModuleRegistration)
        interface.py       abstract service class (ABC): the module's public API
        schemas/           Pydantic models going in and out of the interface and the API
        api/               Flask blueprint + spectree routes; calls the service, commits the session
        internal/          private; never imported from outside the module
            service.py     implements the interface
            managers/      business logic and queries; never commits
            models/        SQLAlchemy models
            exceptions.py  the module's DomainError subclasses

To add a module, define `registration` in its __init__.py and append it to MODULE_REGISTRATIONS.
"""

from app.modules import auth, organizations, users
from app.registry import ModuleRegistration

MODULE_REGISTRATIONS: list[ModuleRegistration] = [
    organizations.registration,
    users.registration,
    auth.registration,
]
