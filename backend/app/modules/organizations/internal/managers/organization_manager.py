from app.extensions import db
from app.modules.organizations.internal.models.organization import Organization


def create_organization(name: str) -> Organization:
    organization = Organization(name=name)
    db.session.add(organization)
    db.session.flush()  # assigns the id, without committing
    return organization
