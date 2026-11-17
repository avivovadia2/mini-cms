from flask import Blueprint
from spectree import Response

from app.errors import ErrorResponse
from app.extensions import api_spec, db
from app.modules.auth.interface import AuthServiceInterface
from app.modules.auth.schemas import MeResponse, RegisterRequest
from app.registry import get_service

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
@api_spec.validate(
    json=RegisterRequest,
    resp=Response(HTTP_201=MeResponse, HTTP_409=ErrorResponse),
    tags=["auth"],
)
def register(json: RegisterRequest):
    """Register a new organization with its first user, and log that user in. No login needed."""
    me = get_service(AuthServiceInterface).register(json)
    db.session.commit()
    return me, 201
