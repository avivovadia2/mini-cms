from app.db_base import TimestampMixin
from app.extensions import db


class User(TimestampMixin, db.Model):
    __table_args__ = (
        # Emails are stored lower-case, so the unique constraint is effectively case-insensitive.
        # The service lower-cases before saving; this makes the database refuse anything else.
        db.CheckConstraint("email = lower(email)", name="email_lowercase"),
    )

    id = db.Column(db.Integer, primary_key=True)
    # Referenced by table name, not by importing Organization: the organizations module's models
    # are internal to it. Indexed for "list the users of an organization" (M1 2/4).
    organization_id = db.Column(
        db.Integer, db.ForeignKey("organization.id"), nullable=False, index=True
    )
    # Unique across all organizations: the email alone identifies who is logging in.
    email = db.Column(db.String(255), nullable=False, unique=True)
    full_name = db.Column(db.String(255), nullable=False)
    # Only the hash is ever stored; the plain password never reaches the database.
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.true())
