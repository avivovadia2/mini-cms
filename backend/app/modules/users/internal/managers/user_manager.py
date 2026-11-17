from werkzeug import security

from app.extensions import db
from app.modules.users.internal.exceptions import EmailAlreadyRegisteredError
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


def get_user(user_id: int) -> User | None:
    return db.session.get(User, user_id)


def check_credentials(email: str, password: str) -> User | None:
    user = db.session.scalar(db.select(User).where(User.email == normalize_email(email)))
    if user is None or not security.check_password_hash(user.password_hash, password):
        return None
    return user
