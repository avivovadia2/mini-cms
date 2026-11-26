from datetime import date
from typing import Self

from pydantic import BaseModel, model_validator

from app.modules.policies.schemas.policy import LineOfBusiness, PolicyStatus
from app.schemas import PageParams, RequiredText


class CreatePolicyRequest(BaseModel):
    """No organization and no status: a new policy joins my organization, and starts active."""

    policy_number: RequiredText
    insured_name: RequiredText
    line_of_business: LineOfBusiness
    effective_date: date
    expiration_date: date

    # Runs after the single fields are validated, so both dates are real dates here. Raising
    # ValueError makes it a normal validation error: spectree answers 422.
    @model_validator(mode="after")
    def expiration_after_effective(self) -> Self:
        if self.expiration_date <= self.effective_date:
            raise ValueError("expiration_date must be after effective_date")
        return self


class UpdatePolicyRequest(CreatePolicyRequest):
    """A full replacement of the editable fields. Cancelling is `status: "cancelled"`."""

    status: PolicyStatus


class PolicyListParams(PageParams):
    """`?search=acme&status=active&line_of_business=auto`; the filters combine with AND."""

    search: str | None = None  # case-insensitive, in policy number or insured name
    status: PolicyStatus | None = None
    line_of_business: LineOfBusiness | None = None
