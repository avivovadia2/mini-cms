from flask_login import login_user, logout_user

from app.modules.auth.interface import AuthServiceInterface
from app.modules.auth.internal.exceptions import InvalidCredentialsError
from app.modules.auth.internal.session_user import SessionUser
from app.modules.auth.schemas import LoginRequest, MeResponse, RegisterRequest
from app.modules.organizations import OrganizationsServiceInterface
from app.modules.organizations.schemas import OrganizationInfo
from app.modules.users import UsersServiceInterface
from app.modules.users.schemas import UserInfo


class AuthService(AuthServiceInterface):
    # Injected by the registry from the type hints: auth depends on the other modules only
    # through their interfaces.
    def __init__(
        self,
        organizations: OrganizationsServiceInterface,
        users: UsersServiceInterface,
    ) -> None:
        self._organizations = organizations
        self._users = users

    def register(self, params: RegisterRequest) -> MeResponse:
        organization = self._organizations.create_organization(params.organization_name)
        user = self._users.create_user(
            organization_id=organization.id,
            email=params.email,
            full_name=params.full_name,
            password=params.password,
        )
        # Replaces any current session: a logged-in user who registers again is switched into
        # the new organization.
        login_user(SessionUser(user))
        return _me_response(user, organization)

    def login(self, params: LoginRequest) -> MeResponse:
        user = self._users.check_credentials(params.email, params.password)
        if user is None or not user.is_active:
            raise InvalidCredentialsError()
        login_user(SessionUser(user))
        return _me_response(user, self._organizations.get_organization(user.organization_id))

    def logout(self) -> None:
        logout_user()

    def get_me(self, user_id: int) -> MeResponse:
        user = self._users.get_user(user_id)
        if user is None:
            # The session's user was loaded at the start of this request, so this can't happen.
            raise RuntimeError(f"Logged-in user {user_id} not found")
        return _me_response(user, self._organizations.get_organization(user.organization_id))


def _me_response(user: UserInfo, organization: OrganizationInfo) -> MeResponse:
    return MeResponse(
        id=user.id, email=user.email, full_name=user.full_name, organization=organization
    )
