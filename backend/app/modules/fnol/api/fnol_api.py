from flask import Blueprint
from flask_login import current_user, login_required
from spectree import Response

from app.errors import ErrorResponse
from app.extensions import api_spec, db
from app.modules.fnol.interface import FnolServiceInterface
from app.modules.fnol.schemas import (
    FnolListParams,
    FnolResponse,
    RejectFnolRequest,
    ReportLossRequest,
)
from app.registry import get_service
from app.schemas import Page

bp = Blueprint("fnol", __name__, url_prefix="/fnols")

# Every route: @login_required first (401 without a session), and the organization always comes
# from current_user, never from the URL or the body.


@bp.get("")
@login_required
@api_spec.validate(
    query=FnolListParams,
    resp=Response(HTTP_200=Page[FnolResponse], HTTP_401=ErrorResponse),
    tags=["fnol"],
)
def list_fnols(query: FnolListParams):
    """FNOLs of my organization, newest first, each with its matched policy."""
    return get_service(FnolServiceInterface).list_fnols(current_user.organization_id, query)


@bp.post("")
@login_required
@api_spec.validate(
    json=ReportLossRequest,
    resp=Response(HTTP_201=FnolResponse, HTTP_401=ErrorResponse),
    tags=["fnol"],
)
def report_loss(json: ReportLossRequest):
    """Report a loss. It is matched to my organization's policy with that number, if any."""
    fnol = get_service(FnolServiceInterface).report_loss(
        current_user.organization_id, current_user.id, json
    )
    db.session.commit()
    return fnol, 201


@bp.get("/<int:fnol_id>")
@login_required
@api_spec.validate(
    resp=Response(HTTP_200=FnolResponse, HTTP_401=ErrorResponse, HTTP_404=ErrorResponse),
    tags=["fnol"],
)
def get_fnol(fnol_id: int):
    """One FNOL of my organization with its matched policy. 404 for another organization's."""
    return get_service(FnolServiceInterface).get_fnol(current_user.organization_id, fnol_id)


@bp.post("/<int:fnol_id>/reject")
@login_required
@api_spec.validate(
    json=RejectFnolRequest,
    resp=Response(
        HTTP_200=FnolResponse,
        HTTP_401=ErrorResponse,
        HTTP_404=ErrorResponse,
        HTTP_409=ErrorResponse,
    ),
    tags=["fnol"],
)
def reject_fnol(fnol_id: int, json: RejectFnolRequest):
    """Reject a submitted FNOL with a reason. 409 if it is already converted or rejected."""
    fnol = get_service(FnolServiceInterface).reject_fnol(
        current_user.organization_id, fnol_id, json
    )
    db.session.commit()
    return fnol
