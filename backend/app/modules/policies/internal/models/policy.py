from app.db_base import TimestampMixin
from app.extensions import db
from app.modules.policies.schemas.policy import LineOfBusiness, PolicyStatus


class Policy(TimestampMixin, db.Model):
    __table_args__ = (
        # Unique per organization, ignoring case: "POL-1" and "pol-1" are the same policy, but two
        # organizations may each have one. A unique index on an expression (lower(...)) can't be a
        # plain UniqueConstraint, hence db.Index(..., unique=True) with an explicit name.
        db.Index(
            "uq_policy_organization_id_policy_number_lower",
            "organization_id",
            db.func.lower(db.text("policy_number")),
            unique=True,
        ),
        db.CheckConstraint("expiration_date > effective_date", name="expiration_after_effective"),
    )

    id = db.Column(db.Integer, primary_key=True)
    # No index=True: the unique index below starts with organization_id, and Postgres uses it for
    # "all policies of organization X" too.
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)
    # Stored as typed (trimmed); comparisons use lower(), see the index above.
    policy_number = db.Column(db.String(255), nullable=False)
    insured_name = db.Column(db.String(255), nullable=False)
    # Native Postgres enum types, named explicitly, built from the schemas' StrEnums.
    line_of_business = db.Column(
        db.Enum(*[lob.value for lob in LineOfBusiness], name="policy_line_of_business"),
        nullable=False,
    )
    effective_date = db.Column(db.Date, nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.Enum(*[status.value for status in PolicyStatus], name="policy_status"),
        nullable=False,
        server_default=PolicyStatus.ACTIVE.value,
    )
