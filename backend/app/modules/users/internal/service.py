from app.modules.users.interface import UsersServiceInterface
from app.modules.users.internal.managers import user_manager
from app.modules.users.schemas import UserInfo
from app.schemas import Page, PageParams


class UsersService(UsersServiceInterface):
    def create_user(
        self, *, organization_id: int, email: str, full_name: str, password: str
    ) -> UserInfo:
        user = user_manager.create_user(
            organization_id=organization_id, email=email, full_name=full_name, password=password
        )
        return UserInfo.model_validate(user)

    def list_users(self, organization_id: int, page: PageParams) -> Page[UserInfo]:
        users, total_count = user_manager.list_users(
            organization_id, offset=page.offset, limit=page.page_size
        )
        return Page[UserInfo](
            results=[UserInfo.model_validate(user) for user in users], total_count=total_count
        )

    def get_organization_user(self, organization_id: int, user_id: int) -> UserInfo:
        return UserInfo.model_validate(user_manager.get_organization_user(organization_id, user_id))

    def get_user(self, user_id: int) -> UserInfo | None:
        user = user_manager.get_user(user_id)
        return UserInfo.model_validate(user) if user is not None else None

    def check_credentials(self, email: str, password: str) -> UserInfo | None:
        user = user_manager.check_credentials(email, password)
        return UserInfo.model_validate(user) if user is not None else None
