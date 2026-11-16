from flask import Flask

from app.config import Config
from app.extensions import api_spec, db, login_manager, migrate
from app.registry import register_service


def create_app(config_class: type = Config) -> Flask:
    """Application factory: build a fresh, configured app (tests can pass their own config)."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.api import api_bp

    app.register_blueprint(api_bp)
    _register_modules(app)

    # Must run after blueprints are registered so spectree can see their routes.
    # OpenAPI docs: /api/docs/swagger/
    api_spec.register(app)

    return app


def _register_modules(app: Flask) -> None:
    from app.modules import MODULE_REGISTRATIONS

    for registration in MODULE_REGISTRATIONS:
        registration.import_models()
        for interface, implementation_class in registration.get_services().items():
            register_service(interface, implementation_class)
        blueprint = registration.get_blueprint()
        if blueprint is not None:
            app.register_blueprint(blueprint)
