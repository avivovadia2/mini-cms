from flask_login import login_user

from app.modules.auth.interface import AuthServiceInterface
from app.modules.auth.internal.session_user import SessionUser
from app.modules.auth.schemas import MeResponse, RegisterRequest
from app.modules.organizations import OrganizationsServiceInterface
from app.modules.users import UsersServiceInterface


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
        return MeResponse(
            id=user.id, email=user.email, full_name=user.full_name, organization=organization
        )
