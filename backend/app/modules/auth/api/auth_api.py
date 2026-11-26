from flask import Blueprint
from flask_login import current_user, login_required
from spectree import Response

from app.errors import ErrorResponse
from app.extensions import api_spec, db, login_manager
from app.modules.auth.interface import AuthServiceInterface
from app.modules.auth.internal.session_user import load_session_user
from app.modules.auth.schemas import LoginRequest, MeResponse, RegisterRequest
from app.registry import get_service

bp = Blueprint("auth", __name__, url_prefix="/auth")

login_manager.user_loader(load_session_user)

# Decorator order: @login_required goes above @api_spec.validate, so it wraps it and runs first.
# A request without a session gets 401 before its body is even validated.


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


@bp.post("/login")
@api_spec.validate(
    json=LoginRequest,
    resp=Response(HTTP_200=MeResponse, HTTP_401=ErrorResponse),
    tags=["auth"],
)
def login(json: LoginRequest):
    """Log in with email and password. No login needed."""
    return get_service(AuthServiceInterface).login(json)


@bp.post("/logout")
@login_required
@api_spec.validate(resp=Response("HTTP_204", HTTP_401=ErrorResponse), tags=["auth"])
def logout():
    """End the current session."""
    get_service(AuthServiceInterface).logout()
    return "", 204


@bp.get("/me")
@login_required
@api_spec.validate(resp=Response(HTTP_200=MeResponse, HTTP_401=ErrorResponse), tags=["auth"])
def me():
    """The logged-in user and their organization."""
    return get_service(AuthServiceInterface).get_me(current_user.id)
