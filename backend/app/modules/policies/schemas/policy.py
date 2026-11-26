from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


# StrEnum: each member is also a plain string ("auto"), so it compares, stores and serialises as
# its value. The model's database enum types are built from these, so both stay in sync.
class LineOfBusiness(StrEnum):
    AUTO = "auto"
    PROPERTY = "property"
    GENERAL_LIABILITY = "general_liability"


class PolicyStatus(StrEnum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class PolicyInfo(BaseModel):
    """What other modules (FNOL matching, claims in M3) and the API get back."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    policy_number: str
    insured_name: str
    line_of_business: LineOfBusiness
    effective_date: date
    expiration_date: date
    status: PolicyStatus
