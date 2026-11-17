from app.modules.policies.interface import PoliciesServiceInterface
from app.modules.policies.internal.managers import policy_manager
from app.modules.policies.schemas import (
    CreatePolicyRequest,
    PolicyInfo,
    PolicyListParams,
    UpdatePolicyRequest,
)
from app.schemas import Page


class PoliciesService(PoliciesServiceInterface):
    def create_policy(self, organization_id: int, params: CreatePolicyRequest) -> PolicyInfo:
        return PolicyInfo.model_validate(policy_manager.create_policy(organization_id, params))

    def update_policy(
        self, organization_id: int, policy_id: int, params: UpdatePolicyRequest
    ) -> PolicyInfo:
        policy = policy_manager.update_policy(organization_id, policy_id, params)
        return PolicyInfo.model_validate(policy)

    def get_policy(self, organization_id: int, policy_id: int) -> PolicyInfo:
        return PolicyInfo.model_validate(policy_manager.get_policy(organization_id, policy_id))

    def list_policies(self, organization_id: int, params: PolicyListParams) -> Page[PolicyInfo]:
        policies, total_count = policy_manager.list_policies(organization_id, params)
        return Page[PolicyInfo](
            results=[PolicyInfo.model_validate(policy) for policy in policies],
            total_count=total_count,
        )

    def find_by_policy_number(self, organization_id: int, policy_number: str) -> PolicyInfo | None:
        policy = policy_manager.find_by_policy_number(organization_id, policy_number)
        return PolicyInfo.model_validate(policy) if policy is not None else None
