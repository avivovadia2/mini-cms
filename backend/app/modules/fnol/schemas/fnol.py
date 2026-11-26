from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from app.modules.policies.schemas import PolicyInfo


class FnolStatus(StrEnum):
    SUBMITTED = "submitted"
    CONVERTED = "converted"  # into a claim, in M3
    REJECTED = "rejected"


class FnolInfo(BaseModel):
    """An FNOL as stored: `policy_id` is the matched policy, or None if nothing matched."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    reported_policy_number: str
    policy_id: int | None
    reporter_name: str
    reporter_email: str | None
    reporter_phone: str | None
    loss_date: date
    loss_description: str
    loss_state: str | None
    status: FnolStatus
    rejection_reason: str | None
    submitted_by_id: int
    created_at: datetime


class FnolResponse(FnolInfo):
    """What the API returns: the FNOL plus its matched policy, so a screen needs one call."""

    policy: PolicyInfo | None
