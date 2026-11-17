from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskClient
from sqlalchemy import event
from werkzeug import security

from app.extensions import db
from app.modules.users.internal.models.user import User

USERS_URL = "/api/users"

RegisteredClient = Callable[..., tuple[FlaskClient, dict[str, Any]]]


def _add_user_payload(**overrides: Any) -> dict[str, Any]:
    return {
        "email": "new.user@acme.com",
        "full_name": "New User",
        "password": "another-horse",
        **overrides,
    }


def _add_users(client: FlaskClient, count: int) -> list[dict[str, Any]]:
    added = []
    for i in range(count):
        response = client.post(USERS_URL, json=_add_user_payload(email=f"user{i}@acme.com"))
        assert response.status_code == 201
        added.append(response.get_json())
    return added


@contextmanager
def _count_queries(app: Flask) -> Iterator[list[str]]:
    """Collect every SQL statement sent to the database while the block runs."""
    statements: list[str] = []

    def record(conn, cursor, statement, *args) -> None:
        statements.append(statement)

    with app.app_context():
        engine = db.engine
    event.listen(engine, "before_cursor_execute", record)
    try:
        yield statements
    finally:
        event.remove(engine, "before_cursor_execute", record)


class TestListUsers:
    def test_lists_my_organization_users_oldest_first(
        self, registered_client: RegisteredClient
    ) -> None:
        client, me = registered_client("Acme", "dana@acme.com")
        added = _add_users(client, 2)

        response = client.get(USERS_URL)

        assert response.status_code == 200
        body = response.get_json()
        assert body["total_count"] == 3
        assert [user["id"] for user in body["results"]] == [me["id"]] + [u["id"] for u in added]
        assert body["results"][0] == {
            "id": me["id"],
            "organization_id": me["organization"]["id"],
            "email": "dana@acme.com",
            "full_name": "First User",
            "is_active": True,
        }

    def test_paginates_with_the_total_count(self, registered_client: RegisteredClient) -> None:
        client, _ = registered_client("Acme", "dana@acme.com")
        _add_users(client, 4)  # 5 users in total

        first = client.get(USERS_URL, query_string={"page_number": 1, "page_size": 2}).get_json()
        last = client.get(USERS_URL, query_string={"page_number": 3, "page_size": 2}).get_json()
        beyond = client.get(USERS_URL, query_string={"page_number": 4, "page_size": 2}).get_json()

        assert len(first["results"]) == 2
        assert len(last["results"]) == 1
        assert beyond["results"] == []
        assert first["total_count"] == last["total_count"] == beyond["total_count"] == 5

    @pytest.mark.parametrize(
        "query", [{"page_size": 101}, {"page_size": 0}, {"page_number": 0}, {"page_number": "x"}]
    )
    def test_invalid_page_params_are_422(
        self, registered_client: RegisteredClient, query: dict[str, Any]
    ) -> None:
        client, _ = registered_client("Acme", "dana@acme.com")

        response = client.get(USERS_URL, query_string=query)

        assert response.status_code == 422

    def test_runs_the_same_number_of_queries_whatever_the_page_size(
        self, app: Flask, registered_client: RegisteredClient
    ) -> None:
        client, _ = registered_client("Acme", "dana@acme.com")
        _add_users(client, 9)

        with _count_queries(app) as one_user:
            client.get(USERS_URL, query_string={"page_size": 1})
        with _count_queries(app) as ten_users:
            client.get(USERS_URL, query_string={"page_size": 10})

        # No N+1: listing 10 users costs no more queries than listing 1.
        assert len(ten_users) == len(one_user)


class TestGetUser:
    def test_returns_a_user_of_my_organization(self, registered_client: RegisteredClient) -> None:
        client, _ = registered_client("Acme", "dana@acme.com")
        [added] = _add_users(client, 1)

        response = client.get(f"{USERS_URL}/{added['id']}")

        assert response.status_code == 200
        assert response.get_json() == added

    def test_unknown_id_is_404(self, registered_client: RegisteredClient) -> None:
        client, _ = registered_client("Acme", "dana@acme.com")

        response = client.get(f"{USERS_URL}/999999")

        assert response.status_code == 404
        assert response.get_json() == {"message": "User not found"}


