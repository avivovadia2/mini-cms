from collections.abc import Callable
from contextlib import AbstractContextManager
from datetime import date, timedelta
from typing import Any

import pytest
from flask.ctx import AppContext
from flask.testing import FlaskClient

from app.extensions import db
from app.modules.fnol.internal.models.fnol import Fnol

FNOLS_URL = "/api/fnols"
POLICIES_URL = "/api/policies"

RegisteredClient = Callable[..., tuple[FlaskClient, dict[str, Any]]]
CountQueries = Callable[[], AbstractContextManager[list[str]]]


def _loss_payload(**overrides: Any) -> dict[str, Any]:
    return {
        "reported_policy_number": "POL-1",
        "reporter_name": "Ron Cohen",
        "reporter_email": "ron@example.com",
        "reporter_phone": "+972-50-000-0000",
        "loss_date": "2026-03-10",
        "loss_description": "Rear-ended at a traffic light.",
        "loss_state": "CA",
        **overrides,
    }


def _report(client: FlaskClient, **overrides: Any) -> dict[str, Any]:
    response = client.post(FNOLS_URL, json=_loss_payload(**overrides))
    assert response.status_code == 201, response.get_json()
    return response.get_json()


def _create_policy(client: FlaskClient, policy_number: str = "POL-1") -> dict[str, Any]:
    response = client.post(
        POLICIES_URL,
        json={
            "policy_number": policy_number,
            "insured_name": "Acme Corp",
            "line_of_business": "auto",
            "effective_date": "2026-01-01",
            "expiration_date": "2027-01-01",
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()


def _reject(client: FlaskClient, fnol_id: int, reason: str = "Duplicate report"):
    return client.post(f"{FNOLS_URL}/{fnol_id}/reject", json={"rejection_reason": reason})


@pytest.fixture
def acme(registered_client: RegisteredClient) -> tuple[FlaskClient, dict[str, Any]]:
    return registered_client("Acme", "dana@acme.com")


class TestReportLoss:
    def test_creates_a_submitted_fnol_matched_to_my_policy(
        self, acme: tuple[FlaskClient, dict[str, Any]], db_read: Callable[[], AppContext]
    ) -> None:
        client, me = acme
        policy = _create_policy(client)

        response = client.post(FNOLS_URL, json=_loss_payload())

        assert response.status_code == 201
        body = response.get_json()
        assert body == {
            "id": body["id"],
            "organization_id": me["organization"]["id"],
            "reported_policy_number": "POL-1",
            "policy_id": policy["id"],
            "reporter_name": "Ron Cohen",
            "reporter_email": "ron@example.com",
            "reporter_phone": "+972-50-000-0000",
            "loss_date": "2026-03-10",
            "loss_description": "Rear-ended at a traffic light.",
            "loss_state": "CA",
            "status": "submitted",
            "rejection_reason": None,
            "submitted_by_id": me["id"],
            "created_at": body["created_at"],
            "policy": policy,
        }
        with db_read():
            fnol = db.session.get(Fnol, body["id"])
            assert fnol.status == "submitted"
            assert fnol.policy_id == policy["id"]
            assert fnol.submitted_by_id == me["id"]

    def test_blank_optional_fields_are_stored_as_null(
        self, acme: tuple[FlaskClient, dict[str, Any]]
    ) -> None:
        client, _ = acme

        body = _report(client, reporter_email="", reporter_phone="  ", loss_state=None)

        assert body["reporter_email"] is None
        assert body["reporter_phone"] is None
        assert body["loss_state"] is None

    def test_ignores_server_owned_fields_in_the_body(
        self, registered_client: RegisteredClient
    ) -> None:
        client_a, me_a = registered_client("Acme", "dana@acme.com")
        _, me_b = registered_client("Globex", "hank@globex.com")

        body = _report(
            client_a,
            organization_id=me_b["organization"]["id"],
            submitted_by_id=me_b["id"],
            status="rejected",
            policy_id=1,
        )

        assert body["organization_id"] == me_a["organization"]["id"]
        assert body["submitted_by_id"] == me_a["id"]
        assert body["status"] == "submitted"
        assert body["policy_id"] is None

    def test_a_loss_dated_today_is_accepted(self, acme: tuple[FlaskClient, dict[str, Any]]) -> None:
        client, _ = acme

        body = _report(client, loss_date=date.today().isoformat())

        assert body["loss_date"] == date.today().isoformat()

    @pytest.mark.parametrize(
        ("overrides", "field"),
        [
            ({"loss_date": (date.today() + timedelta(days=1)).isoformat()}, "loss_date"),
            ({"loss_date": "not-a-date"}, "loss_date"),
            ({"reporter_name": "  "}, "reporter_name"),
            ({"loss_description": ""}, "loss_description"),
            ({"loss_description": "x" * 5001}, "loss_description"),
            ({"reporter_email": "not-an-email"}, "reporter_email"),
        ],
    )
    def test_invalid_input_is_422_and_saves_nothing(
        self,
        acme: tuple[FlaskClient, dict[str, Any]],
        db_read: Callable[[], AppContext],
        overrides: dict[str, Any],
        field: str,
    ) -> None:
        client, _ = acme

        response = client.post(FNOLS_URL, json=_loss_payload(**overrides))

        assert response.status_code == 422
        assert [error["loc"] for error in response.get_json()] == [[field]]
        with db_read():
            assert db.session.scalar(db.select(db.func.count()).select_from(Fnol)) == 0

    def test_missing_fields_are_422(self, acme: tuple[FlaskClient, dict[str, Any]]) -> None:
        client, _ = acme

        response = client.post(FNOLS_URL, json={})

        assert response.status_code == 422
        missing = {error["loc"][0] for error in response.get_json()}
        assert missing == {
            "reported_policy_number",
            "reporter_name",
            "loss_date",
            "loss_description",
        }


class TestPolicyMatching:
    @pytest.mark.parametrize("reported", ["pol-1", "POL-1", "  Pol-1 "])
    def test_matches_ignoring_case_and_surrounding_spaces(
        self, acme: tuple[FlaskClient, dict[str, Any]], reported: str
    ) -> None:
        client, _ = acme
        policy = _create_policy(client, "POL-1")

        body = _report(client, reported_policy_number=reported)

        assert body["policy_id"] == policy["id"]
        assert body["reported_policy_number"] == reported.strip()  # as typed, not the policy's

    def test_never_matches_another_organization_policy(
        self, registered_client: RegisteredClient
    ) -> None:
        client_a, _ = registered_client("Acme", "dana@acme.com")
        client_b, _ = registered_client("Globex", "hank@globex.com")
        _create_policy(client_a, "POL-1")

        body = _report(client_b, reported_policy_number="POL-1")

        assert body["policy_id"] is None
        assert body["policy"] is None

    def test_picks_my_policy_when_both_organizations_have_the_number(
        self, registered_client: RegisteredClient
    ) -> None:
        client_a, _ = registered_client("Acme", "dana@acme.com")
        client_b, _ = registered_client("Globex", "hank@globex.com")
        _create_policy(client_a, "POL-1")
        policy_b = _create_policy(client_b, "POL-1")

        body = _report(client_b, reported_policy_number="POL-1")

        assert body["policy_id"] == policy_b["id"]

    def test_no_match_leaves_the_policy_empty(
        self, acme: tuple[FlaskClient, dict[str, Any]], db_read: Callable[[], AppContext]
    ) -> None:
        client, _ = acme
        _create_policy(client, "POL-1")

        body = _report(client, reported_policy_number="POL-2")

        assert body["policy_id"] is None
        assert body["policy"] is None
        with db_read():
            assert db.session.get(Fnol, body["id"]).policy_id is None

    def test_matching_happens_at_submission_only(
        self, acme: tuple[FlaskClient, dict[str, Any]]
    ) -> None:
        client, _ = acme
        fnol = _report(client, reported_policy_number="POL-1")
        _create_policy(client, "POL-1")  # created after the loss was reported

        body = client.get(f"{FNOLS_URL}/{fnol['id']}").get_json()

        assert body["policy_id"] is None


class TestListFnols:
    def test_lists_newest_first_with_the_matched_policy(
        self, acme: tuple[FlaskClient, dict[str, Any]]
    ) -> None:
        client, _ = acme
        policy = _create_policy(client, "POL-1")
        matched = _report(client, reported_policy_number="POL-1")
        unmatched = _report(client, reported_policy_number="NOPE")

        body = client.get(FNOLS_URL).get_json()

        assert body["total_count"] == 2
        assert body["results"] == [unmatched, matched]
        assert body["results"][1]["policy"] == policy

    def test_filters_by_status(self, acme: tuple[FlaskClient, dict[str, Any]]) -> None:
        client, _ = acme
        submitted = _report(client)
        rejected = _report(client)
        assert _reject(client, rejected["id"]).status_code == 200

        only_submitted = client.get(FNOLS_URL, query_string={"status": "submitted"}).get_json()
        only_rejected = client.get(FNOLS_URL, query_string={"status": "rejected"}).get_json()

        assert [fnol["id"] for fnol in only_submitted["results"]] == [submitted["id"]]
        assert only_submitted["total_count"] == 1
        assert [fnol["id"] for fnol in only_rejected["results"]] == [rejected["id"]]

    def test_paginates_with_the_total_count(self, acme: tuple[FlaskClient, dict[str, Any]]) -> None:
        client, _ = acme
        for _ in range(5):
            _report(client)

        first = client.get(FNOLS_URL, query_string={"page_number": 1, "page_size": 2}).get_json()
        last = client.get(FNOLS_URL, query_string={"page_number": 3, "page_size": 2}).get_json()

        assert len(first["results"]) == 2
        assert len(last["results"]) == 1
        assert first["total_count"] == last["total_count"] == 5

    @pytest.mark.parametrize("query", [{"status": "open"}, {"page_size": 101}])
    def test_invalid_params_are_422(
        self, acme: tuple[FlaskClient, dict[str, Any]], query: dict[str, Any]
    ) -> None:
        client, _ = acme

        response = client.get(FNOLS_URL, query_string=query)

        assert response.status_code == 422

    def test_runs_the_same_number_of_queries_whatever_the_page_size(
        self, acme: tuple[FlaskClient, dict[str, Any]], count_queries: CountQueries
    ) -> None:
        client, _ = acme
        for i in range(10):  # every FNOL matched to a different policy
            _create_policy(client, f"POL-{i}")
            _report(client, reported_policy_number=f"POL-{i}")

        with count_queries() as one_fnol:
            client.get(FNOLS_URL, query_string={"page_size": 1})
        with count_queries() as ten_fnols:
            client.get(FNOLS_URL, query_string={"page_size": 10})

        # No N+1: the matched policies of a page are loaded in one query, however many there are.
        assert len(ten_fnols) == len(one_fnol)


class TestGetFnol:
    def test_returns_the_fnol_with_its_matched_policy(
        self, acme: tuple[FlaskClient, dict[str, Any]]
    ) -> None:
        client, _ = acme
        _create_policy(client)
        fnol = _report(client)

        response = client.get(f"{FNOLS_URL}/{fnol['id']}")

        assert response.status_code == 200
        assert response.get_json() == fnol

    def test_unknown_id_is_404(self, acme: tuple[FlaskClient, dict[str, Any]]) -> None:
        client, _ = acme

        response = client.get(f"{FNOLS_URL}/999999")

        assert response.status_code == 404
        assert response.get_json() == {"message": "FNOL not found"}


class TestRejectFnol:
    def test_rejects_a_submitted_fnol_and_stores_the_reason(
        self, acme: tuple[FlaskClient, dict[str, Any]], db_read: Callable[[], AppContext]
    ) -> None:
        client, _ = acme
        fnol = _report(client)

        response = _reject(client, fnol["id"], "  Not covered by any of our policies  ")

        assert response.status_code == 200
        body = response.get_json()
        assert body == {
            **fnol,
            "status": "rejected",
            "rejection_reason": "Not covered by any of our policies",
        }
        with db_read():
            stored = db.session.get(Fnol, fnol["id"])
            assert stored.status == "rejected"
            assert stored.rejection_reason == "Not covered by any of our policies"

    @pytest.mark.parametrize("payload", [{}, {"rejection_reason": "   "}])
    def test_a_missing_reason_is_422_and_changes_nothing(
        self,
        acme: tuple[FlaskClient, dict[str, Any]],
        db_read: Callable[[], AppContext],
        payload: dict[str, Any],
    ) -> None:
        client, _ = acme
        fnol = _report(client)

        response = client.post(f"{FNOLS_URL}/{fnol['id']}/reject", json=payload)

        assert response.status_code == 422
        with db_read():
            assert db.session.get(Fnol, fnol["id"]).status == "submitted"

    def test_rejecting_twice_is_409_and_keeps_the_first_reason(
        self, acme: tuple[FlaskClient, dict[str, Any]], db_read: Callable[[], AppContext]
    ) -> None:
        client, _ = acme
        fnol = _report(client)
        assert _reject(client, fnol["id"], "First reason").status_code == 200

        response = _reject(client, fnol["id"], "Second reason")

        assert response.status_code == 409
        assert response.get_json() == {"message": "This FNOL is already rejected"}
        with db_read():
            assert db.session.get(Fnol, fnol["id"]).rejection_reason == "First reason"

    def test_unknown_id_is_404(self, acme: tuple[FlaskClient, dict[str, Any]]) -> None:
        client, _ = acme

        response = _reject(client, 999999)

        assert response.status_code == 404


class TestOrganizationIsolation:
    def test_list_never_includes_another_organization_fnols(
        self, registered_client: RegisteredClient
    ) -> None:
        client_a, _ = registered_client("Acme", "dana@acme.com")
        _report(client_a)
        client_b, _ = registered_client("Globex", "hank@globex.com")
        mine = _report(client_b)

        body = client_b.get(FNOLS_URL).get_json()

        assert body["total_count"] == 1
        assert [fnol["id"] for fnol in body["results"]] == [mine["id"]]

    def test_another_organization_fnol_is_404(self, registered_client: RegisteredClient) -> None:
        client_a, _ = registered_client("Acme", "dana@acme.com")
        client_b, _ = registered_client("Globex", "hank@globex.com")
        fnol_a = _report(client_a)

        response = client_b.get(f"{FNOLS_URL}/{fnol_a['id']}")

        # Exactly the same answer as an id that doesn't exist: no hint that it does.
        assert response.status_code == 404
        assert response.get_json() == {"message": "FNOL not found"}

    def test_cannot_reject_another_organization_fnol(
        self, registered_client: RegisteredClient, db_read: Callable[[], AppContext]
    ) -> None:
        client_a, _ = registered_client("Acme", "dana@acme.com")
        client_b, _ = registered_client("Globex", "hank@globex.com")
        fnol_a = _report(client_a)

        response = _reject(client_b, fnol_a["id"])

        assert response.status_code == 404
        with db_read():
            assert db.session.get(Fnol, fnol_a["id"]).status == "submitted"


class TestRequiresSession:
    @pytest.mark.parametrize(
        ("method", "url"),
        [
            ("get", FNOLS_URL),
            ("post", FNOLS_URL),
            ("get", f"{FNOLS_URL}/1"),
            ("post", f"{FNOLS_URL}/1/reject"),
        ],
    )
    def test_is_401_without_a_session(self, client: FlaskClient, method: str, url: str) -> None:
        response = getattr(client, method)(url, json=_loss_payload())

        assert response.status_code == 401
        assert response.get_json() == {"message": "Unauthorized"}
