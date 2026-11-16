import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.config import TestConfig
from app.errors import (
    AuthenticationError,
    ConflictError,
    DomainError,
    DomainValidationError,
    NotFoundError,
)


class EmailTakenError(ConflictError):
    """A module-specific error: subclasses its category and inherits its status code."""


ERRORS_BY_PATH: dict[str, Exception] = {
    "not-found": NotFoundError("Policy not found"),
    "conflict": ConflictError("Claim is already closed"),
    "validation": DomainValidationError("Loss date is outside the policy period"),
    "authentication": AuthenticationError("Invalid email or password"),
    "module-specific": EmailTakenError("Email is already registered"),
    "uncategorised": DomainError("Something about the domain"),
    "bug": RuntimeError("secret internal detail"),
}


@pytest.fixture
def error_client() -> FlaskClient:
    app: Flask = create_app(TestConfig)

    @app.get("/raise/<path>")
    def raise_error(path: str):
        raise ERRORS_BY_PATH[path]

    return app.test_client()


class TestErrorHandlers:
    @pytest.mark.parametrize(
        ("path", "status", "message"),
        [
            ("not-found", 404, "Policy not found"),
            ("conflict", 409, "Claim is already closed"),
            ("validation", 422, "Loss date is outside the policy period"),
            ("authentication", 401, "Invalid email or password"),
            ("module-specific", 409, "Email is already registered"),
            ("uncategorised", 400, "Something about the domain"),
        ],
    )
    def test_domain_errors_map_to_status_and_message(
        self, error_client: FlaskClient, path: str, status: int, message: str
    ) -> None:
        response = error_client.get(f"/raise/{path}")

        assert response.status_code == status
        assert response.get_json() == {"message": message}

    def test_unexpected_error_is_500_without_details(self, error_client: FlaskClient) -> None:
        response = error_client.get("/raise/bug")

        assert response.status_code == 500
        assert response.get_json() == {"message": "Internal Server Error"}

    def test_unknown_url_is_json_404(self, client: FlaskClient) -> None:
        response = client.get("/api/does-not-exist")

        assert response.status_code == 404
        assert "message" in response.get_json()