class TestAddUser:
    def test_adds_the_user_to_my_organization_with_a_hashed_password(
        self, registered_client: RegisteredClient, db_read: Callable[[], AppContext]
    ) -> None:
        client, me = registered_client("Acme", "dana@acme.com")

        response = client.post(
            USERS_URL, json=_add_user_payload(email="New.User@Acme.com", password="another-horse")
        )

        assert response.status_code == 201
        body = response.get_json()
        with db_read():
            user = db.session.get(User, body["id"])
            assert user.organization_id == me["organization"]["id"]
            assert user.email == "new.user@acme.com"
            assert security.check_password_hash(user.password_hash, "another-horse")
        assert body == {
            "id": user.id,
            "organization_id": me["organization"]["id"],
            "email": "new.user@acme.com",
            "full_name": "New User",
            "is_active": True,
        }
        assert "another-horse" not in response.get_data(as_text=True)

    def test_ignores_an_organization_id_in_the_body(
        self, registered_client: RegisteredClient
    ) -> None:
        client_a, me_a = registered_client("Acme", "dana@acme.com")
        _, me_b = registered_client("Globex", "hank@globex.com")

        response = client_a.post(
            USERS_URL, json=_add_user_payload(organization_id=me_b["organization"]["id"])
        )

        assert response.status_code == 201
        assert response.get_json()["organization_id"] == me_a["organization"]["id"]

    @pytest.mark.parametrize("email", ["dana@acme.com", "HANK@globex.com"])
    def test_duplicate_email_in_any_organization_is_409(
        self,
        registered_client: RegisteredClient,
        db_read: Callable[[], AppContext],
        email: str,
    ) -> None:
        client, _ = registered_client("Acme", "dana@acme.com")
        registered_client("Globex", "hank@globex.com")

        response = client.post(USERS_URL, json=_add_user_payload(email=email))

        assert response.status_code == 409
        assert response.get_json() == {"message": "This email is already registered"}
        with db_read():
            assert db.session.scalar(db.select(db.func.count()).select_from(User)) == 2

    @pytest.mark.parametrize(
        ("overrides", "field"),
        [
            ({"password": "short"}, "password"),
            ({"email": "not-an-email"}, "email"),
            ({"full_name": "  "}, "full_name"),
        ],
    )
    def test_invalid_input_is_422(
        self,
        registered_client: RegisteredClient,
        db_read: Callable[[], AppContext],
        overrides: dict[str, str],
        field: str,
    ) -> None:
        client, _ = registered_client("Acme", "dana@acme.com")

        response = client.post(USERS_URL, json=_add_user_payload(**overrides))

        assert response.status_code == 422
        assert [error["loc"] for error in response.get_json()] == [[field]]
        with db_read():
            assert db.session.scalar(db.select(db.func.count()).select_from(User)) == 1

    def test_missing_fields_are_422(self, registered_client: RegisteredClient) -> None:
        client, _ = registered_client("Acme", "dana@acme.com")

        response = client.post(USERS_URL, json={})

        assert response.status_code == 422
        missing = {error["loc"][0] for error in response.get_json()}
        assert missing == {"email", "full_name", "password"}


class TestOrganizationIsolation:
    def test_list_never_includes_another_organization_users(
        self, registered_client: RegisteredClient
    ) -> None:
        client_a, _ = registered_client("Acme", "dana@acme.com")
        _add_users(client_a, 2)
        client_b, me_b = registered_client("Globex", "hank@globex.com")

        body = client_b.get(USERS_URL).get_json()

        assert body["total_count"] == 1
        assert [user["id"] for user in body["results"]] == [me_b["id"]]

    def test_another_organization_user_is_404(self, registered_client: RegisteredClient) -> None:
        client_a, me_a = registered_client("Acme", "dana@acme.com")
        client_b, _ = registered_client("Globex", "hank@globex.com")

        response = client_b.get(f"{USERS_URL}/{me_a['id']}")

        # Exactly the same answer as an id that doesn't exist: no hint that it does.
        assert response.status_code == 404
        assert response.get_json() == {"message": "User not found"}


class TestRequiresSession:
    @pytest.mark.parametrize(
        ("method", "url"),
        [("get", USERS_URL), ("get", f"{USERS_URL}/1"), ("post", USERS_URL)],
    )
    def test_is_401_without_a_session(self, client: FlaskClient, method: str, url: str) -> None:
        response = getattr(client, method)(url, json=_add_user_payload())

        assert response.status_code == 401
        assert response.get_json() == {"message": "Unauthorized"}
