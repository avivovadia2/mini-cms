from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# The password rule lives here, with the module that owns users; every request schema that takes
# a password (register now, "add user" in M1 2/4) uses this type instead of repeating the rule.
Password = Annotated[str, Field(min_length=8, max_length=128)]


class UserInfo(BaseModel):
    """What other modules (and the API) get back: never the ORM model, never the password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    email: str
    full_name: str
    is_active: bool
