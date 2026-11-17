from abc import ABC, abstractmethod

from app.modules.policies.schemas import (
    CreatePolicyRequest,
    PolicyInfo,
    PolicyListParams,
    UpdatePolicyRequest,
)
from app.schemas import Page


class PoliciesServiceInterface(ABC):
    """Public API of the policies module.

    Every method is scoped to `organization_id`; the caller passes the logged-in user's
    organization, never a value from the request. Writes are flushed, not committed.
    """

    @abstractmethod
    def create_policy(self, organization_id: int, params: CreatePolicyRequest) -> PolicyInfo:
        """Raises PolicyNumberAlreadyExistsError (a ConflictError) if the organization already has
        a policy with this number, ignoring case."""

    @abstractmethod
    def update_policy(
        self, organization_id: int, policy_id: int, params: UpdatePolicyRequest
    ) -> PolicyInfo:
        """Replaces the editable fields, including status (cancel / reactivate).

        Raises PolicyNotFoundError or PolicyNumberAlreadyExistsError.
        """

    @abstractmethod
    def get_policy(self, organization_id: int, policy_id: int) -> PolicyInfo:
        """Raises PolicyNotFoundError (a NotFoundError) if it doesn't exist or belongs to another
        organization."""

    @abstractmethod
    def list_policies(self, organization_id: int, params: PolicyListParams) -> Page[PolicyInfo]:
        """One page of the organization's policies, newest first, with the total count."""

    @abstractmethod
    def find_by_policy_number(self, organization_id: int, policy_number: str) -> PolicyInfo | None:
        """The organization's policy with this number, ignoring case, or None. For FNOL matching."""
