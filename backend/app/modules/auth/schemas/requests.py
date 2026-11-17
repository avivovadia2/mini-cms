from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints

from app.modules.users.schemas import Password

# Required text: surrounding whitespace removed, then at least one character left.
RequiredText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
]


class RegisterRequest(BaseModel):
    organization_name: RequiredText
    full_name: RequiredText
    email: EmailStr
    password: Password


class LoginRequest(BaseModel):
    email: EmailStr
    # Not the `Password` rule: if that rule ever gets stricter, existing users must still be able
    # to log in with the password they have. A wrong password is a 401, not a 422.
    password: Annotated[str, Field(min_length=1, max_length=128)]
