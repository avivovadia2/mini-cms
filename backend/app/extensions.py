"""Extension instances, created unbound and attached to the app in create_app().

Keeping them here (not in __init__.py) lets models and routes import `db` without circular imports.
"""

from flask import jsonify
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from spectree import SpecTree
from sqlalchemy import MetaData

# Deterministic constraint names, so Alembic migrations can refer to (and drop) them reliably.
# Same convention as the CMS.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

db = SQLAlchemy(metadata=MetaData(naming_convention=NAMING_CONVENTION))
migrate = Migrate()
login_manager = LoginManager()
api_spec = SpecTree("flask", title="Mini CMS API", version="0.1.0", path="api/docs")


@login_manager.unauthorized_handler
def unauthorized():
    """@login_required without a session: JSON 401 (an API never redirects to a login page)."""
    return jsonify(message="Unauthorized"), 401
