from app.modules.fnol.interface import FnolServiceInterface
from app.modules.fnol.internal.managers import fnol_manager
from app.modules.fnol.internal.models.fnol import Fnol
from app.modules.fnol.schemas import (
    FnolInfo,
    FnolListParams,
    FnolResponse,
    RejectFnolRequest,
    ReportLossRequest,
)
from app.modules.policies import PoliciesServiceInterface
from app.schemas import Page


class FnolService(FnolServiceInterface):
    # Injected by the registry: the policies module is reached only through its interface.
    def __init__(self, policies: PoliciesServiceInterface) -> None:
        self._policies = policies

    def report_loss(
        self, organization_id: int, submitted_by_id: int, params: ReportLossRequest
    ) -> FnolResponse:
        policy = self._policies.find_by_policy_number(
            organization_id, params.reported_policy_number
        )
        fnol = fnol_manager.create_fnol(
            organization_id, submitted_by_id, policy.id if policy else None, params
        )
        return FnolResponse(**FnolInfo.model_validate(fnol).model_dump(), policy=policy)

    def get_fnol(self, organization_id: int, fnol_id: int) -> FnolResponse:
        fnol = fnol_manager.get_fnol(organization_id, fnol_id)
        return self._with_policies(organization_id, [fnol])[0]

    def list_fnols(self, organization_id: int, params: FnolListParams) -> Page[FnolResponse]:
        fnols, total_count = fnol_manager.list_fnols(organization_id, params)
        return Page[FnolResponse](
            results=self._with_policies(organization_id, fnols), total_count=total_count
        )

    def reject_fnol(
        self, organization_id: int, fnol_id: int, params: RejectFnolRequest
    ) -> FnolResponse:
        fnol = fnol_manager.reject_fnol(organization_id, fnol_id, params.rejection_reason)
        return self._with_policies(organization_id, [fnol])[0]

    def _with_policies(self, organization_id: int, fnols: list[Fnol]) -> list[FnolResponse]:
        """Attach each FNOL's matched policy, loading all of them in one query (no N+1)."""
        policy_ids = {fnol.policy_id for fnol in fnols if fnol.policy_id is not None}
        policies = self._policies.get_policies(organization_id, policy_ids)
        return [
            FnolResponse(
                **FnolInfo.model_validate(fnol).model_dump(),
                policy=policies.get(fnol.policy_id) if fnol.policy_id is not None else None,
            )
            for fnol in fnols
        ]
