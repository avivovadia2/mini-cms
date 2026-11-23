from flask.testing import FlaskClient


class TestHealth:
    def test_returns_ok_when_database_is_reachable(self, client: FlaskClient) -> None:
        response = client.get("/api/health")

        assert response.status_code == 200
        assert response.get_json() == {"status": "ok", "database": "ok"}
