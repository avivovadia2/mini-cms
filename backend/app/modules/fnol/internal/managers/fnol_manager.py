from sqlalchemy import Select

from app.extensions import db
from app.modules.fnol.internal.exceptions import FnolNotFoundError, FnolNotSubmittedError
from app.modules.fnol.internal.models.fnol import Fnol
from app.modules.fnol.schemas import FnolListParams, FnolStatus, ReportLossRequest


def create_fnol(
    organization_id: int, submitted_by_id: int, policy_id: int | None, params: ReportLossRequest
) -> Fnol:
    fnol = Fnol(
        organization_id=organization_id,
        submitted_by_id=submitted_by_id,
        policy_id=policy_id,
        **params.model_dump(),
    )
    db.session.add(fnol)
    db.session.flush()  # assigns the id and the server defaults (status, created_at)
    return fnol


def get_fnol(organization_id: int, fnol_id: int, *, for_update: bool = False) -> Fnol:
    query = db.select(Fnol).where(Fnol.id == fnol_id, Fnol.organization_id == organization_id)
    if for_update:
        # Lock the row until the transaction ends: of two simultaneous status changes, the second
        # waits, then sees the first one's result instead of overwriting it.
        query = query.with_for_update()
    fnol = db.session.scalar(query)
    if fnol is None:
        raise FnolNotFoundError()
    return fnol


def reject_fnol(organization_id: int, fnol_id: int, rejection_reason: str) -> Fnol:
    fnol = get_fnol(organization_id, fnol_id, for_update=True)
    if fnol.status != FnolStatus.SUBMITTED:
        raise FnolNotSubmittedError(fnol.status)
    fnol.status = FnolStatus.REJECTED
    fnol.rejection_reason = rejection_reason
    db.session.flush()
    return fnol


def _filtered(query: Select, organization_id: int, params: FnolListParams) -> Select:
    query = query.where(Fnol.organization_id == organization_id)
    if params.status is not None:
        query = query.where(Fnol.status == params.status)
    return query


def list_fnols(organization_id: int, params: FnolListParams) -> tuple[list[Fnol], int]:
    """Newest first. Two queries (count, page) whatever the page size."""
    total_count = db.session.scalar(
        _filtered(db.select(db.func.count()).select_from(Fnol), organization_id, params)
    )
    fnols = db.session.scalars(
        _filtered(db.select(Fnol), organization_id, params)
        .order_by(Fnol.id.desc())
        .offset(params.offset)
        .limit(params.page_size)
    ).all()
    return list(fnols), total_count
