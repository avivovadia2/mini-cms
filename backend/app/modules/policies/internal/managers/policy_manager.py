from sqlalchemy import Select

from app.extensions import db
from app.modules.policies.internal.exceptions import (
    PolicyNotFoundError,
    PolicyNumberAlreadyExistsError,
)
from app.modules.policies.internal.models.policy import Policy
from app.modules.policies.schemas import (
    CreatePolicyRequest,
    PolicyListParams,
    UpdatePolicyRequest,
)


def _same_number(policy_number: str):
    """SQL condition: this policy number, ignoring case (matches the unique index)."""
    return db.func.lower(Policy.policy_number) == policy_number.strip().lower()


def _check_number_is_free(organization_id: int, policy_number: str, *, except_id: int | None):
    query = db.select(Policy.id).where(
        Policy.organization_id == organization_id, _same_number(policy_number)
    )
    if except_id is not None:
        query = query.where(Policy.id != except_id)  # editing a policy may keep its own number
    if db.session.scalar(query) is not None:
        raise PolicyNumberAlreadyExistsError()


def create_policy(organization_id: int, params: CreatePolicyRequest) -> Policy:
    _check_number_is_free(organization_id, params.policy_number, except_id=None)
    policy = Policy(organization_id=organization_id, **params.model_dump())
    db.session.add(policy)
    db.session.flush()  # assigns the id and the server defaults (status), without committing
    return policy


def get_policy(organization_id: int, policy_id: int) -> Policy:
    # Filtering by organization in the same query: another organization's policy looks exactly
    # like one that doesn't exist.
    policy = db.session.scalar(
        db.select(Policy).where(Policy.id == policy_id, Policy.organization_id == organization_id)
    )
    if policy is None:
        raise PolicyNotFoundError()
    return policy


def update_policy(organization_id: int, policy_id: int, params: UpdatePolicyRequest) -> Policy:
    policy = get_policy(organization_id, policy_id)
    _check_number_is_free(organization_id, params.policy_number, except_id=policy.id)
    for field, value in params.model_dump().items():
        setattr(policy, field, value)
    db.session.flush()
    return policy


def _filtered(query: Select, organization_id: int, params: PolicyListParams) -> Select:
    query = query.where(Policy.organization_id == organization_id)
    if params.search:
        # icontains with autoescape: a "%" or "_" typed by the user is searched for literally.
        query = query.where(
            Policy.policy_number.icontains(params.search, autoescape=True)
            | Policy.insured_name.icontains(params.search, autoescape=True)
        )
    if params.status is not None:
        query = query.where(Policy.status == params.status)
    if params.line_of_business is not None:
        query = query.where(Policy.line_of_business == params.line_of_business)
    return query


def list_policies(organization_id: int, params: PolicyListParams) -> tuple[list[Policy], int]:
    """Newest first. Two queries (count, page) whatever the page size."""
    total_count = db.session.scalar(
        _filtered(db.select(db.func.count()).select_from(Policy), organization_id, params)
    )
    policies = db.session.scalars(
        _filtered(db.select(Policy), organization_id, params)
        .order_by(Policy.id.desc())
        .offset(params.offset)
        .limit(params.page_size)
    ).all()
    return list(policies), total_count


def get_policies(organization_id: int, policy_ids: set[int]) -> list[Policy]:
    if not policy_ids:
        return []  # skip the query entirely
    return list(
        db.session.scalars(
            db.select(Policy).where(
                Policy.organization_id == organization_id, Policy.id.in_(policy_ids)
            )
        )
    )


def find_by_policy_number(organization_id: int, policy_number: str) -> Policy | None:
    return db.session.scalar(
        db.select(Policy).where(
            Policy.organization_id == organization_id, _same_number(policy_number)
        )
    )
