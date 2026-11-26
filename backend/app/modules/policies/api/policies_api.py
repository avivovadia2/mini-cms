from flask import Blueprint
from flask_login import current_user, login_required
from spectree import Response

from app.errors import ErrorResponse
from app.extensions import api_spec, db
from app.modules.policies.interface import PoliciesServiceInterface
from app.modules.policies.schemas import (
    CreatePolicyRequest,
    PolicyInfo,
    PolicyListParams,
    UpdatePolicyRequest,
)
from app.registry import get_service
from app.schemas import Page

bp = Blueprint("policies", __name__, url_prefix="/policies")

# Every route: @login_required first (401 without a session), and the organization always comes
# from current_user, never from the URL or the body.


@bp.get("")
@login_required
@api_spec.validate(
    query=PolicyListParams,
    resp=Response(HTTP_200=Page[PolicyInfo], HTTP_401=ErrorResponse),
    tags=["policies"],
)
def list_policies(query: PolicyListParams):
    """Policies of my organization, newest first; search and filters combine with AND."""
    return get_service(PoliciesServiceInterface).list_policies(current_user.organization_id, query)


@bp.post("")
@login_required
@api_spec.validate(
    json=CreatePolicyRequest,
    resp=Response(HTTP_201=PolicyInfo, HTTP_401=ErrorResponse, HTTP_409=ErrorResponse),
    tags=["policies"],
)
def create_policy(json: CreatePolicyRequest):
    """Create a policy in my organization. 409 if the number is taken (ignoring case)."""
    policy = get_service(PoliciesServiceInterface).create_policy(current_user.organization_id, json)
    db.session.commit()
    return policy, 201


@bp.get("/<int:policy_id>")
@login_required
@api_spec.validate(
    resp=Response(HTTP_200=PolicyInfo, HTTP_401=ErrorResponse, HTTP_404=ErrorResponse),
    tags=["policies"],
)
def get_policy(policy_id: int):
    """One policy of my organization. 404 for another organization's policy."""
    return get_service(PoliciesServiceInterface).get_policy(current_user.organization_id, policy_id)


@bp.put("/<int:policy_id>")
@login_required
@api_spec.validate(
    json=UpdatePolicyRequest,
    resp=Response(
        HTTP_200=PolicyInfo,
        HTTP_401=ErrorResponse,
        HTTP_404=ErrorResponse,
        HTTP_409=ErrorResponse,
    ),
    tags=["policies"],
)
def update_policy(policy_id: int, json: UpdatePolicyRequest):
    """Replace a policy's editable fields. Cancel by sending status "cancelled"."""
    policy = get_service(PoliciesServiceInterface).update_policy(
        current_user.organization_id, policy_id, json
    )
    db.session.commit()
    return policy
