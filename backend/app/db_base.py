from app.extensions import db


class TimestampMixin:
    """created_at / updated_at, which every table has (spec §4).

    Set by Postgres (`now()`), so they come from one clock and are filled even for rows inserted
    outside the app. `updated_at` is refreshed on every SQLAlchemy update.
    """

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )
