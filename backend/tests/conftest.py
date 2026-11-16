"""Shared pytest fixtures: a real Postgres test database, built by the Alembic migrations.

- Once per test session: wipe the test database's schema and run every migration (`upgrade`),
  so the migrations themselves are tested from scratch on every run.
- After each test: truncate all tables. Tests may commit for real (e.g. register's single
  transaction), so wrapping each test in a rolled-back transaction would not work here.
"""

from collections.abc import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_migrate import upgrade
from sqlalchemy import text

from app import create_app
from app.config import TestConfig
from app.extensions import db


@pytest.fixture(scope="session")
def app() -> Iterator[Flask]:
    app = create_app(TestConfig)
    with app.app_context():
        db.session.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        db.session.commit()
        upgrade()
        yield app
        db.session.remove()


@pytest.fixture(autouse=True)
def clean_tables(app: Flask) -> Iterator[None]:
    yield
    db.session.rollback()
    table_names = ", ".join(f'"{table.name}"' for table in db.metadata.sorted_tables)
    if table_names:
        db.session.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))
        db.session.commit()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A client with no session. Each test gets its own (cookies are not shared between tests)."""
    return app.test_client()
