from flask_login import UserMixin

from app.modules.users import UsersServiceInterface
from app.modules.users.schemas import UserInfo
from app.registry import get_service


class SessionUser(UserMixin):
    """What Flask-Login's `current_user` holds for a logged-in request.

    Not the ORM User (that model is internal to the users module): just the fields other code
    needs, chiefly `organization_id`, which scopes every query to the user's organization.
    """

    def __init__(self, user: UserInfo) -> None:
        self.id = user.id
        self.organization_id = user.organization_id


def load_session_user(user_id: str) -> SessionUser | None:
    """Flask-Login's user_loader: called once per request that carries a session cookie, with the
    id stored at login. Returning None makes the request anonymous, so a user who was deactivated
    (or deleted) after logging in loses access on their next request."""
    user = get_service(UsersServiceInterface).get_user(int(user_id))
    if user is None or not user.is_active:
        return None
    return SessionUser(user)
