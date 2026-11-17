from collections.abc import Callable
from typing import Any

import pytest
from flask.ctx import AppContext
from flask.testing import FlaskClient
from werkzeug import security

from app.extensions import db
from app.modules.organizations.internal.models.organization import Organization
from app.modules.users.internal.models.user import User

REGISTER_URL = "/api/auth/register"


def _register_payload(**overrides: Any) -> dict[str, Any]:
    payload = {
        "organization_name": "Acme Insurance",
        "full_name": "Dana Levi",
        "email": "dana@acme.com",
        "password": "correct-horse",
    }
    return {**payload, **overrides}


def _logged_in_user_id(client: FlaskClient) -> str | None:
    with client.session_transaction() as session:
        return session.get("_user_id")


class TestRegister:
    def test_creates_one_organization_and_its_first_user(
        self, client: FlaskClient, db_read: Callable[[], AppContext]
    ) -> None:
        response = client.post(REGISTER_URL, json=_register_payload())

        assert response.status_code == 201
        with db_read():
            organization = db.session.scalars(db.select(Organization)).one()
            user = db.session.scalars(db.select(User)).one()
        assert organization.name == "Acme Insurance"
        assert user.organization_id == organization.id
        assert user.full_name == "Dana Levi"
        assert user.is_active is True
        assert response.get_json() == {
            "id": user.id,
            "email": "dana@acme.com",
            "full_name": "Dana Levi",
            "organization": {"id": organization.id, "name": "Acme Insurance"},
        }

    def test_logs_the_new_user_in(self, client: FlaskClient) -> None:
        response = client.post(REGISTER_URL, json=_register_payload())

        assert _logged_in_user_id(client) == str(response.get_json()["id"])

    def test_stores_the_password_only_as_a_hash(
        self, client: FlaskClient, db_read: Callable[[], AppContext]
    ) -> None:
        response = client.post(REGISTER_URL, json=_register_payload(password="correct-horse"))

        with db_read():
            user = db.session.scalars(db.select(User)).one()
        assert user.password_hash != "correct-horse"
        assert security.check_password_hash(user.password_hash, "correct-horse")
        assert "correct-horse" not in response.get_data(as_text=True)

    def test_stores_the_email_lower_case(
        self, client: FlaskClient, db_read: Callable[[], AppContext]
    ) -> None:
        client.post(REGISTER_URL, json=_register_payload(email="Dana.Levi@Acme.COM"))

        with db_read():
            user = db.session.scalars(db.select(User)).one()
        assert user.email == "dana.levi@acme.com"

    @pytest.mark.parametrize("second_email", ["dana@acme.com", "DANA@acme.com"])
    def test_duplicate_email_is_409_and_leaves_no_organization_behind(
        self, client: FlaskClient, db_read: Callable[[], AppContext], second_email: str
    ) -> None:
        client.post(REGISTER_URL, json=_register_payload(organization_name="First"))

        response = client.post(
            REGISTER_URL, json=_register_payload(organization_name="Second", email=second_email)
        )

        assert response.status_code == 409
        assert response.get_json() == {"message": "This email is already registered"}
        with db_read():
            organization_names = db.session.scalars(db.select(Organization.name)).all()
        assert organization_names == ["First"]

    @pytest.mark.parametrize(
        ("overrides", "field"),
        [
            ({"password": "short"}, "password"),
            ({"email": "not-an-email"}, "email"),
            ({"organization_name": "   "}, "organization_name"),
            ({"full_name": ""}, "full_name"),
        ],
    )
    def test_invalid_input_is_422_and_creates_nothing(
        self,
        client: FlaskClient,
        db_read: Callable[[], AppContext],
        overrides: dict[str, str],
        field: str,
    ) -> None:
        response = client.post(REGISTER_URL, json=_register_payload(**overrides))

        assert response.status_code == 422
        assert [error["loc"] for error in response.get_json()] == [[field]]
        with db_read():
            assert db.session.scalars(db.select(Organization)).all() == []

    def test_missing_fields_are_422(self, client: FlaskClient) -> None:
        response = client.post(REGISTER_URL, json={})

        assert response.status_code == 422
        missing = {error["loc"][0] for error in response.get_json()}
        assert missing == {"organization_name", "full_name", "email", "password"}

    def test_logged_in_user_who_registers_again_is_switched_to_the_new_organization(
        self, client: FlaskClient, db_read: Callable[[], AppContext]
    ) -> None:
        first = client.post(REGISTER_URL, json=_register_payload(email="dana@acme.com"))

        second = client.post(
            REGISTER_URL,
            json=_register_payload(organization_name="Globex", email="dana@globex.com"),
        )

        assert second.status_code == 201
        assert second.get_json()["organization"]["name"] == "Globex"
        assert _logged_in_user_id(client) == str(second.get_json()["id"])
        assert _logged_in_user_id(client) != str(first.get_json()["id"])
        with db_read():
            assert len(db.session.scalars(db.select(Organization)).all()) == 2

    def test_validation_errors_do_not_echo_the_submitted_values(self, client: FlaskClient) -> None:
        response = client.post(REGISTER_URL, json=_register_payload(password="secret7"))

        assert response.status_code == 422
        assert "secret7" not in response.get_data(as_text=True)
        assert response.get_json() == [
            {
                "loc": ["password"],
                "msg": "String should have at least 8 characters",
                "type": "string_too_short",
            }
        ]
