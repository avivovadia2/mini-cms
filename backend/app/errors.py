"""Domain exceptions and the one place that turns them into HTTP responses.

Managers and services raise these; they know nothing about HTTP. Each module subclasses the
category that fits, e.g. `class EmailAlreadyRegisteredError(ConflictError)`, and the handler
below maps the category to a status code. Routes never catch them.
"""

import logging

from flask import Flask, Response, jsonify
from pydantic import BaseModel
from werkzeug.exceptions import HTTPException


class DomainError(Exception):
    """Base class for expected business errors. `message` is safe to show to the user."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    """The resource doesn't exist, or belongs to another organization (never confirm which)."""


class ConflictError(DomainError):
    """The request clashes with current state: a duplicate, or a disallowed status transition."""


class DomainValidationError(DomainError):
    """The input is well-formed but breaks a business rule."""


class AuthenticationError(DomainError):
    """The caller could not be authenticated, e.g. wrong email or password."""


class ErrorResponse(BaseModel):
    """The body of every error response, for the OpenAPI docs."""

    message: str


STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFoundError: 404,
    ConflictError: 409,
    DomainValidationError: 422,
    AuthenticationError: 401,
}


def _status_for(error: DomainError) -> int:
    for error_class in type(error).__mro__:
        if error_class in STATUS_BY_ERROR:
            return STATUS_BY_ERROR[error_class]
    return 400


def register_error_handlers(app: Flask) -> None:
    """Every error leaves the API as JSON: `{"message": "..."}` with the matching status code."""

    @app.errorhandler(DomainError)
    def handle_domain_error(error: DomainError) -> tuple[Response, int]:
        return jsonify(message=error.message), _status_for(error)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> tuple[Response, int]:
        # Flask's own errors (unknown URL, wrong method, ...), as JSON instead of an HTML page.
        return jsonify(message=error.description), error.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> tuple[Response, int]:
        # A bug, not a business error: log the traceback, but don't leak details to the client.
        logging.exception("Unhandled exception")
        return jsonify(message="Internal Server Error"), 500
