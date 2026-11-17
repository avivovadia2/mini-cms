from werkzeug import security

from app.extensions import db
from app.modules.users.internal.exceptions import EmailAlreadyRegisteredError, UserNotFoundError
from app.modules.users.internal.models.user import User


def normalize_email(email: str) -> str:
    return email.strip().lower()


def create_user(*, organization_id: int, email: str, full_name: str, password: str) -> User:
    email = normalize_email(email)
    if db.session.scalar(db.select(User.id).where(User.email == email)) is not None:
        raise EmailAlreadyRegisteredError()

    user = User(
        organization_id=organization_id,
        email=email,
        full_name=full_name,
        password_hash=security.generate_password_hash(password),
    )
    db.session.add(user)
    db.session.flush()  # assigns the id and the server defaults, without committing
    return user


def list_users(organization_id: int, *, offset: int, limit: int) -> tuple[list[User], int]:
    """Two queries whatever the page size: one count, one page. User has no relationships, so
    reading the rows triggers no further queries (no N+1)."""
    in_organization = User.organization_id == organization_id
    total_count = db.session.scalar(
        db.select(db.func.count()).select_from(User).where(in_organization)
    )
    users = db.session.scalars(
        db.select(User).where(in_organization).order_by(User.id).offset(offset).limit(limit)
    ).all()
    return list(users), total_count


def get_organization_user(organization_id: int, user_id: int) -> User:
    # Filtering by both columns in one query: a user of another organization looks exactly like
    # a user that doesn't exist.
    user = db.session.scalar(
        db.select(User).where(User.id == user_id, User.organization_id == organization_id)
    )
    if user is None:
        raise UserNotFoundError()
    return user


def get_user(user_id: int) -> User | None:
    return db.session.get(User, user_id)


def check_credentials(email: str, password: str) -> User | None:
    user = db.session.scalar(db.select(User).where(User.email == normalize_email(email)))
    if user is None or not security.check_password_hash(user.password_hash, password):
        return None
    return user
