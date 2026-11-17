from app.db_base import TimestampMixin
from app.extensions import db


class Organization(TimestampMixin, db.Model):
    """A tenant. Every other business row belongs to exactly one organization."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
