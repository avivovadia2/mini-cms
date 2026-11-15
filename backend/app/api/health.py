from pydantic import BaseModel
from spectree import Response
from sqlalchemy import text

from app.api import api_bp
from app.extensions import api_spec, db


class HealthResponse(BaseModel):
    status: str
    database: str


@api_bp.get("/health")
@api_spec.validate(resp=Response(HTTP_200=HealthResponse, HTTP_503=HealthResponse), tags=["health"])
def health():
    """Liveness + database connectivity check."""
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        return HealthResponse(status="error", database="unreachable"), 503
    return HealthResponse(status="ok", database="ok")
