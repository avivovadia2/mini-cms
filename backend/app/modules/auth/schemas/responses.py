from pydantic import BaseModel

from app.modules.organizations.schemas import OrganizationInfo


class MeResponse(BaseModel):
    """The logged-in user and their organization."""

    id: int
    email: str
    full_name: str
    organization: OrganizationInfo
