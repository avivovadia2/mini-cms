"""Database-level rules on the policy table: they hold even if the API is bypassed."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.modules.organizations.internal.models.organization import Organization
from app.modules.policies.internal.models.policy import Policy


def _create_organization(name: str) -> Organization:
    organization = Organization(name=name)
    db.session.add(organization)
    db.session.flush()
    return organization


def _new_policy(organization: Organization, policy_number: str = "POL-1", **overrides) -> Policy:
    fields = {
        "organization_id": organization.id,
        "policy_number": policy_number,
        "insured_name": "Acme Corp",
        "line_of_business": "auto",
        "effective_date": date(2026, 1, 1),
        "expiration_date": date(2027, 1, 1),
        **overrides,
    }
    return Policy(**fields)


@pytest.mark.usefixtures("app_context")
class TestPolicyTable:
    def test_status_defaults_to_active(self) -> None:
        policy = _new_policy(_create_organization("Acme"))
        db.session.add(policy)
        db.session.commit()

        assert policy.status == "active"

    def test_policy_number_is_unique_per_organization_ignoring_case(self) -> None:
        organization = _create_organization("Acme")
        db.session.add(_new_policy(organization, "POL-1"))
        db.session.flush()

        db.session.add(_new_policy(organization, "pol-1"))
        with pytest.raises(IntegrityError, match="uq_policy_organization_id_policy_number_lower"):
            db.session.flush()
        db.session.rollback()

    def test_two_organizations_may_share_a_policy_number(self) -> None:
        db.session.add(_new_policy(_create_organization("Acme"), "POL-1"))
        db.session.add(_new_policy(_create_organization("Globex"), "POL-1"))
        db.session.commit()

        assert db.session.scalar(db.select(db.func.count()).select_from(Policy)) == 2

    @pytest.mark.parametrize("expiration", [date(2026, 1, 1), date(2025, 12, 31)])
    def test_expiration_must_be_after_effective(self, expiration: date) -> None:
        policy = _new_policy(
            _create_organization("Acme"),
            effective_date=date(2026, 1, 1),
            expiration_date=expiration,
        )
        db.session.add(policy)
        with pytest.raises(IntegrityError, match="ck_policy_expiration_after_effective"):
            db.session.flush()
        db.session.rollback()
