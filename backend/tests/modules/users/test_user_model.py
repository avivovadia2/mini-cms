"""Database-level rules on the user table (API-level rules are tested with the endpoints)."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.modules.organizations.internal.models.organization import Organization
from app.modules.users.internal.models.user import User


def _create_organization(name: str = "Acme") -> Organization:
    organization = Organization(name=name)
    db.session.add(organization)
    db.session.flush()
    return organization


def _new_user(organization: Organization, email: str = "dana@acme.com") -> User:
    return User(
        organization_id=organization.id,
        email=email,
        full_name="Dana Levi",
        password_hash="not-a-real-hash",
    )


class TestUserTable:
    def test_database_fills_defaults_and_timestamps(self) -> None:
        user = _new_user(_create_organization())
        db.session.add(user)
        db.session.commit()

        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at == user.created_at

    def test_updated_at_changes_on_update(self) -> None:
        user = _new_user(_create_organization())
        db.session.add(user)
        db.session.commit()

        user.full_name = "Dana Cohen"
        db.session.commit()

        assert user.updated_at > user.created_at

    def test_rejects_an_upper_case_email(self) -> None:
        db.session.add(_new_user(_create_organization(), email="Dana@Acme.com"))

        with pytest.raises(IntegrityError, match="ck_user_email_lowercase"):
            db.session.commit()

    def test_email_is_unique_across_organizations(self) -> None:
        db.session.add(_new_user(_create_organization("Acme")))
        db.session.add(_new_user(_create_organization("Globex")))

        with pytest.raises(IntegrityError, match="uq_user_email"):
            db.session.commit()
