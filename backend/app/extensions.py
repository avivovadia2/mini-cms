"""Extension instances, created unbound and attached to the app in create_app().

Keeping them here (not in __init__.py) lets models and routes import `db` without circular imports.
"""

import json
from typing import Any

from flask import Request, Response, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from pydantic import ValidationError
from spectree import SpecTree
from sqlalchemy import MetaData

# Deterministic constraint names, so Alembic migrations can refer to (and drop) them reliably.
# Same convention as the CMS.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

db = SQLAlchemy(metadata=MetaData(naming_convention=NAMING_CONVENTION))
migrate = Migrate()
login_manager = LoginManager()


def _hide_input_in_validation_errors(
    req: Request, resp: Response | None, req_validation_error: ValidationError | None, _: Any
) -> None:
    """Spectree's 422 body echoes each field's submitted value, including passwords. Rebuild it
    with only the location, message and type of each error."""
    if req_validation_error is not None and resp is not None:
        errors = req_validation_error.errors(
            include_input=False, include_url=False, include_context=False
        )
        resp.set_data(json.dumps(errors))


# annotations=True: routes receive the validated body as a typed parameter (`json: XRequest`).
api_spec = SpecTree(
    "flask",
    title="Mini CMS API",
    version="0.1.0",
    path="api/docs",
    annotations=True,
    before=_hide_input_in_validation_errors,
)


@login_manager.unauthorized_handler
def unauthorized():
    """@login_required without a session: JSON 401 (an API never redirects to a login page)."""
    return jsonify(message="Unauthorized"), 401
