from pydantic import BaseModel, ConfigDict


class OrganizationInfo(BaseModel):
    """What other modules (and the API) get back: never the ORM model itself."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
