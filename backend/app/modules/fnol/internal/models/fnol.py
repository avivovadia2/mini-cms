from app.db_base import TimestampMixin
from app.extensions import db
from app.modules.fnol.schemas.fnol import FnolStatus


class Fnol(TimestampMixin, db.Model):
    __table_args__ = (
        # The FNOL list always filters by organization and usually by status. The index also
        # serves "all FNOLs of organization X", since it starts with organization_id.
        db.Index("ix_fnol_organization_id_status", "organization_id", "status"),
        # A rejection reason exactly when the FNOL is rejected: never a rejected FNOL without
        # one, never a leftover reason on another status.
        db.CheckConstraint(
            "(status = 'rejected') = (rejection_reason IS NOT NULL)",
            name="rejection_reason_iff_rejected",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)
    # Exactly what the reporter typed, kept even when it matches a policy (or doesn't).
    reported_policy_number = db.Column(db.String(255), nullable=False)
    # The matched policy of the same organization, or null. A foreign key by table name only:
    # no ORM relationship into the policies module, whose models are internal to it.
    policy_id = db.Column(db.Integer, db.ForeignKey("policy.id"), nullable=True)
    reporter_name = db.Column(db.String(255), nullable=False)
    reporter_email = db.Column(db.String(255), nullable=True)
    reporter_phone = db.Column(db.String(255), nullable=True)
    loss_date = db.Column(db.Date, nullable=False)
    loss_description = db.Column(db.Text, nullable=False)
    loss_state = db.Column(db.String(255), nullable=True)
    status = db.Column(
        db.Enum(*[status.value for status in FnolStatus], name="fnol_status"),
        nullable=False,
        server_default=FnolStatus.SUBMITTED.value,
    )
    rejection_reason = db.Column(db.Text, nullable=True)
    submitted_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
