from collections.abc import Callable
from typing import Any

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskClient

from app.extensions import db
from app.modules.users.internal.models.user import User

LOGIN_URL = "/api/auth/login"
LOGOUT_URL = "/api/auth/logout"
ME_URL = "/api/auth/me"

EMAIL = "dana@acme.com"
PASSWORD = "correct-horse"


@pytest.fixture
def registered_user(app: Flask) -> dict[str, Any]:
    """Register through the API with a separate client, so the test's `client` has no session."""
    response = app.test_client().post(
        "/api/auth/register",
        json={
            "organization_name": "Acme Insurance",
            "full_name": "Dana Levi",
            "email": EMAIL,
            "password": PASSWORD,
        },
    )
    assert response.status_code == 201
    return response.get_json()


def _deactivate(db_read: Callable[[], AppContext], user_id: int) -> None:
    with db_read():
        db.session.get(User, user_id).is_active = False
        db.session.commit()


def _logged_in_user_id(client: FlaskClient) -> str | None:
    with client.session_transaction() as session:
        return session.get("_user_id")


@pytest.mark.usefixtures("registered_user")
class TestLogin:
    def test_valid_credentials_log_the_user_in(
        self, client: FlaskClient, registered_user: dict[str, Any]
    ) -> None:
        response = client.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD})

        assert response.status_code == 200
        assert response.get_json() == registered_user
        assert _logged_in_user_id(client) == str(registered_user["id"])

    def test_email_is_case_insensitive(self, client: FlaskClient) -> None:
        response = client.post(LOGIN_URL, json={"email": "Dana@ACME.com", "password": PASSWORD})

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "credentials",
        [
            {"email": EMAIL, "password": "wrong-password"},
            {"email": "nobody@acme.com", "password": PASSWORD},
        ],
        ids=["wrong password", "unknown email"],
    )
    def test_bad_credentials_are_401_and_do_not_log_in(
        self, client: FlaskClient, credentials: dict[str, str]
    ) -> None:
        response = client.post(LOGIN_URL, json=credentials)

        assert response.status_code == 401
        assert response.get_json() == {"message": "Invalid email or password"}
        assert _logged_in_user_id(client) is None

    def test_inactive_user_cannot_log_in(
        self,
        client: FlaskClient,
        db_read: Callable[[], AppContext],
        registered_user: dict[str, Any],
    ) -> None:
        _deactivate(db_read, registered_user["id"])

        response = client.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD})

        # Same answer as a wrong password: don't reveal that the account exists.
        assert response.status_code == 401
        assert response.get_json() == {"message": "Invalid email or password"}
        assert _logged_in_user_id(client) is None

    def test_missing_fields_are_422(self, client: FlaskClient) -> None:
        response = client.post(LOGIN_URL, json={})

        assert response.status_code == 422
        assert {error["loc"][0] for error in response.get_json()} == {"email", "password"}


class TestMe:
    def test_returns_the_logged_in_user_and_organization(
        self, client: FlaskClient, registered_user: dict[str, Any]
    ) -> None:
        client.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD})

        response = client.get(ME_URL)

        assert response.status_code == 200
        assert response.get_json() == registered_user

    def test_is_401_without_a_session(self, client: FlaskClient) -> None:
        response = client.get(ME_URL)

        assert response.status_code == 401
        assert response.get_json() == {"message": "Unauthorized"}

    def test_is_401_once_the_user_is_deactivated(
        self,
        client: FlaskClient,
        db_read: Callable[[], AppContext],
        registered_user: dict[str, Any],
    ) -> None:
        client.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD})
        _deactivate(db_read, registered_user["id"])

        response = client.get(ME_URL)

        assert response.status_code == 401


@pytest.mark.usefixtures("registered_user")
class TestLogout:
    def test_ends_the_session(self, client: FlaskClient) -> None:
        client.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD})

        response = client.post(LOGOUT_URL)

        assert response.status_code == 204
        assert _logged_in_user_id(client) is None
        assert client.get(ME_URL).status_code == 401

    def test_is_401_without_a_session(self, client: FlaskClient) -> None:
        response = client.post(LOGOUT_URL)

        assert response.status_code == 401
