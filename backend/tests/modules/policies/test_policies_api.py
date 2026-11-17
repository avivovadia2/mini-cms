from collections.abc import Callable
from typing import Any

import pytest
from flask.ctx import AppContext
from flask.testing import FlaskClient

from app.extensions import db
from app.modules.policies.internal.models.policy import Policy

POLICIES_URL = "/api/policies"

RegisteredClient = Callable[..., tuple[FlaskClient, dict[str, Any]]]


def _policy_payload(**overrides: Any) -> dict[str, Any]:
    return {
        "policy_number": "POL-1",
        "insured_name": "Acme Corp",
        "line_of_business": "auto",
        "effective_date": "2026-01-01",
        "expiration_date": "2027-01-01",
        **overrides,
    }


def _create(client: FlaskClient, **overrides: Any) -> dict[str, Any]:
    response = client.post(POLICIES_URL, json=_policy_payload(**overrides))
    assert response.status_code == 201, response.get_json()
    return response.get_json()


def _update_payload(policy: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    fields = ("policy_number", "insured_name", "line_of_business", "effective_date")
    payload = {field: policy[field] for field in fields}
    return {
        **payload,
        "expiration_date": policy["expiration_date"],
        "status": policy["status"],
        **overrides,
    }


@pytest.fixture
def acme(registered_client: RegisteredClient) -> tuple[FlaskClient, dict[str, Any]]:
    return registered_client("Acme", "dana@acme.com")


class TestCreatePolicy:
    def test_creates_an_active_policy_in_my_organization(
        self, acme: tuple[FlaskClient, dict[str, Any]], db_read: Callable[[], AppContext]
    ) -> None:
        client, me = acme

        response = client.post(POLICIES_URL, json=_policy_payload(policy_number="  POL-1 "))

        assert response.status_code == 201
        body = response.get_json()
        assert body == {
            "id": body["id"],
            "organization_id": me["organization"]["id"],
            "policy_number": "POL-1",  # trimmed
            "insured_name": "Acme Corp",
            "line_of_business": "auto",
            "effective_date": "2026-01-01",
            "expiration_date": "2027-01-01",
            "status": "active",
        }
        with db_read():
            policy = db.session.get(Policy, body["id"])
            assert policy.organization_id == me["organization"]["id"]
            assert policy.status == "active"

    @pytest.mark.parametrize("number", ["POL-1", "pol-1"])
    def test_duplicate_number_in_my_organization_is_409(
        self,
        acme: tuple[FlaskClient, dict[str, Any]],
        db_read: Callable[[], AppContext],
        number: str,
    ) -> None:
        client, _ = acme
        _create(client, policy_number="POL-1")

        response = client.post(POLICIES_URL, json=_policy_payload(policy_number=number))

        assert response.status_code == 409
        assert response.get_json() == {"message": "A policy with this number already exists"}
        with db_read():
            assert db.session.scalar(db.select(db.func.count()).select_from(Policy)) == 1

    def test_another_organization_may_use_the_same_number(
        self, registered_client: RegisteredClient
    ) -> None:
        client_a, _ = registered_client("Acme", "dana@acme.com")
        client_b, _ = registered_client("Globex", "hank@globex.com")
        _create(client_a, policy_number="POL-1")

        response = client_b.post(POLICIES_URL, json=_policy_payload(policy_number="POL-1"))

        assert response.status_code == 201

    @pytest.mark.parametrize("expiration", ["2026-01-01", "2025-06-01"])
    def test_expiration_not_after_effective_is_422(
        self, acme: tuple[FlaskClient, dict[str, Any]], expiration: str
    ) -> None:
        client, _ = acme

        response = client.post(
            POLICIES_URL,
            json=_policy_payload(effective_date="2026-01-01", expiration_date=expiration),
        )

        assert response.status_code == 422
        assert "expiration_date must be after effective_date" in response.get_data(as_text=True)

    @pytest.mark.parametrize(
        ("overrides", "field"),
        [
            ({"policy_number": "  "}, "policy_number"),
            ({"insured_name": ""}, "insured_name"),
            ({"line_of_business": "marine"}, "line_of_business"),
            ({"effective_date": "not-a-date"}, "effective_date"),
        ],
    )
    def test_invalid_fields_are_422(
        self, acme: tuple[FlaskClient, dict[str, Any]], overrides: dict[str, str], field: str
    ) -> None:
        client, _ = acme

        response = client.post(POLICIES_URL, json=_policy_payload(**overrides))

        assert response.status_code == 422
        assert [error["loc"] for error in response.get_json()] == [[field]]

    def test_a_status_in_the_body_is_ignored(
        self, acme: tuple[FlaskClient, dict[str, Any]]
    ) -> None:
        client, _ = acme

        policy = _create(client, status="cancelled")

        assert policy["status"] == "active"


class TestUpdatePolicy:
    def test_replaces_the_editable_fields(self, acme: tuple[FlaskClient, dict[str, Any]]) -> None:
        client, _ = acme
        policy = _create(client)

        response = client.put(
            f"{POLICIES_URL}/{policy['id']}",
            json=_update_payload(policy, insured_name="Acme Holdings", line_of_business="property"),
        )

        assert response.status_code == 200
        assert response.get_json() == {
            **policy,
            "insured_name": "Acme Holdings",
            "line_of_business": "property",
        }

    def test_cancel_and_reactivate(
        self, acme: tuple[FlaskClient, dict[str, Any]], db_read: Callable[[], AppContext]
    ) -> None:
        client, _ = acme
        policy = _create(client)
        url = f"{POLICIES_URL}/{policy['id']}"

        cancelled = client.put(url, json=_update_payload(policy, status="cancelled")).get_json()
        with db_read():
            assert db.session.get(Policy, policy["id"]).status == "cancelled"
        reactivated = client.put(url, json=_update_payload(policy, status="active")).get_json()

        assert cancelled["status"] == "cancelled"
        assert reactivated["status"] == "active"

    def test_may_keep_its_own_number_in_a_different_case(
        self, acme: tuple[FlaskClient, dict[str, Any]]
    ) -> None:
        client, _ = acme
        policy = _create(client, policy_number="POL-1")

        response = client.put(
            f"{POLICIES_URL}/{policy['id']}", json=_update_payload(policy, policy_number="pol-1")
        )

        assert response.status_code == 200
        assert response.get_json()["policy_number"] == "pol-1"

    def test_taking_another_policy_number_is_409(
        self, acme: tuple[FlaskClient, dict[str, Any]], db_read: Callable[[], AppContext]
    ) -> None:
        client, _ = acme
        _create(client, policy_number="POL-1")
        second = _create(client, policy_number="POL-2")

        response = client.put(
            f"{POLICIES_URL}/{second['id']}", json=_update_payload(second, policy_number="Pol-1")
        )

        assert response.status_code == 409
        with db_read():
            assert db.session.get(Policy, second["id"]).policy_number == "POL-2"

    def test_expiration_not_after_effective_is_422(
        self, acme: tuple[FlaskClient, dict[str, Any]]
    ) -> None:
        client, _ = acme
        policy = _create(client)

        response = client.put(
            f"{POLICIES_URL}/{policy['id']}",
            json=_update_payload(policy, expiration_date=policy["effective_date"]),
        )

        assert response.status_code == 422

    def test_unknown_id_is_404(self, acme: tuple[FlaskClient, dict[str, Any]]) -> None:
        client, _ = acme

        response = client.put(
            f"{POLICIES_URL}/999999", json={**_policy_payload(), "status": "active"}
        )

        assert response.status_code == 404
        assert response.get_json() == {"message": "Policy not found"}


class TestGetPolicy:
    def test_returns_a_policy_of_my_organization(
        self, acme: tuple[FlaskClient, dict[str, Any]]
    ) -> None:
        client, _ = acme
        policy = _create(client)

        response = client.get(f"{POLICIES_URL}/{policy['id']}")

        assert response.status_code == 200
        assert response.get_json() == policy

    def test_unknown_id_is_404(self, acme: tuple[FlaskClient, dict[str, Any]]) -> None:
        client, _ = acme

        assert client.get(f"{POLICIES_URL}/999999").status_code == 404


class TestListPolicies:
    @pytest.fixture
    def three_policies(self, acme: tuple[FlaskClient, dict[str, Any]]) -> FlaskClient:
        client, _ = acme
        _create(client, policy_number="AUTO-100", insured_name="Dana Levi")
        _create(
            client, policy_number="PROP-200", insured_name="Acme Corp", line_of_business="property"
        )
        cancelled = _create(client, policy_number="AUTO-300", insured_name="Hank Hill")
        client.put(
            f"{POLICIES_URL}/{cancelled['id']}", json=_update_payload(cancelled, status="cancelled")
        )
        return client

    @staticmethod
    def _numbers(client: FlaskClient, **query: Any) -> tuple[list[str], int]:
        response = client.get(POLICIES_URL, query_string=query)
        assert response.status_code == 200, response.get_json()
        body = response.get_json()
        return [policy["policy_number"] for policy in body["results"]], body["total_count"]

    def test_lists_newest_first_with_the_total_count(self, three_policies: FlaskClient) -> None:
        assert self._numbers(three_policies) == (["AUTO-300", "PROP-200", "AUTO-100"], 3)

    @pytest.mark.parametrize(
        ("query", "expected"),
        [
            ({"search": "auto-"}, ["AUTO-300", "AUTO-100"]),  # policy number, any case
            ({"search": "ACME"}, ["PROP-200"]),  # insured name, any case
            ({"search": "%"}, []),  # searched literally, not as a wildcard
            ({"status": "cancelled"}, ["AUTO-300"]),
            ({"line_of_business": "property"}, ["PROP-200"]),
            ({"search": "auto", "status": "active"}, ["AUTO-100"]),  # filters combine with AND
        ],
    )
    def test_search_and_filters(
        self, three_policies: FlaskClient, query: dict[str, str], expected: list[str]
    ) -> None:
        numbers, total_count = self._numbers(three_policies, **query)

        assert numbers == expected
        assert total_count == len(expected)

    def test_paginates_with_the_total_count(self, three_policies: FlaskClient) -> None:
        first = self._numbers(three_policies, page_number=1, page_size=2)
        second = self._numbers(three_policies, page_number=2, page_size=2)

        assert first == (["AUTO-300", "PROP-200"], 3)
        assert second == (["AUTO-100"], 3)

    @pytest.mark.parametrize(
        "query", [{"status": "expired"}, {"line_of_business": "marine"}, {"page_size": 101}]
    )
    def test_invalid_params_are_422(
        self, acme: tuple[FlaskClient, dict[str, Any]], query: dict[str, Any]
    ) -> None:
        client, _ = acme

        assert client.get(POLICIES_URL, query_string=query).status_code == 422


class TestOrganizationIsolation:
    @pytest.fixture
    def acme_policy_and_globex(
        self, registered_client: RegisteredClient
    ) -> tuple[dict[str, Any], FlaskClient]:
        client_a, _ = registered_client("Acme", "dana@acme.com")
        client_b, _ = registered_client("Globex", "hank@globex.com")
        return _create(client_a, policy_number="POL-1"), client_b

    def test_another_organization_policy_is_404(
        self, acme_policy_and_globex: tuple[dict[str, Any], FlaskClient]
    ) -> None:
        policy, globex = acme_policy_and_globex

        response = globex.get(f"{POLICIES_URL}/{policy['id']}")

        assert response.status_code == 404
        assert response.get_json() == {"message": "Policy not found"}

    def test_another_organization_policy_cannot_be_edited(
        self,
        acme_policy_and_globex: tuple[dict[str, Any], FlaskClient],
        db_read: Callable[[], AppContext],
    ) -> None:
        policy, globex = acme_policy_and_globex

        response = globex.put(
            f"{POLICIES_URL}/{policy['id']}", json=_update_payload(policy, status="cancelled")
        )

        assert response.status_code == 404
        with db_read():
            assert db.session.get(Policy, policy["id"]).status == "active"

    def test_list_never_includes_another_organization_policies(
        self, acme_policy_and_globex: tuple[dict[str, Any], FlaskClient]
    ) -> None:
        _, globex = acme_policy_and_globex

        body = globex.get(POLICIES_URL, query_string={"search": "POL"}).get_json()

        assert body == {"results": [], "total_count": 0}


class TestRequiresSession:
    @pytest.mark.parametrize(
        ("method", "url"),
        [
            ("get", POLICIES_URL),
            ("post", POLICIES_URL),
            ("get", f"{POLICIES_URL}/1"),
            ("put", f"{POLICIES_URL}/1"),
        ],
    )
    def test_is_401_without_a_session(self, client: FlaskClient, method: str, url: str) -> None:
        response = getattr(client, method)(url, json=_policy_payload())

        assert response.status_code == 401
