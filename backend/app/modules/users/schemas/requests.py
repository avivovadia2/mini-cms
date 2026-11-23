from pydantic import BaseModel, EmailStr

from app.modules.users.schemas.user import Password
from app.schemas import RequiredText


class AddUserRequest(BaseModel):
    """No organization field: the new user always joins the logged-in user's organization."""

    email: EmailStr
    full_name: RequiredText
    password: Password
