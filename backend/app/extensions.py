"""Extension instances, created unbound and attached to the app in create_app().

Keeping them here (not in __init__.py) lets models and routes import `db` without circular imports.
"""

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from spectree import SpecTree

db = SQLAlchemy()
migrate = Migrate()
api_spec = SpecTree("flask", title="Mini CMS API", version="0.1.0", path="api/docs")
