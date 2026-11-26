from flask import Blueprint

# No url_prefix of its own: create_app() mounts it under API_PREFIX, like every module.
api_bp = Blueprint("api", __name__)

# Route modules register themselves on api_bp when imported.
from app.api import health  # noqa: E402, F401
