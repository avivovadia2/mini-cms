"""Shared pytest fixtures: a real Postgres test database, built by the Alembic migrations.

- Once per test session: wipe the test database's schema and run every migration (`upgrade`),
  so the migrations themselves are tested from scratch on every run.
- After each test: truncate all tables. Requests commit for real (e.g. register's single
  transaction), so wrapping each test in a rolled-back transaction would not work here.
- No app context is held open while a test runs. Each request then gets its own database
  session, which is rolled back and closed when the request ends, exactly as in production.
  To check what a request really committed, read the database in a fresh context (`db_read`).
"""

from collections.abc import Callable, Iterator
from typing import Any

import pytest
from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskClient
from flask_migrate import upgrade
from sqlalchemy import text

from app import create_app
from app.config import TestConfig
from app.extensions import db


@pytest.fixture(scope="session")
def app() -> Flask:
    app = create_app(TestConfig)
    with app.app_context():
        db.session.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        db.session.commit()
        upgrade()
    return app


@pytest.fixture(autouse=True)
def clean_tables(app: Flask) -> Iterator[None]:
    yield
    with app.app_context():
        table_names = ", ".join(f'"{table.name}"' for table in db.metadata.sorted_tables)
        if table_names:
            db.session.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))
            db.session.commit()


@pytest.fixture
def app_context(app: Flask) -> Iterator[None]:
    """For tests that use db.session directly (model tests), not through requests."""
    with app.app_context():
        yield


@pytest.fixture
def db_read(app: Flask) -> Callable[[], AppContext]:
    """A fresh context for assertions: it only sees data that requests actually committed.

    Use it as a context manager in the test: `with db_read(): ...`.
    """
    return app.app_context


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A client with no session. Each test gets its own (cookies are not shared between tests)."""
    return app.test_client()


@pytest.fixture
def registered_client(app: Flask) -> Callable[..., tuple[FlaskClient, dict[str, Any]]]:
    """Register a new organization through the API; returns its logged-in client and `me` body.

    Call it twice for two organizations: `client_a, me_a = registered_client("Acme", "a@acme.com")`.
    """

    def register(organization_name: str, email: str) -> tuple[FlaskClient, dict[str, Any]]:
        client = app.test_client()
        response = client.post(
            "/api/auth/register",
            json={
                "organization_name": organization_name,
                "full_name": "First User",
                "email": email,
                "password": "correct-horse",
            },
        )
        assert response.status_code == 201
        return client, response.get_json()

    return register
