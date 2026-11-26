"""Database-level rules on the fnol table: they hold even if the API is bypassed."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.modules.fnol.internal.models.fnol import Fnol
from app.modules.organizations.internal.models.organization import Organization
from app.modules.users.internal.models.user import User


def _new_fnol(**overrides) -> Fnol:
    organization = Organization(name="Acme")
    db.session.add(organization)
    db.session.flush()
    user = User(
        organization_id=organization.id,
        email="dana@acme.com",
        full_name="Dana Levi",
        password_hash="not-a-real-hash",
    )
    db.session.add(user)
    db.session.flush()
    fields = {
        "organization_id": organization.id,
        "submitted_by_id": user.id,
        "reported_policy_number": "POL-1",
        "reporter_name": "Ron Cohen",
        "loss_date": date(2026, 3, 10),
        "loss_description": "Rear-ended at a traffic light.",
        **overrides,
    }
    return Fnol(**fields)


@pytest.mark.usefixtures("app_context")
class TestFnolTable:
    def test_status_defaults_to_submitted(self) -> None:
        fnol = _new_fnol()
        db.session.add(fnol)
        db.session.commit()

        assert fnol.status == "submitted"

    @pytest.mark.parametrize(
        ("status", "rejection_reason"),
        [("rejected", None), ("submitted", "A leftover reason"), ("converted", "A reason")],
    )
    def test_a_rejection_reason_exactly_when_rejected(
        self, status: str, rejection_reason: str | None
    ) -> None:
        db.session.add(_new_fnol(status=status, rejection_reason=rejection_reason))

        with pytest.raises(IntegrityError, match="ck_fnol_rejection_reason_iff_rejected"):
            db.session.commit()
        db.session.rollback()
