from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Route modules register themselves on api_bp when imported.
from app.api import health  # noqa: E402, F401
