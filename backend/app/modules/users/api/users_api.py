from flask import Blueprint
from flask_login import current_user, login_required
from spectree import Response

from app.errors import ErrorResponse
from app.extensions import api_spec, db
from app.modules.users.interface import UsersServiceInterface
from app.modules.users.schemas import AddUserRequest, UserInfo
from app.registry import get_service
from app.schemas import Page, PageParams

bp = Blueprint("users", __name__, url_prefix="/api/users")

# Every route: @login_required first (401 without a session), and the organization always comes
# from current_user, never from the URL or the body.


@bp.get("")
@login_required
@api_spec.validate(
    query=PageParams,
    resp=Response(HTTP_200=Page[UserInfo], HTTP_401=ErrorResponse),
    tags=["users"],
)
def list_users(query: PageParams):
    """Users of my organization, oldest first."""
    return get_service(UsersServiceInterface).list_users(current_user.organization_id, query)


@bp.get("/<int:user_id>")
@login_required
@api_spec.validate(
    resp=Response(HTTP_200=UserInfo, HTTP_401=ErrorResponse, HTTP_404=ErrorResponse),
    tags=["users"],
)
def get_user(user_id: int):
    """One user of my organization. 404 for a user of another organization."""
    return get_service(UsersServiceInterface).get_organization_user(
        current_user.organization_id, user_id
    )


@bp.post("")
@login_required
@api_spec.validate(
    json=AddUserRequest,
    resp=Response(HTTP_201=UserInfo, HTTP_401=ErrorResponse, HTTP_409=ErrorResponse),
    tags=["users"],
)
def add_user(json: AddUserRequest):
    """Add a user to my organization."""
    user = get_service(UsersServiceInterface).create_user(
        organization_id=current_user.organization_id,
        email=json.email,
        full_name=json.full_name,
        password=json.password,
    )
    db.session.commit()
    return user, 201
