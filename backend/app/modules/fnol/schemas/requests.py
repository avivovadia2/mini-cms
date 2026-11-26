from datetime import date

from pydantic import BaseModel, field_validator

from app.modules.fnol.schemas.fnol import FnolStatus
from app.schemas import LongText, OptionalEmail, OptionalText, PageParams, RequiredText


class ReportLossRequest(BaseModel):
    """No organization, status, matched policy or submitter: the server decides all four."""

    reported_policy_number: RequiredText
    reporter_name: RequiredText
    reporter_email: OptionalEmail = None
    reporter_phone: OptionalText = None
    loss_date: date
    loss_description: LongText
    loss_state: OptionalText = None

    @field_validator("loss_date")
    @classmethod
    def not_in_the_future(cls, loss_date: date) -> date:
        # The server's today. A user a few hours ahead of the server could be refused a loss
        # dated "today" for them; acceptable here, and the frontend checks the same rule.
        if loss_date > date.today():
            raise ValueError("loss_date cannot be in the future")
        return loss_date


class RejectFnolRequest(BaseModel):
    rejection_reason: LongText


class FnolListParams(PageParams):
    """`?status=submitted`. No status: every FNOL. (The FNOL screen asks for submitted first.)"""

    status: FnolStatus | None = None
