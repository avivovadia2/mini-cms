from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints

from app.modules.organizations.schemas import OrganizationInfo
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


class MeResponse(BaseModel):
    """The logged-in user and their organization."""

    id: int
    email: str
    full_name: str
    organization: OrganizationInfo
