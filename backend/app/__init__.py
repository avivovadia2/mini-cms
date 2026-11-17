from flask import Flask

from app.config import Config
from app.extensions import api_spec, db, migrate


def create_app(config_class: type = Config) -> Flask:
    """Application factory: build a fresh, configured app (tests can pass their own config)."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.api import api_bp

    app.register_blueprint(api_bp)

    # Must run after blueprints are registered so spectree can see their routes.
    # OpenAPI docs: /api/docs/swagger/
    api_spec.register(app)

    return app
