from abc import ABC, abstractmethod

from app.modules.fnol.schemas import (
    FnolListParams,
    FnolResponse,
    RejectFnolRequest,
    ReportLossRequest,
)
from app.schemas import Page


class FnolServiceInterface(ABC):
    """Public API of the FNOL module.

    Every method is scoped to `organization_id`; the caller passes the logged-in user's
    organization, never a value from the request. Writes are flushed, not committed.
    """

    @abstractmethod
    def report_loss(
        self, organization_id: int, submitted_by_id: int, params: ReportLossRequest
    ) -> FnolResponse:
        """Creates a submitted FNOL, matched to the organization's policy with the reported
        number (ignoring case), or to none.

        Matching happens here only: a matching policy created later doesn't update the FNOL.
        """

    @abstractmethod
    def get_fnol(self, organization_id: int, fnol_id: int) -> FnolResponse:
        """Raises FnolNotFoundError (a NotFoundError) if it doesn't exist or belongs to another
        organization."""

    @abstractmethod
    def list_fnols(self, organization_id: int, params: FnolListParams) -> Page[FnolResponse]:
        """One page of the organization's FNOLs, newest first, with the total count."""

    @abstractmethod
    def reject_fnol(
        self, organization_id: int, fnol_id: int, params: RejectFnolRequest
    ) -> FnolResponse:
        """Raises FnolNotFoundError, or FnolNotSubmittedError (a ConflictError) if the FNOL is
        already converted or rejected."""
