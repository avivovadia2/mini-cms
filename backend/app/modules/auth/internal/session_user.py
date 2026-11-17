from flask_login import UserMixin

from app.modules.users.schemas import UserInfo


class SessionUser(UserMixin):
    """What Flask-Login's `current_user` holds for a logged-in request.

    Not the ORM User (that model is internal to the users module): just the fields other code
    needs, chiefly `organization_id`, which scopes every query to the user's organization.
    """

    def __init__(self, user: UserInfo) -> None:
        self.id = user.id
        self.organization_id = user.organization_id
